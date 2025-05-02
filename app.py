import os
import sys
import platform
import logging
import datetime
import flask
import threading
from flask import Flask, render_template, jsonify, request, session
from utils.auth import get_sql_connection_string
from utils.monitoring import setup_logging, QUERY_COUNTER
from utils.dbatools import run_dbatools
from chains.levy_calculator import create_levy_chain
from chains.neighborhood_trends import create_neighborhood_trend_chain
from utils.llm_providers import get_llm, available_providers
from langchain_community.utilities.sql_database import SQLDatabase
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from prometheus_client import start_http_server
import langchain  # for version info

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize flask-sqlalchemy extension
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Initialize database connections and chains
try:
    # Get connection string from utils/auth.py
    conn_str = get_sql_connection_string()
    
    # Initialize LangChain SQL Database
    langchain_db = SQLDatabase.from_uri(conn_str)
    
    # Create database tables based on models.py
    with app.app_context():
        import models
        db.create_all()
        logger.info("Database tables created successfully")
    
    # Initialize RAG functionality
    try:
        from utils.rag import create_rag_chain, run_rag_query
        qa_chain = run_rag_query
        logger.info("RAG functionality initialized successfully")
    except Exception as e:
        logger.warning(f"Vector store functionality is currently disabled: {str(e)}")
        qa_chain = None
    
    # Initialize Levy Calculator chain
    levy_chain = create_levy_chain()
    logger.info("Levy calculator chain initialized successfully")
    
    # Initialize Neighborhood Trends chain
    try:
        trends_chain = create_neighborhood_trend_chain(conn_str)
        logger.info("Neighborhood trends chain initialized successfully")
    except Exception as e:
        logger.error(f"Failed to create neighborhood trends chain: {str(e)}")
        logger.warning("Using fallback neighborhood trends chain")
        
        # Create simple template for trends analysis
        from langchain_core.prompts import ChatPromptTemplate
        
        # Get LLM using provider configuration
        trends_llm = get_llm()
        trends_template = """You are analyzing neighborhood property trends. 
        However, you currently do not have access to the actual data. 
        Please inform the user that the neighborhood trend analysis is currently unavailable 
        and suggest they try a general property query instead."""
        
        trends_prompt = ChatPromptTemplate.from_template(trends_template)
        
        # Create a simple chain that always returns the same message
        def trends_chain(inputs):
            result = trends_prompt | trends_llm
            response = result.invoke({})
            return {"answer": response.content}
            
        logger.info("Neighborhood trends fallback chain initialized successfully")
    
except Exception as e:
    logger.critical(f"Failed to initialize database connections: {str(e)}")
    langchain_db = None
    vs = None
    qa_chain = None
    levy_chain = None
    trends_chain = None

# Start Prometheus metrics server in a separate thread
def start_metrics_server():
    start_http_server(8001)
    logger.info("Prometheus metrics server started on port 8001")

threading.Thread(target=start_metrics_server, daemon=True).start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """
    Render the dashboard page with statistics from the database.
    """
    try:
        # Gather statistics for dashboard
        from models import QueryLog, Document, Property, Assessment, Sale, Neighborhood
        
        # Query counts
        total_queries = QueryLog.query.count()
        error_count = QueryLog.query.filter_by(status="error").count()
        
        # Query types
        query_types = {}
        for q_type in ["general", "rag", "levy", "trends", "dbatools"]:
            query_types[q_type] = QueryLog.query.filter_by(query_type=q_type).count()
            
        # Average response time
        avg_time = db.session.query(db.func.avg(QueryLog.response_time)).scalar() or 0
        
        # Document count
        document_count = Document.query.count()
        
        # Property counts
        property_count = Property.query.count()
        assessment_count = Assessment.query.count()
        sale_count = Sale.query.count()
        neighborhood_count = Neighborhood.query.count()
        
        # Recent errors
        recent_errors = QueryLog.query.filter_by(status="error").order_by(
            QueryLog.timestamp.desc()
        ).limit(5).all()
        
        errors = []
        for err in recent_errors:
            errors.append({
                "query": err.query_text[:100] + "..." if len(err.query_text) > 100 else err.query_text,
                "error": err.error_message[:100] + "..." if len(err.error_message) > 100 else err.error_message,
                "timestamp": err.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "type": err.query_type
            })
        
        # Get current LLM provider
        current_provider = os.getenv("LLM_PROVIDER", "openai")
        available_llms = ", ".join(available_providers())
        
        # Pass data to template
        dashboard_data = {
            "total_queries": total_queries,
            "error_count": error_count,
            "query_types": query_types,
            "avg_time": round(avg_time, 2),
            "document_count": document_count,
            "property_count": property_count,
            "assessment_count": assessment_count,
            "sale_count": sale_count,
            "neighborhood_count": neighborhood_count,
            "recent_errors": errors,
            "llm_provider": current_provider,
            "available_llms": available_llms
        }
        
        return render_template('dashboard.html', data=dashboard_data)
        
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        # If there's an error, still render the dashboard but without data
        return render_template('dashboard.html', data=None)

@app.route('/api/query', methods=['POST'])
def process_query():
    if not langchain_db:
        return jsonify({"error": "Database connection not initialized"}), 500
    
    data = request.get_json()
    query_text = data.get('query')
    query_type = data.get('type', 'general')
    
    if not query_text:
        return jsonify({"error": "No query provided"}), 400
    
    logger.info(f"Processing {query_type} query: {query_text}")
    QUERY_COUNTER.labels(query_type=query_type).inc()
    
    # Log the query for analytics
    from models import QueryLog
    query_log = QueryLog(
        query_text=query_text,
        query_type=query_type
    )
    
    start_time = None
    import time
    start_time = time.time()
    
    try:
        if query_type == 'levy':
            # Levy calculation query
            parcel_record = data.get('parcel_record', {})
            tax_rate = data.get('tax_rate', 0.0)
            exemptions = data.get('exemptions', [])
            
            result = levy_chain({
                "parcel_record": parcel_record,
                "tax_rate": tax_rate,
                "exemptions": exemptions
            })
            response_text = result["text"]
            return jsonify({"result": response_text})
        
        elif query_type == 'trends':
            # Neighborhood trends query
            result = trends_chain({"question": query_text})
            response_text = result["answer"]
            return jsonify({"result": response_text})
        
        elif query_type == 'dbatools':
            # dbatools query
            result = run_dbatools(query_text)
            response_text = result
            return jsonify({"result": response_text})
        
        elif query_type == 'rag':
            # RAG query
            if not qa_chain:
                return jsonify({"error": "Document retrieval system not initialized"}), 500
                
            chat_history = session.get('chat_history', [])
            result = qa_chain(
                question=query_text,
                chat_history=chat_history
            )
            
            # Update chat history
            response_text = result["answer"]
            chat_history.append((query_text, response_text))
            session['chat_history'] = chat_history
            
            return jsonify({"result": response_text})
        
        else:
            # General SQL query
            try:
                # Try using the SQL agent from pacs_agent.py
                from pacs_agent import agent
                result = agent.run(query_text)
                response_text = result
            except ImportError:
                # Fallback to direct SQL execution if agent is not available
                logger.warning("SQL agent not available, using direct SQL execution")
                result = langchain_db.run(query_text)
                response_text = result
                
            return jsonify({"result": response_text})
    
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing query: {error_message}")
        
        # Log the error
        if query_log:
            query_log.status = "error"
            query_log.error_message = error_message
            
        return jsonify({"error": error_message}), 500
        
    finally:
        # Calculate and record response time
        if start_time and query_log:
            end_time = time.time()
            query_log.response_time = end_time - start_time
            
            # Set status to success if not already set to error
            if not hasattr(query_log, 'status') or not query_log.status:
                query_log.status = "success"
                
            # Set response text if available
            if 'response_text' in locals():
                query_log.response_text = response_text
                
            # Save query log to database
            with app.app_context():
                db.session.add(query_log)
                try:
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error saving query log: {str(e)}")
                    db.session.rollback()

@app.route('/api/reset_chat', methods=['POST'])
def reset_chat():
    session['chat_history'] = []
    return jsonify({"status": "success"})

@app.route('/api/ingest_document', methods=['POST'])
def ingest_document():
    """API endpoint to ingest a document from a URL."""
    if not db:
        return jsonify({"error": "Database not initialized"}), 500
        
    data = request.get_json()
    url = data.get('url')
    title = data.get('title')
    doc_type = data.get('type', 'webpage')
    description = data.get('description')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    logger.info(f"Ingesting document from URL: {url}")
    
    try:
        # Process document from URL
        from utils.document_processor import process_document_from_url
        document = process_document_from_url(
            url=url,
            title=title,
            document_type=doc_type,
            description=description
        )
        
        if not document:
            return jsonify({"error": "Failed to process document"}), 500
            
        logger.info(f"Document ingested successfully: {document.title} (ID: {document.id})")
        return jsonify({
            "status": "success",
            "document_id": document.id,
            "title": document.title
        })
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error ingesting document: {error_message}")
        return jsonify({"error": error_message}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """API endpoint to list all ingested documents."""
    if not db:
        return jsonify({"error": "Database not initialized"}), 500
        
    try:
        from models import Document
        documents = Document.query.order_by(Document.updated_at.desc()).all()
        
        results = []
        for doc in documents:
            results.append({
                "id": doc.id,
                "title": doc.title,
                "type": doc.document_type,
                "published_date": doc.published_date.isoformat() if doc.published_date else None,
                "source_url": doc.source_url
            })
            
        return jsonify({"documents": results})
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error listing documents: {error_message}")
        return jsonify({"error": error_message}), 500

@app.route('/api/llm_providers', methods=['GET'])
def list_llm_providers():
    """API endpoint to list available LLM providers."""
    try:
        providers = available_providers()
        current = os.getenv("LLM_PROVIDER", "openai")
        
        return jsonify({
            "providers": providers,
            "current": current
        })
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error listing LLM providers: {error_message}")
        return jsonify({"error": error_message}), 500
        
@app.route('/api/status', methods=['GET'])
def system_status():
    """
    API endpoint to get the current system status.
    Returns information about available services and their status.
    """
    try:
        status = {
            "database": langchain_db is not None,
            "vector_store": qa_chain is not None and "vector_store" not in str(qa_chain),
            "ai_model": True,  # Always assume AI model is available
            "levy_calculator": levy_chain is not None,
            "trends_analyzer": trends_chain is not None and "fallback" not in str(trends_chain)
        }
        
        # Log status check
        logger.info(f"System status check: {status}")
        
        # Get component versions where available
        versions = {
            "python": platform.python_version(),
            "flask": flask.__version__,
            "langchain": langchain.__version__ if 'langchain' in sys.modules else "Not available"
        }
        
        # Get LLM provider info
        llm_info = {
            "provider": os.getenv("LLM_PROVIDER", "openai"),
            "available_providers": available_providers()
        }
        
        # Get document statistics
        doc_stats = {}
        try:
            from models import Document
            doc_count = Document.query.count()
            doc_stats["count"] = doc_count
            doc_stats["last_updated"] = Document.query.order_by(Document.updated_at.desc()).first().updated_at.isoformat() if doc_count > 0 else None
        except Exception as e:
            logger.warning(f"Could not get document statistics: {str(e)}")
            doc_stats["error"] = str(e)
        
        return jsonify({
            "status": status,
            "versions": versions,
            "llm": llm_info,
            "documents": doc_stats,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error getting system status: {error_message}")
        return jsonify({
            "error": error_message,
            "status": {
                "database": False,
                "vector_store": False,
                "ai_model": False,
                "levy_calculator": False,
                "trends_analyzer": False
            }
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

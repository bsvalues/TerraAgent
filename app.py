import os
import logging
from flask import Flask, render_template, jsonify, request, session
from utils.auth import get_sql_connection_string
from utils.monitoring import setup_logging, QUERY_COUNTER
from utils.dbatools import run_dbatools
from chains.levy_calculator import create_levy_chain
from chains.neighborhood_trends import create_neighborhood_trend_chain
from langchain_openai import OpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from prometheus_client import start_http_server
import threading

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
    
    # Vector store functionality is not available in this version
    logger.warning("Vector store functionality is currently disabled")
    vs = None
    qa_chain = None
    
    # Initialize Levy Calculator chain
    levy_chain = create_levy_chain()
    logger.info("Levy calculator chain initialized successfully")
    
    # Initialize Neighborhood Trends chain
    trends_chain = create_neighborhood_trend_chain(conn_str)
    logger.info("Neighborhood trends chain initialized successfully")
    
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
    return render_template('dashboard.html')

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
                return jsonify({"error": "Vector store not initialized"}), 500
                
            chat_history = session.get('chat_history', [])
            result = qa_chain({
                "question": query_text,
                "chat_history": chat_history
            })
            
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

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

# Initialize database connections and chains
try:
    # Get connection string with Windows Authentication
    conn_str = get_sql_connection_string()
    logger.info("Using Windows Authentication for database connection")
    
    # Initialize SQL Database
    db = SQLDatabase.from_uri(conn_str)
    
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
    db = None
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
    if not db:
        return jsonify({"error": "Database connection not initialized"}), 500
    
    data = request.get_json()
    query_text = data.get('query')
    query_type = data.get('type', 'general')
    
    if not query_text:
        return jsonify({"error": "No query provided"}), 400
    
    logger.info(f"Processing {query_type} query: {query_text}")
    QUERY_COUNTER.inc()
    
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
            return jsonify({"result": result["text"]})
        
        elif query_type == 'trends':
            # Neighborhood trends query
            result = trends_chain({"question": query_text})
            return jsonify({"result": result["answer"]})
        
        elif query_type == 'dbatools':
            # dbatools query
            result = run_dbatools(query_text)
            return jsonify({"result": result})
        
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
            chat_history.append((query_text, result["answer"]))
            session['chat_history'] = chat_history
            
            return jsonify({"result": result["answer"]})
        
        else:
            # General SQL query
            from pacs_agent import agent
            result = agent.run(query_text)
            return jsonify({"result": result})
    
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing query: {error_message}")
        return jsonify({"error": error_message}), 500

@app.route('/api/reset_chat', methods=['POST'])
def reset_chat():
    session['chat_history'] = []
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

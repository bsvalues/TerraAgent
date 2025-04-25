import os
import logging
from chainlit import on_message, on_chat_start
import chainlit as cl
from langchain_openai import OpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from utils.auth import get_sql_connection_string
from utils.monitoring import setup_logging, QUERY_COUNTER
from utils.dbatools import run_dbatools, DbatoolsTool
from chains.levy_calculator import create_levy_chain, LevyTool
from chains.neighborhood_trends import create_neighborhood_trend_chain, TrendsTool
from langchain_community.agents import initialize_agent
from langchain_community.agents.agent_types import AgentType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

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
    
    # Initialize LLM
    llm = OpenAI(temperature=0)
    
    # Initialize tools
    tools = [
        DbatoolsTool(),
        LevyTool(create_levy_chain()),
        TrendsTool(create_neighborhood_trend_chain(conn_str))
    ]
    
    # Create agent with tools
    agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True
    )
    
except Exception as e:
    logger.critical(f"Failed to initialize components: {str(e)}")
    agent = None
    qa_chain = None

# Store user chat history
user_chat_histories = {}

@on_chat_start
async def start():
    """Initialize the chat session"""
    # Send a welcome message
    await cl.Message(
        content="Welcome to PACS-Training Assistant! Ask me anything about CAMA data, levy calculations, or database information.",
    ).send()
    
    # Create a new chat history for this session
    user_chat_histories[cl.user_session.get("id")] = []
    
    # Inform about available tools
    tools_msg = """
    **Available specialized tools:**
    - **Database Analysis**: Ask questions about tables, data schemas, or run queries
    - **Levy Calculation**: Calculate tax levies for parcels
    - **Neighborhood Trends**: Analyze property value trends in specific areas
    """
    await cl.Message(content=tools_msg).send()
    
    if not agent or not qa_chain:
        await cl.Message(
            content="⚠️ Warning: Some components failed to initialize. Functionality may be limited.",
        ).send()

@on_message
async def handle(message: cl.Message):
    """Process incoming messages"""
    
    # Log the query
    logger.info(f"Processing query: {message.content}")
    QUERY_COUNTER.inc()
    
    # Send thinking message
    thinking = cl.Message(content="Thinking...", author="PACS Assistant")
    await thinking.send()
    
    try:
        # Get user session ID and chat history
        session_id = cl.user_session.get("id")
        chat_history = user_chat_histories.get(session_id, [])
        
        if "vector" in message.content.lower() or "document" in message.content.lower() or "report" in message.content.lower():
            # Use RAG for document-related queries
            if not qa_chain:
                await thinking.update(content="Sorry, the vector store is not available. I can't search through documents at the moment.")
                return
                
            result = qa_chain({
                "question": message.content,
                "chat_history": chat_history
            })
            
            # Update chat history
            chat_history.append((message.content, result["answer"]))
            user_chat_histories[session_id] = chat_history
            
            await thinking.update(content=result["answer"])
            
        else:
            # Use the agent for other queries
            if not agent:
                await thinking.update(content="Sorry, the AI agent is not available. Please check the logs for details.")
                return
                
            result = agent({"input": message.content, "chat_history": chat_history})
            
            # Update chat history
            chat_history.append((message.content, result["output"]))
            user_chat_histories[session_id] = chat_history
            
            await thinking.update(content=result["output"])
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing query: {error_message}")
        await thinking.update(content=f"Sorry, I encountered an error: {error_message}")

if __name__ == "__main__":
    # Chainlit starts automatically when this script is executed with `chainlit run`
    # You don't need to call any start() method here
    pass

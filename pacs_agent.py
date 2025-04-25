import os
import logging
from langchain_openai import OpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import SQLDatabaseChain
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from utils.auth import get_sql_connection_string
from utils.monitoring import QUERY_COUNTER
from dotenv import load_dotenv

load_dotenv()

# Get logger
logger = logging.getLogger("pacs_assistant")

# Build connection string using Windows Authentication
try:
    conn_str = get_sql_connection_string()
    logger.info("Using Windows Authentication for database connection")
except Exception as e:
    logger.error(f"Windows Authentication failed: {str(e)}")
    # Fallback to basic authentication if provided in environment
    if all(os.getenv(var) for var in ["PACS_DB_USER", "PACS_DB_PASS", "PACS_DB_HOST", "PACS_DB_NAME"]):
        conn_str = (
            f"mssql+pyodbc://{os.getenv('PACS_DB_USER')}:"
            f"{os.getenv('PACS_DB_PASS')}@"
            f"{os.getenv('PACS_DB_HOST')}/{os.getenv('PACS_DB_NAME')}?"
            "driver=ODBC+Driver+18+for+SQL+Server"
        )
        logger.warning("Falling back to basic authentication")
    else:
        logger.critical("Authentication failed and no fallback credentials available")
        raise Exception("Cannot connect to database: Authentication failed")

# Initialize LangChain SQLDatabase
try:
    db = SQLDatabase.from_uri(conn_str)
    logger.info("Database connection established")
except Exception as e:
    logger.critical(f"Failed to initialize database: {str(e)}")
    raise

# Initialize LLM
llm = OpenAI(temperature=0)

# Create an advanced SQL agent with toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Create the agent with a custom prompt
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    top_k=10,  # Return more examples to help with complex queries
)

def run_sql_query(query_text):
    """
    Run a natural language query against the PACS database.
    
    Args:
        query_text (str): Natural language query
        
    Returns:
        str: Result of the query
    """
    logger.info(f"Running SQL query: {query_text}")
    
    try:
        # Increment query counter for monitoring
        QUERY_COUNTER.inc()
        
        # Run the query through the agent
        result = agent.run(query_text)
        
        logger.info("Query executed successfully")
        return result
    
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error executing query: {error_message}")
        raise

if __name__ == "__main__":
    while True:
        query = input("\nAsk PACS-Training DB> ")
        if query.lower() in ("exit", "quit"):
            break
        try:
            result = run_sql_query(query)
            print("\n", result)
        except Exception as e:
            print(f"Error: {str(e)}")

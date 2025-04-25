import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Get logger
logger = logging.getLogger("pacs_assistant")

def get_sql_connection_string():
    """
    Get a SQL Server connection string using Windows Authentication.
    Falls back to basic authentication if Windows Auth fails.
    
    Returns:
        str: SQL connection string
    """
    # Try Windows Authentication first
    try:
        host = os.getenv('PACS_DB_HOST')
        db_name = os.getenv('PACS_DB_NAME')
        
        if not host or not db_name:
            raise ValueError("Database host or name not specified in environment variables")
        
        # Connection string with Windows Authentication
        conn_str = (
            f"mssql+pyodbc://{host}/{db_name}?"
            "driver=ODBC+Driver+18+for+SQL+Server;"
            "Trusted_Connection=yes;"
            "Authentication=ActiveDirectoryIntegrated"
        )
        
        # Test the connection (this will raise an exception if it fails)
        import pyodbc
        test_conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={host};"
            f"DATABASE={db_name};"
            f"Trusted_Connection=yes;"
            f"Authentication=ActiveDirectoryIntegrated"
        )
        test_conn.close()
        
        logger.info("Windows Authentication successful")
        return conn_str
        
    except Exception as e:
        logger.warning(f"Windows Authentication failed: {str(e)}")
        
        # Fall back to basic authentication if provided
        user = os.getenv('PACS_DB_USER')
        password = os.getenv('PACS_DB_PASS')
        
        if user and password and host and db_name:
            logger.warning("Falling back to basic authentication")
            return (
                f"mssql+pyodbc://{user}:{password}@{host}/{db_name}?"
                "driver=ODBC+Driver+18+for+SQL+Server"
            )
        else:
            logger.error("Cannot create connection string: Missing credentials")
            raise ValueError("Database authentication failed and no fallback credentials available")

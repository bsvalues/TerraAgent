"""
Ollama LLM Provider for TerraAgent.
This module handles Ollama LLM configurations.
"""

import os
import logging

# Get logger
logger = logging.getLogger("pacs_assistant")

def get_ollama_llm(model="llama3", base_url="http://localhost:11434", temperature=0, **kwargs):
    """
    Get an Ollama LLM instance.
    
    Args:
        model (str): The model name to use
        base_url (str): The Ollama API base URL
        temperature (float): The sampling temperature
        **kwargs: Additional parameters to pass to the model
        
    Returns:
        LLM: A configured Ollama model instance
    """
    # Use base_url from args, then env var, or default
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        # Import here to avoid requiring the package if not used
        try:
            from langchain_community.llms import Ollama
            from langchain_community.chat_models import ChatOllama
        except ImportError:
            logger.error("langchain_community is not installed. Please install it to use Ollama models.")
            raise ImportError("Please install langchain_community using pip install langchain_community")
        
        logger.info(f"Initializing ChatOllama with model {model}")
        
        # Check if we want a chat model (default) or completion model
        if kwargs.pop("chat_model", True):
            return ChatOllama(
                model=model,
                base_url=base_url,
                temperature=temperature,
                **kwargs
            )
        else:
            return Ollama(
                model=model,
                base_url=base_url,
                temperature=temperature,
                **kwargs
            )
    except Exception as e:
        logger.error(f"Error initializing Ollama model: {str(e)}")
        raise
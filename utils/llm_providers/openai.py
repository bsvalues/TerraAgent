"""
OpenAI LLM Provider for TerraAgent.
This module handles OpenAI LLM configurations.
"""

import os
import logging
from langchain_openai import ChatOpenAI, OpenAI

# Get logger
logger = logging.getLogger("pacs_assistant")

def get_openai_llm(model="gpt-4o", api_key=None, temperature=0, chat_model=True, **kwargs):
    """
    Get an OpenAI LLM instance.
    
    Args:
        model (str): The model name to use
        api_key (str, optional): The OpenAI API key
        temperature (float): The sampling temperature
        chat_model (bool): Whether to use ChatOpenAI or OpenAI
        **kwargs: Additional parameters to pass to the model
        
    Returns:
        LLM: A configured OpenAI model instance
    """
    # Use API key from args, then env var, then fail
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        logger.error("OpenAI API key not found in environment variables or passed to function")
        raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
    
    try:
        if chat_model:
            logger.info(f"Initializing ChatOpenAI with model {model}")
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                temperature=temperature,
                **kwargs
            )
        else:
            logger.info(f"Initializing OpenAI with model {model}")
            return OpenAI(
                model=model,
                api_key=api_key,
                temperature=temperature,
                **kwargs
            )
    except Exception as e:
        logger.error(f"Error initializing OpenAI model: {str(e)}")
        raise
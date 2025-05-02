"""
Anthropic LLM Provider for TerraAgent.
This module handles Anthropic LLM configurations.
"""

import os
import logging
from langchain.chains.base import Chain
from typing import Dict, Any, List, Optional

# Get logger
logger = logging.getLogger("pacs_assistant")

def get_anthropic_llm(model="claude-3-opus-20240229", api_key=None, temperature=0, **kwargs):
    """
    Get an Anthropic LLM instance.
    
    Args:
        model (str): The model name to use
        api_key (str, optional): The Anthropic API key
        temperature (float): The sampling temperature
        **kwargs: Additional parameters to pass to the model
        
    Returns:
        LLM: A configured Anthropic model instance
    """
    # Use API key from args, then env var, then fail
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        logger.error("Anthropic API key not found in environment variables or passed to function")
        raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
    
    try:
        # Import here to avoid requiring the package if not used
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            logger.error("langchain_anthropic not installed. Please install it to use Anthropic models.")
            raise ImportError("Please install langchain_anthropic using pip install langchain_anthropic")
        
        logger.info(f"Initializing ChatAnthropic with model {model}")
        return ChatAnthropic(
            model=model,
            anthropic_api_key=api_key,
            temperature=temperature,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Error initializing Anthropic model: {str(e)}")
        raise
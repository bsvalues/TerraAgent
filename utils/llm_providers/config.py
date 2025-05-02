"""
LLM Configuration Module for TerraAgent.
This module provides functions to select and configure LLM providers.
"""

import os
import logging
from typing import Dict, Any, Optional, Callable
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get logger
logger = logging.getLogger("pacs_assistant")

# Default provider is OpenAI
DEFAULT_PROVIDER = "openai"

# Provider configuration with default values
_provider_config = {
    "provider": os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER),
    "openai": {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0"))
    },
    "azure_openai": {
        "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", ""),
        "model": os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
        "api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
        "temperature": float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0"))
    },
    "anthropic": {
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "temperature": float(os.getenv("ANTHROPIC_TEMPERATURE", "0"))
    },
    "ollama": {
        "model": os.getenv("OLLAMA_MODEL", "llama3"),
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0"))
    }
}

def available_providers() -> list:
    """
    Get a list of available LLM providers.
    
    Returns:
        list: Available providers
    """
    return ["openai", "azure_openai", "anthropic", "ollama"]

def update_provider_config(provider: str = None, **kwargs) -> None:
    """
    Update the LLM provider configuration.
    
    Args:
        provider (str, optional): The provider to update
        **kwargs: Configuration parameters to update
    """
    global _provider_config
    
    if provider:
        _provider_config["provider"] = provider
        
    if provider in _provider_config and kwargs:
        for key, value in kwargs.items():
            if key in _provider_config[provider]:
                _provider_config[provider][key] = value
                
    logger.info(f"Updated LLM provider configuration: {provider}")

def get_llm(provider: str = None, **kwargs):
    """
    Get a configured LLM instance based on provider.
    
    Args:
        provider (str, optional): The provider to use. If None, uses the configured provider.
        **kwargs: Additional configuration parameters
        
    Returns:
        LLM: A configured LLM instance
    """
    if not provider:
        provider = _provider_config["provider"]
    
    # Import provider-specific functions
    if provider == "openai":
        from .openai import get_openai_llm
        return get_openai_llm(**{**_provider_config["openai"], **kwargs})
        
    elif provider == "azure_openai":
        from .azure_openai import get_azure_openai_llm
        return get_azure_openai_llm(**{**_provider_config["azure_openai"], **kwargs})
        
    elif provider == "anthropic":
        from .anthropic import get_anthropic_llm
        return get_anthropic_llm(**{**_provider_config["anthropic"], **kwargs})
        
    elif provider == "ollama":
        from .ollama import get_ollama_llm
        return get_ollama_llm(**{**_provider_config["ollama"], **kwargs})
        
    else:
        logger.warning(f"Unknown provider: {provider}. Using OpenAI as default.")
        from .openai import get_openai_llm
        return get_openai_llm(**{**_provider_config["openai"], **kwargs})

def get_provider_config(provider: str = None) -> Dict[str, Any]:
    """
    Get the configuration for a provider.
    
    Args:
        provider (str, optional): The provider to get configuration for.
            If None, returns the current provider's configuration.
            
    Returns:
        Dict[str, Any]: The provider configuration
    """
    if not provider:
        provider = _provider_config["provider"]
        
    return _provider_config.get(provider, {})
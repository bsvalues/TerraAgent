"""
Azure OpenAI LLM Provider for TerraAgent.
This module handles Azure OpenAI LLM configurations.
"""

import os
import logging
from langchain_openai import AzureChatOpenAI, AzureOpenAI

# Get logger
logger = logging.getLogger("pacs_assistant")

def get_azure_openai_llm(
    deployment_name=None,
    model=None,
    api_key=None,
    endpoint=None,
    api_version="2023-05-15",
    temperature=0,
    chat_model=True,
    **kwargs
):
    """
    Get an Azure OpenAI LLM instance.
    
    Args:
        deployment_name (str): The deployment name in Azure
        model (str): The model name (not usually needed with deployment_name)
        api_key (str, optional): The Azure OpenAI API key
        endpoint (str, optional): The Azure OpenAI endpoint
        api_version (str): The API version to use
        temperature (float): The sampling temperature
        chat_model (bool): Whether to use AzureChatOpenAI or AzureOpenAI
        **kwargs: Additional parameters to pass to the model
        
    Returns:
        LLM: A configured Azure OpenAI model instance
    """
    # Use values from args, then env vars, then fail
    deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
    
    # Check required parameters
    if not deployment_name:
        logger.error("Azure OpenAI deployment name not provided")
        raise ValueError("Deployment name is required for Azure OpenAI")
        
    if not api_key:
        logger.error("Azure OpenAI API key not found in environment variables or passed to function")
        raise ValueError("API key is required for Azure OpenAI")
        
    if not endpoint:
        logger.error("Azure OpenAI endpoint not found in environment variables or passed to function")
        raise ValueError("Endpoint is required for Azure OpenAI")
    
    try:
        # Apply Azure best practices for retries and error handling
        retry_options = {
            "max_retries": 5,
            "backoff_factor": 2
        }
        
        # Update retry options from kwargs if provided
        retry_options.update({k: v for k, v in kwargs.items() if k in retry_options})
        
        # Remove retry options from kwargs to avoid duplicates
        for k in retry_options:
            if k in kwargs:
                del kwargs[k]
                
        if chat_model:
            logger.info(f"Initializing AzureChatOpenAI with deployment {deployment_name}")
            return AzureChatOpenAI(
                deployment_name=deployment_name,
                openai_api_key=api_key,
                azure_endpoint=endpoint,
                openai_api_version=api_version,
                temperature=temperature,
                **retry_options,
                **kwargs
            )
        else:
            logger.info(f"Initializing AzureOpenAI with deployment {deployment_name}")
            return AzureOpenAI(
                deployment_name=deployment_name,
                openai_api_key=api_key,
                azure_endpoint=endpoint,
                openai_api_version=api_version,
                temperature=temperature,
                **retry_options,
                **kwargs
            )
    except Exception as e:
        logger.error(f"Error initializing Azure OpenAI model: {str(e)}")
        raise
"""
LLM configuration module for Azure OpenAI.
"""
import os
from langchain_openai import AzureChatOpenAI
from typing import Optional


def get_azure_llm(
    model: str = "gpt-4",
    temperature: float = 0,
    deployment_name: Optional[str] = None
) -> AzureChatOpenAI:
    """
    Create an Azure OpenAI LLM instance.
    
    Args:
        model: The model name (e.g., "gpt-4", "gpt-35-turbo")
        temperature: The temperature for the model
        deployment_name: Optional deployment name. If not provided, will use model name.
        
    Returns:
        AzureChatOpenAI instance
        
    Raises:
        ValueError: If required environment variables are not set
    """
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
    
    # Use deployment name from env or default to model name
    if not deployment_name:
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", model)
    
    return AzureChatOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
        azure_deployment=deployment_name,
        temperature=temperature,
    )


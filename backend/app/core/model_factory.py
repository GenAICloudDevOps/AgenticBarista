"""
Model Factory for Multi-LLM Support
Supports: AWS Bedrock, Google Gemini, Mistral AI
"""
import os
from typing import Any

def get_model(provider: str = "bedrock", model_name: str = None) -> Any:
    """
    Factory function to create LLM model instances
    
    Args:
        provider: Model provider (bedrock, gemini, mistral)
        model_name: Specific model name/ID
    
    Returns:
        LangChain chat model instance
    """
    
    if provider == "bedrock":
        from langchain_aws import ChatBedrockConverse
        
        # Default Bedrock models
        if not model_name:
            model_name = "amazon.nova-lite-v1:0"
        
        return ChatBedrockConverse(
            model=model_name,
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            temperature=0.7
        )
    
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Default Gemini model
        if not model_name:
            model_name = "gemini-2.5-flash-lite"
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7
        )
    
    elif provider == "mistral":
        from langchain_mistralai import ChatMistralAI
        
        # Default Mistral model
        if not model_name:
            model_name = "magistral-small-250925"
        
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        
        return ChatMistralAI(
            model=model_name,
            mistral_api_key=api_key,
            temperature=0.7
        )
    
    else:
        # Fallback to Bedrock
        from langchain_aws import ChatBedrockConverse
        return ChatBedrockConverse(
            model="amazon.nova-lite-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            temperature=0.7
        )


# Available models configuration
AVAILABLE_MODELS = {
    "bedrock": [
        {
            "id": "amazon.nova-lite-v1:0",
            "name": "Nova Lite",
            "description": "Fast and efficient"
        },
        {
            "id": "amazon.nova-pro-v1:0",
            "name": "Nova Pro",
            "description": "Balanced performance"
        },
        {
            "id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "name": "Claude 3.5 Sonnet",
            "description": "Highest quality reasoning"
        },
        {
            "id": "anthropic.claude-3-haiku-20240307-v1:0",
            "name": "Claude 3 Haiku",
            "description": "Fast and efficient"
        }
    ],
    "gemini": [
        {
            "id": "gemini-2.5-flash-lite",
            "name": "Gemini 2.5 Flash-Lite",
            "description": "Lightweight and fast"
        },
        {
            "id": "gemini-2.5-flash",
            "name": "Gemini 2.5 Flash",
            "description": "Fast and capable"
        },
        {
            "id": "gemini-2.5-pro",
            "name": "Gemini 2.5 Pro",
            "description": "High quality responses"
        }
    ],
    "mistral": [
        {
            "id": "magistral-small-250925",
            "name": "Magistral Small 1.2",
            "description": "Latest reasoning model with vision support (Sep 2025)"
        },
        {
            "id": "mistral-small-250625",
            "name": "Mistral Small 3.2",
            "description": "Updated small model (Jun 2025)"
        }
    ]
}


def get_available_models():
    """Return list of all available models"""
    return AVAILABLE_MODELS


def get_model_info(provider: str, model_id: str):
    """Get information about a specific model"""
    if provider in AVAILABLE_MODELS:
        for model in AVAILABLE_MODELS[provider]:
            if model["id"] == model_id:
                return model
    return None

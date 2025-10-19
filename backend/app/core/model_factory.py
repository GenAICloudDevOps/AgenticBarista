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
            model_name = "gemini-1.5-flash"
        
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
            model_name = "mistral-small-latest"
        
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
            "description": "Fast and cost-effective",
            "cost_per_1m": 0.30
        },
        {
            "id": "amazon.nova-pro-v1:0",
            "name": "Nova Pro",
            "description": "Balanced performance",
            "cost_per_1m": 0.80
        },
        {
            "id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "name": "Claude 3.5 Sonnet",
            "description": "Highest quality reasoning",
            "cost_per_1m": 3.00
        },
        {
            "id": "anthropic.claude-3-haiku-20240307-v1:0",
            "name": "Claude 3 Haiku",
            "description": "Fast and efficient",
            "cost_per_1m": 0.25
        }
    ],
    "gemini": [
        {
            "id": "gemini-1.5-flash",
            "name": "Gemini 1.5 Flash",
            "description": "Very fast and cheap",
            "cost_per_1m": 0.075
        },
        {
            "id": "gemini-1.5-pro",
            "name": "Gemini 1.5 Pro",
            "description": "High quality responses",
            "cost_per_1m": 1.25
        },
        {
            "id": "gemini-2.0-flash-exp",
            "name": "Gemini 2.0 Flash (Experimental)",
            "description": "Latest experimental model",
            "cost_per_1m": 0.075
        }
    ],
    "mistral": [
        {
            "id": "mistral-small-latest",
            "name": "Mistral Small",
            "description": "Fast and affordable",
            "cost_per_1m": 0.20
        },
        {
            "id": "mistral-medium-latest",
            "name": "Mistral Medium",
            "description": "Balanced performance",
            "cost_per_1m": 2.70
        },
        {
            "id": "mistral-large-latest",
            "name": "Mistral Large",
            "description": "Most capable model",
            "cost_per_1m": 8.00
        },
        {
            "id": "open-mistral-7b",
            "name": "Open Mistral 7B",
            "description": "Open source, cheapest",
            "cost_per_1m": 0.10
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

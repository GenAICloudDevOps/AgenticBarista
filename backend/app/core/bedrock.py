import boto3
import json
import os

def get_bedrock_client():
    return boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

def get_haiku_response(prompt: str) -> str:
    """Get response from Amazon Nova Lite model"""
    try:
        client = get_bedrock_client()
        
        body = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1000,
                "temperature": 0.7
            }
        })
        
        response = client.invoke_model(
            modelId="amazon.nova-lite-v1:0",
            body=body,
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['output']['message']['content'][0]['text']
        
    except Exception as e:
        return f"I'm having trouble connecting to the AI service. Error: {str(e)}"

from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
import os
from functools import cache
from dotenv import load_dotenv
load_dotenv()
from botocore.config import Config

bedrock_config = Config(
        retries={
            "max_attempts": 10,
            "mode": "adaptive"  
        }
    )

@cache
def getLLM() -> BaseChatModel:

    return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="openai/gpt-oss-120b"
        ) 
       

    """return ChatBedrockConverse(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name="us-east-1",  
            model="us.amazon.nova-lite-v1:0",
            config=bedrock_config,
            max_tokens=1000
        )"""


def getGROQLLM() -> BaseChatModel:
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="openai/gpt-oss-120b"
    ) 
        

from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import BaseChatModel
import os
from functools import cache
from botocore.config import Config
from dotenv import load_dotenv
load_dotenv()


bedrock_config = Config(
        retries={
            "max_attempts": 10,
            "mode": "adaptive"  
        }
    )

@cache
def getLLM() -> BaseChatModel:


    return ChatBedrockConverse(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name="us-east-1",  
            model="us.amazon.nova-2-lite-v1:0",
            config=bedrock_config
        )

from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import BaseChatModel
import os
from functools import cache
from dotenv import load_dotenv
load_dotenv()

@cache
def getLLM() -> BaseChatModel:
    return  ChatBedrockConverse(aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), region_name="us-east-2", model="us.anthropic.claude-haiku-4-5-20251001-v1:0")

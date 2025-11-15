import os

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama

load_dotenv()


def load_default_model(model: str = "gpt-oss:20b") -> BaseChatModel:
    llm = ChatOllama(
        model=model,
        temperature=0,
        validate_model_on_init=True,
        base_url=os.getenv("OLLAMA_API_URL"),
    )
    return llm

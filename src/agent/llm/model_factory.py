import os

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()


def load_model(backend_model: str = "gpt-oss:20b") -> BaseChatModel:
    if backend_model in ["gpt-oss:20b", "qwen3:32b"]:
        llm = ChatOllama(
            model=backend_model,
            temperature=0,
            validate_model_on_init=True,
            base_url=os.getenv("OLLAMA_API_URL"),
        )
    elif backend_model in ["gpt-5-mini"]:
        llm = ChatOpenAI(
            model_name=backend_model,
        )
    else:
        raise ValueError(f"Unsupported backend model: {backend_model}")
    return llm

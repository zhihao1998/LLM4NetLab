import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()


def OllamaLLM(model: str = "gpt-oss:20b") -> ChatOllama:
    llm = ChatOllama(
        model=model,
        temperature=0,
        base_url=os.getenv("OLLAMA_API_URL"),
    )
    return llm

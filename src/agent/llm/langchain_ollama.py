import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()


def OllamaLLM(model: str = "gpt-oss:20b", callbacks=[]) -> ChatOllama:
    llm = ChatOllama(
        model=model,
        temperature=0,
        validate_model_on_init=True,
        base_url=os.getenv("OLLAMA_API_URL"),
        callbacks=callbacks,
    )
    return llm

import os

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

load_dotenv()


class DeepSeekLLM:
    def __init__(self):
        self.llm = ChatDeepSeek(
            model="deepseek-reasoner",
            temperature=0,
            base_url=os.getenv("DEEPSEEK_API_URL"),
        )

    def invoke(self, prompt: str):
        response = self.llm.invoke(prompt)
        return response

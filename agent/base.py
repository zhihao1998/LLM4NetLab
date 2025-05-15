from typing import List

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

from agent import configs


class Character(BaseModel):
    name: str
    age: int
    fact: List[str] = Field(..., description="A list of facts about the character")


# enables `response_model` in create call
client = instructor.from_openai(
    OpenAI(
        base_url=configs.LLM_API_URL,
        api_key="ollama",  # required, but unused
    ),
    mode=instructor.Mode.JSON,
)

resp = client.chat.completions.create(
    model="deepseek-r1:1.5b",
    messages=[
        {
            "role": "user",
            "content": "Tell me about the Harry Potter",
        }
    ],
    response_model=Character,
)
print(resp.model_dump_json(indent=2))

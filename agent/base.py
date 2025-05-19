from typing import List

import instructor
import llm_config
from openai import OpenAI
from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str
    age: int
    fact: List[str] = Field(..., description="A list of facts about the character")


# enables `response_model` in create call
client = instructor.from_openai(
    OpenAI(
        base_url=llm_config.LLM_API_URL,
        api_key="ollama",  # required, but unused
    ),
    mode=instructor.Mode.JSON,
)

resp = client.chat.completions.create(
    model="deepseek-r1:1.5b",
    messages=[
        {
            "role": "user",
            "content": "how old is Joh biden?",
        }
    ],
    response_model=Character,
)
print(resp.model_dump_json(indent=2))

"""An common abstraction for a cached LLM inference setup.
Reproduce from AIOpsLab repo.
Currently supports localized DeepSeek-R1."""

import json
import os
from pathlib import Path

from openai import OpenAI

from config import OPENAI_LLM_KEY, OPENAI_LLM_MODEL, OPENAI_LLM_URL

CACHE_DIR = Path("./cache_dir")
CACHE_PATH = CACHE_DIR / "cache.json"


class Cache:
    """A simple cache implementation to store the results of the LLM inference."""

    def __init__(self) -> None:
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH) as f:
                self.cache_dict = json.load(f)
        else:
            os.makedirs(CACHE_DIR, exist_ok=True)
            self.cache_dict = {}

    @staticmethod
    def process_payload(payload):
        if isinstance(payload, (list, dict)):
            return json.dumps(payload)
        return payload

    def get_from_cache(self, payload):
        payload_cache = self.process_payload(payload)
        if payload_cache in self.cache_dict:
            return self.cache_dict[payload_cache]
        return None

    def add_to_cache(self, payload, output):
        payload_cache = self.process_payload(payload)
        self.cache_dict[payload_cache] = output

    def save_cache(self):
        with open(CACHE_PATH, "w") as f:
            json.dump(self.cache_dict, f, indent=4)


class LLMBase:
    """Universal base class for OpenAI-compatible LLMs."""

    def __init__(self):
        self.cache = Cache()

    def inference(self, payload: list[dict[str, str]]) -> list[str]:
        if self.cache is not None:
            cache_result = self.cache.get_from_cache(payload)
            if cache_result is not None:
                return cache_result

        client = OpenAI(base_url=OPENAI_LLM_URL, api_key=OPENAI_LLM_KEY)
        try:
            response = client.chat.completions.create(
                messages=payload,
                model=OPENAI_LLM_MODEL,
                stream=False,
                stop=[],
            )
        except Exception as e:
            print(f"Exception: {repr(e)}")
            raise e

        return [c.message.content for c in response.choices]

    def run(self, payload: list[dict[str, str]]) -> list[str]:
        response = self.inference(payload)
        if self.cache is not None:
            self.cache.add_to_cache(payload, response)
            self.cache.save_cache()
        return response


if __name__ == "__main__":
    client = LLMBase()
    resp = client.inference(
        [
            {
                "role": "user",
                "content": "how old is Joh biden?",
            }
        ]
    )
    print(resp[0])

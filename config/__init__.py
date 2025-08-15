import os

import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.join(BASE_DIR, "llm4netlab")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

with open(CONFIG_PATH, "r") as f:
    _cfg = yaml.safe_load(f)

USE_LOCAL = _cfg.get("use_local", False)
LLM_TYPE = _cfg.get("use_llm", "deepseek")
USE_LANGFUSE = _cfg.get("use_langfuse", False)

if LLM_TYPE == "deepseek":
    # ===== DeepSeek =====
    deepseek = _cfg.get("deepseek")
    if USE_LOCAL:
        OPENAI_LLM_URL = deepseek["local"]["url"]
        OPENAI_LLM_MODEL = deepseek["local"]["model"]
        OPENAI_LLM_KEY = deepseek["local"].get("key", "")
    else:
        OPENAI_LLM_URL = deepseek["remote"]["url"]
        OPENAI_LLM_MODEL = deepseek["remote"]["model"]
        OPENAI_LLM_KEY = deepseek["remote"].get("key", "")
elif LLM_TYPE == "qwen3":
    # ===== Qwen3 =====
    qwen3 = _cfg.get("qwen3")
    if USE_LOCAL:
        OPENAI_LLM_URL = qwen3["local"]["url"]
        OPENAI_LLM_MODEL = qwen3["local"]["model"]
        QOPENAI_LLM_KEY = qwen3["local"].get("key", "")
    else:
        OPENAI_LLM_URL = qwen3["remote"]["url"]
        OPENAI_LLM_MODEL = qwen3["remote"]["model"]
        OPENAI_LLM_KEY = qwen3["remote"].get("key", "")


class RuntimeConfig:
    """Runtime configuration for the application."""

    langfuse_trace_id = None  # TODO: not good place for sharing this, but it works for now
    root_span_id = None


if __name__ == "__main__":
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"RESULTS_DIR: {RESULTS_DIR}")
    print(f"OPENAI_LLM_URL: {OPENAI_LLM_URL}")
    print(f"OPENAI_LLM_MODEL: {OPENAI_LLM_MODEL}")

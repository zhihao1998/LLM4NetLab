import json
import logging
import os
import traceback
from datetime import datetime
from typing import Any

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.outputs.generation import Generation

from llm4netlab.config import BASE_DIR


class FileLoggerHandler(BaseCallbackHandler):
    def __init__(self, name=None):
        super().__init__()
        self.logger = logging.getLogger("LLMAgentLogger")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)

        # read session info from file
        with open(f"{BASE_DIR}/runtime/current_session.json", "r") as f:
            session_info = json.load(f)

        log_path = os.path.join(
            BASE_DIR,
            "results",
            session_info["root_cause_name"],
            session_info["session_id"],
            f"conversation_{name}.log",
        )
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # new loggers
        file_handler = logging.FileHandler(log_path, encoding="utf-8", mode="a")
        formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _log(self, event_type: str, payload: dict):
        log_entry = {"timestamp": datetime.now(), "event": event_type, **payload}
        self.logger.info(json.dumps(log_entry, ensure_ascii=False, default=str))

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        **kwargs,
    ) -> None:
        self._log(
            "llm_start",
            {
                "messages": messages[0][-1],
                "model": serialized,
            },
        )

    def on_llm_end(self, response, **kwargs):
        payload = {}
        try:
            res: Generation = response.generations[0][0]
            if res:
                text = getattr(res, "text", None)
                if text:
                    payload["text"] = res.text
                generation_info = getattr(res, "generation_info", None)
                if generation_info:
                    payload["generation_info"] = res.generation_info
                message = getattr(res, "message", None)
                if message:
                    payload["invalid_tool_calls"] = getattr(message, "invalid_tool_calls", None)
                    payload["usage_metadata"] = getattr(message, "usage_metadata", None)
                self._log("llm_end", payload)
        except Exception as e:
            self._log(
                "llm_end_error",
                {"error": str(e), "traceback": traceback.format_exc(), "response": str(response)},
            )

    def on_tool_start(self, serialized, input_str, **kwargs):
        self._log(
            "tool_start",
            {
                "tool": serialized,
                "input": input_str,
            },
        )

    def on_tool_end(self, output: ToolMessage, **kwargs):
        if output.status == "error":
            self._log(
                "tool_error",
                {
                    "output": output,
                },
            )
            return

        self._log(
            "tool_end",
            {
                "output": output,
                "output_type": type(output).__name__,
            },
        )

    def on_tool_error(self, error, **kwargs):
        self._log(
            "tool_error",
            {
                "error": str(error),
            },
        )

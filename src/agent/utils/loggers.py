import json
import logging
import traceback
from datetime import datetime

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs.generation import Generation


class FileLoggerHandler(BaseCallbackHandler):
    def __init__(self, log_path):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_path, encoding="utf-8", mode="a")

            formatter = logging.Formatter("%(message)s")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _log(self, event_type: str, payload: dict):
        log_entry = {"timestamp": datetime.now(), "event": event_type, **payload}
        self.logger.info(json.dumps(log_entry, ensure_ascii=False, default=str))

    def on_llm_start(self, serialized, prompts, **kwargs):
        self._log(
            "llm_start",
            {
                "prompts": prompts,
                "metadata": serialized,
            },
        )

    def on_llm_end(self, response, **kwargs):
        payload = {}
        try:
            res: Generation = response.generations[0][0]
            if res:
                # TODO: Now only works for ollama_langchain, to adapt to other LLMs
                text = getattr(res, "text", None)
                if text:
                    payload["text"] = res.text
                generation_info = getattr(res, "generation_info", None)
                if generation_info:
                    payload["generation_info"] = res.generation_info
                message = getattr(res, "message", None)
                if message:
                    # TODO: Check the tool call formats
                    # tool_calls = getattr(message, "tool_call_chunks", []) or []
                    # if tool_calls:
                    #     for tool_call in tool_calls:
                    #         payload["tool_calls"] = {
                    #             "tool_name": getattr(tool_call, "tool_name", None),
                    #             "tool_input": getattr(tool_call, "tool_input", None),
                    #         }

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

    def on_tool_end(self, output, **kwargs):
        self._log(
            "tool_end",
            {
                "output": output,
            },
        )

    def on_tool_error(self, error, **kwargs):
        self._log(
            "tool_error",
            {
                "error": str(error),
            },
        )

import logging

from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs.generation import Generation


class FileLoggerHandler(BaseCallbackHandler):
    def __init__(self, log_path):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.logger.info(f"LLM started: prompts: {prompts}, metadata: {serialized}.")

    def on_llm_end(self, response, **kwargs):
        res: Generation = response.generations[0][0]
        output_text = "LLM ended: "
        if getattr(res, "text", None):
            output_text += f"text: {res.text}. "
        if getattr(res, "generation_info", None):
            output_text += f"generation_info: {res.generation_info}. "
        if getattr(res, "message", None):
            output_text += f"message: {res.message}. "

        self.logger.info(output_text)

    def on_tool_start(self, serialized, input_str, **kwargs):
        self.logger.info(f"Tool started: {serialized}, input: {input_str}.")

    def on_tool_end(self, output, **kwargs):
        self.logger.info(f"Tool ended: tool_output: {output}.")

    def on_tool_error(self, error, **kwargs):
        self.logger.error(f"Tool error: {error}.")

import logging

from langchain.callbacks.base import BaseCallbackHandler


class FileLoggerHandler(BaseCallbackHandler):
    def __init__(self, log_dir):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_dir, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id=None, tags=None, metadata=None, **kwargs):
        self.logger.info(
            f"LLM started with prompts: {prompts}, run_id: {run_id}, parent_run_id: {parent_run_id}, tags: {tags}, metadata: {metadata}"
        )

    def on_llm_end(self, response, *, run_id, parent_run_id=None, **kwargs):
        self.logger.info(f"LLM ended with response: {response}, run_id: {run_id}, parent_run_id: {parent_run_id}")

    def on_tool_start(
        self, serialized, input_str, *, run_id, parent_run_id=None, tags=None, metadata=None, inputs=None, **kwargs
    ):
        self.logger.info(
            f"Tool started with input: {input_str}, run_id: {run_id}, parent_run_id: {parent_run_id}, tags: {tags}, metadata: {metadata}"
        )

    def on_tool_end(self, output, *, run_id, parent_run_id=None, **kwargs):
        self.logger.info(f"Tool ended, run_id: {run_id}, parent_run_id: {parent_run_id}")

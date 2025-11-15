import json
import os
import re

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage

# from agent.llm.langchain_deepseek import DeepSeekLLM
from agent.llm.langchain_ollama import OllamaLLM
from agent.utils.template import LLM_JUDGE_PROMPT_TEMPLATE
from llm4netlab.orchestrator.problems.prob_pool import get_problem_instance

load_dotenv()

RESULTS_DIR = os.getenv("RESULTS_DIR")


class LLMJudge:
    def __init__(self):
        # self.llm = DeepSeekLLM()  # Note: good models required here
        self.llm = OllamaLLM(model="qwen3:32b")
        self.prompt = LLM_JUDGE_PROMPT_TEMPLATE

    def _parse_trace(self, trace: str) -> str:
        """Parse the agent's action history trace.
        1. Remove generation info and usage metadata.

        Args:
            trace: The raw trace string.

        Returns:
            str: The parsed trace.
        """
        new_trace = []
        for line in trace.splitlines():
            line = json.loads(line)
            if "event" in line:
                if line["event"] == "llm_start":
                    payload = line.get("prompts", "")
                    new_trace.append(
                        {
                            "timestamp": line.get("timestamp", ""),
                            "event": "LLM Prompt",
                            "payload": payload,
                        }
                    )
                elif line["event"] == "llm_end":
                    payload = line.get("text", "")
                    new_trace.append(
                        {
                            "timestamp": line.get("timestamp", ""),
                            "event": "LLM Response",
                            "payload": payload,
                        }
                    )
                else:
                    new_trace.append(line)
        return json.dumps(new_trace, ensure_ascii=False)

    def evaluate_agent(self, problem_description: str, net_env_info: str, trace_path: str, save_path: str) -> str:
        """Evaluate the agent's performance based on the problem description, network environment info, and action history.

        Args:
            problem_description: Description of the problem.
            net_env_info: Information about the network environment.
            trace_path: Path to the file containing the agent's action history.
            save_path: Path to save the evaluation result.

        Returns:
            str: The evaluation result from the judge model.
            int: The score extracted from the evaluation result.
        """
        with open(trace_path, "r") as f:
            trace = f.read()
        trace = self._parse_trace(trace)

        self.prompt = self.prompt.format(
            problem_description=problem_description,
            net_env_info=net_env_info,
            trace=trace,
        )
        evaluation: BaseMessage = self.llm.invoke(self.prompt)
        evaluation_content = getattr(evaluation, "content")
        score = self._extract_score(evaluation.content)

        # Save evaluation result to file
        with open(save_path, "w+") as f:
            f.write(evaluation_content)

        return evaluation_content, score

    def _extract_score(self, evaluation_result: str) -> int:
        """Extract the score from the evaluation result.

        Args:
            evaluation_result: The evaluation result string.
        """
        one_score_pattern = re.compile(r"\[\[(\d+\.?\d*)\]\]")
        match = one_score_pattern.search(evaluation_result)
        if match:
            return int(match.group(1))
        return -1


if __name__ == "__main__":
    judge = LLMJudge()
    session_id = "20251113090058"
    root_cause_type = "frr_down_localization"
    eval_backend_model_name = "gpt-oss:20b"
    problem_instance = get_problem_instance(root_cause_type)
    problem_description = problem_instance.META.description
    net_env_info = problem_instance.net_env.get_info()

    trace_file = os.path.join(RESULTS_DIR, root_cause_type, f"{session_id}_{eval_backend_model_name}_conversation.log")

    evaluation_content, score = judge.evaluate_agent(
        problem_description,
        net_env_info,
        trace_file,
        save_path=os.path.join(RESULTS_DIR, root_cause_type, f"{session_id}_{eval_backend_model_name}_llm_judge.log"),
    )
    print("Evaluation Result:", evaluation_content)
    print("Evaluation Score:", score)

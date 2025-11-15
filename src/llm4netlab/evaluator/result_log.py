import csv
import os
from dataclasses import asdict, dataclass

from dotenv import load_dotenv

load_dotenv()
RESULTS_DIR = os.getenv("RESULTS_DIR")


@dataclass
class EvalResult:
    agent_name: str = None
    backend_model_name: str = None
    root_cause_category: str = None
    root_cause_type: str = None
    task_level: str = None
    net_env: str = None
    session_id: str = None
    in_tokens: int = None
    out_tokens: int = None
    steps: int = None
    tool_calls: int = None
    tool_errors: int = None
    time_taken: float = None
    llm_judge_score: float = None
    evaluator_score: float = None


def record_eval_result(eval_result: EvalResult) -> None:
    log_results_dir = os.path.join(RESULTS_DIR, "0_summary")
    os.makedirs(log_results_dir, exist_ok=True)

    log_file_path = os.path.join(log_results_dir, "evaluation_summary.csv")

    data = asdict(eval_result)

    file_exists = os.path.exists(log_file_path)

    with open(log_file_path, "a+", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

import csv
import os
from dataclasses import asdict, dataclass

from dotenv import load_dotenv

load_dotenv()
RESULTS_DIR = os.getenv("RESULTS_DIR")


@dataclass
class EvalResult:
    agent_type: str = None
    backend_model: str = None
    root_cause_category: str = None
    root_cause_name: str = None
    net_env: str = None
    scenario_topo_size: str = None
    session_id: str = None
    in_tokens: int = None
    out_tokens: int = None
    steps: int = None
    tool_calls: int = None
    tool_errors: int = None
    time_taken: float = None
    llm_judge_relevance_score: int = None
    llm_judge_correctness_score: int = None
    llm_judge_efficiency_score: int = None
    llm_judge_clarity_score: int = None
    llm_judge_final_outcome_score: int = None
    llm_judge_overall_score: int = None
    detection_score: float = None
    localization_accuracy: float = None
    localization_precision: float = None
    localization_recall: float = None
    localization_f1: float = None
    rca_accuracy: float = None
    rca_precision: float = None
    rca_recall: float = None
    rca_f1: float = None


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

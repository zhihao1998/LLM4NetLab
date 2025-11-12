import os

from dotenv import load_dotenv

load_dotenv()
RESULTS_DIR = os.getenv("RESULTS_DIR")


class EvalResult:
    def __init__(self):
        self.agent_name = None
        self.model_name = None
        self.problem_id = None
        self.net_env = None
        self.session_id = None
        self.in_tokens = None
        self.out_tokens = None
        self.steps = None
        self.tool_calls = None
        self.tool_errors = None
        self.time_taken = None
        self.llm_judge_score = None
        self.evaluator_score = None


def record_eval_result(eval_result: EvalResult) -> None:
    """Record the evaluation result to a log file.

    Args:
    eval_result: The evaluation result to record.
    """
    log_results_dir = os.path.join(RESULTS_DIR, "0_summary")
    os.makedirs(log_results_dir, exist_ok=True)
    log_file_path = os.path.join(log_results_dir, "evaluation_summary.csv")

    if not os.path.exists(log_file_path):
        with open(log_file_path, "a+") as log_file:
            log_file.write(
                "agent_namemodel_name,problem_id,session_id,net_env,in_tokens,out_tokens,steps,tool_calls,tool_errors,time_taken,llm_judge_score,evaluator_score\n"
            )

    with open(log_file_path, "a+") as log_file:
        log_file.write(
            f"{eval_result.agent_name},{eval_result.model_name},{eval_result.problem_id},{eval_result.session_id},{eval_result.net_env},\
                {eval_result.in_tokens},{eval_result.out_tokens},{eval_result.steps},{eval_result.tool_calls},\
                {eval_result.tool_errors},{eval_result.time_taken:.2f},{eval_result.llm_judge_score},{eval_result.evaluator_score}\n"
        )

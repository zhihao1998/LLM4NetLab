import argparse
import json
import logging
import os
import textwrap

from llm4netlab.config import BASE_DIR
from llm4netlab.evaluator.llm_judge import JudgeResponse, LLMJudge
from llm4netlab.evaluator.result_log import EvalResult, record_eval_result
from llm4netlab.evaluator.trace_parser import AgentTraceParser
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.prob_pool import get_problem_instance
from llm4netlab.utils.session import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _eval_problem(session: Session, judge_model: str):
    """Evaluate the problem solution and log the results."""
    sub_log_path = f"{session.session_dir}/{session.backend_model}_submission.log"
    problem = get_problem_instance(
        problem_names=session.problem_names,
        task_level=session.task_level,
        scenario_name=session.scenario_name,
    )

    if not os.path.exists(sub_log_path):
        evaluator_acc = -1
        evaluator_precision = -1
        evaluator_recall = -1
        evaluator_f1 = -1
    else:
        with open(sub_log_path, "r") as f:
            submission = json.load(f)
        # task-specific evaluation
        evaluator_acc, evaluator_precision, evaluator_recall, evaluator_f1 = problem.eval(submission=submission)

    # agent trace
    trace_path = os.path.join(session.session_dir, "conversation.log")

    logger.info(f"Evaluating session {session.session_id} using LLM-as-Judge.")
    # llm as judge evaluation
    llm_judge = LLMJudge(judge_model=judge_model)
    judge_response: JudgeResponse = llm_judge.evaluate_agent(
        problem_description=problem.META.description,
        net_env_info=problem.net_env.get_info(),
        ground_truth=textwrap.dedent(f"""\
                The root cause is {problem.root_cause_name}.
                The faulty devices are: {", ".join(problem.faulty_devices)}.
            """),
        trace_path=trace_path,
        save_path=f"{session.session_dir}/llm_judge.json",
    )
    relevance_score = judge_response.scores.relevance.score
    correctness_score = judge_response.scores.correctness.score
    efficiency_score = judge_response.scores.efficiency.score
    clarity_score = judge_response.scores.clarity.score
    final_outcome_score = judge_response.scores.final_outcome.score
    overall_score = judge_response.scores.overall_score.score

    # parse agent trace
    trace_parser = AgentTraceParser(trace_path=trace_path)
    trace_metrics = trace_parser.parse_trace()

    logger.info(f"All Done! LLM Judge Score: {overall_score}, Evaluator F1 Score: {evaluator_f1}")

    # log evaluation results
    eval_result = EvalResult(
        agent_type=session.agent_type,
        backend_model=session.backend_model,
        root_cause_category=problem.root_cause_category,
        root_cause_name=problem.root_cause_name,
        task_level=session.task_level,
        net_env=problem.net_env.name,
        scenario_topo_size=session.scenario_topo_size,
        session_id=session.session_id,
        in_tokens=trace_metrics.get("in_tokens", None),
        out_tokens=trace_metrics.get("out_tokens", None),
        steps=trace_metrics.get("steps", None),
        tool_calls=trace_metrics.get("tool_calls", None),
        tool_errors=trace_metrics.get("tool_errors", None),
        time_taken=round(float(session.end_time) - float(session.start_time), 2),
        llm_judge_relevance_score=relevance_score,
        llm_judge_correctness_score=correctness_score,
        llm_judge_efficiency_score=efficiency_score,
        llm_judge_clarity_score=clarity_score,
        llm_judge_final_outcome_score=final_outcome_score,
        llm_judge_overall_score=overall_score,
        evaluator_accuracy=evaluator_acc,
        evaluator_precision=evaluator_precision,
        evaluator_recall=evaluator_recall,
        evaluator_f1=evaluator_f1,
    )

    record_eval_result(eval_result)


def eval(judge_model, destroy_env=True):
    """
    Destroy the network environment associated with the current session.
    """
    session = Session()
    session.load_running_session()

    _eval_problem(session, judge_model)
    net_env = get_net_env_instance(session.scenario_name)
    assert net_env.lab_exists(), "Network environment lab does not exist."
    if destroy_env:
        net_env.undeploy()
    logger.info(f"Destroyed network environment: {session.scenario_name} with session ID: {session.session_id}")
    session.clear_session()
    assert not os.path.exists(f"{BASE_DIR}/runtime/current_session.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End Network Environment")
    parser.add_argument(
        "--judge_model",
        type=str,
        nargs="?",
        default="qwen3:32b",
        help="LLM model used for judgment (default: qwen3:32b)",
    )
    args = parser.parse_args()

    eval(judge_model=args.judge_model)

import argparse
import json
import os
import textwrap

from llm4netlab.config import BASE_DIR
from llm4netlab.evaluator.llm_judge import JudgeResponse, LLMJudge
from llm4netlab.evaluator.result_log import EvalResult, record_eval_result
from llm4netlab.evaluator.trace_parser import AgentTraceParser
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.prob_pool import get_problem_instance
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.utils.logger import system_logger
from llm4netlab.utils.session import Session

logger = system_logger


def generic_eval(gt, submission):
    # detection evaluation
    try:
        parsed_detect_sub = DetectionSubmission.model_validate({"is_anomaly": submission.get("is_anomaly", False)})
        if gt["is_anomaly"] == parsed_detect_sub.is_anomaly:
            detection_score = 1.0
        else:
            detection_score = 0.0
    except Exception:
        detection_score = -1.0

    # localization evaluation
    try:
        loc_acc, loc_prec, loc_rec, loc_f1 = LocalizationTask().eval(
            submission={
                "faulty_devices": submission.get("faulty_devices", []),
            },
            gt={
                "faulty_devices": gt.get("faulty_devices", []),
            },
        )
    except Exception:
        loc_acc, loc_prec, loc_rec, loc_f1 = -1.0, -1.0, -1.0, -1.0
    # rca evaluation
    try:
        rca_acc, rca_prec, rca_rec, rca_f1 = RCATask().eval(
            submission={
                "root_cause_name": submission.get("root_cause_name", []),
            },
            gt={
                "root_cause_name": gt.get("root_cause_name", []),
            },
        )
    except Exception:
        rca_acc, rca_prec, rca_rec, rca_f1 = -1.0, -1.0, -1.0, -1.0

    return (
        detection_score,
        loc_acc,
        loc_prec,
        loc_rec,
        loc_f1,
        rca_acc,
        rca_prec,
        rca_rec,
        rca_f1,
    )


def _eval_problem(session: Session, judge_model: str):
    """Evaluate the problem solution and log the results."""
    gt = f"{session.session_dir}/ground_truth.json"
    gt = json.loads(open(gt, "r").read())

    submission = f"{session.session_dir}/submission.json"
    if os.path.exists(submission):
        submission = json.loads(open(submission, "r").read())
        # task-specific evaluation
        (
            detection_score,
            loc_acc,
            loc_prec,
            loc_rec,
            loc_f1,
            rca_acc,
            rca_prec,
            rca_rec,
            rca_f1,
        ) = generic_eval(gt, submission)
    else:
        logger.error(f"Submission file not found: {submission}")
        detection_score = -1.0
        loc_acc = loc_prec = loc_rec = loc_f1 = -1.0
        rca_acc = rca_prec = rca_rec = rca_f1 = -1.0

    # agent trace
    trace_path = os.path.join(session.session_dir, "conversation_diagnosis_agent.log")

    logger.info(f"Evaluating session {session.session_id} using LLM-as-Judge.")

    # llm as judge evaluation
    llm_judge = LLMJudge(judge_model=judge_model)
    judge_response: JudgeResponse = llm_judge.evaluate_agent(
        ground_truth=textwrap.dedent(f"""\
                The root cause is {gt["root_cause_name"]}.
                The faulty devices are: {", ".join(gt["faulty_devices"])}.
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

    logger.info(
        f"All Done! LLM Judge Score: {overall_score}, "
        f"Detection Score: {detection_score}, "
        f"Localization - Acc: {loc_acc}, "
        f"RCA - Acc: {rca_acc}."
    )

    problem = get_problem_instance(
        problem_names=session.problem_names, task_level="detection", scenario_name=session.scenario_name
    )

    # log evaluation results
    eval_result = EvalResult(
        agent_type=session.agent_type,
        backend_model=session.backend_model,
        root_cause_category=problem.root_cause_category,
        root_cause_name=problem.root_cause_name,
        net_env=session.scenario_name,
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
        detection_score=detection_score,
        localization_accuracy=loc_acc,
        localization_precision=loc_prec,
        localization_recall=loc_rec,
        localization_f1=loc_f1,
        rca_accuracy=rca_acc,
        rca_precision=rca_prec,
        rca_recall=rca_rec,
        rca_f1=rca_f1,
    )

    record_eval_result(eval_result)


def eval_results(judge_model, destroy_env=True):
    """
    Destroy the network environment associated with the current session.
    """
    session = Session()
    session.load_running_session()

    _eval_problem(session, judge_model)
    net_env = get_net_env_instance(session.scenario_name)
    if destroy_env and net_env.lab_exists():
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

    eval_results(judge_model=args.judge_model)

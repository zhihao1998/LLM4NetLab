import logging

from dotenv import load_dotenv

from llm4netlab.orchestrator.orchestrator import Orchestrator

load_dotenv()


logging.basicConfig(level=logging.INFO)


backend_model_name = "gpt-oss:20b"
root_cause_category = "device_failure"
root_cause_name = "frr_service_down"
task_level = "detection"
session_id = "1118094629"

orchestrator = Orchestrator()
root_cause_category, task_desc, session_id, lab_name = orchestrator.init_problem(
    root_cause_name=root_cause_name,
    task_level=task_level,
    agent_name="ReAct",
    backend_model_name=backend_model_name,
    session_id=session_id,
    if_inject=False,
)

print(task_desc)
# orchestrator.stop_problem(cleanup=False)

# orchestrator.eval_problem()

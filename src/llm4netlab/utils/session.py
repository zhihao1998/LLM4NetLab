import json
import os
import shutil
from datetime import datetime

from pydantic import BaseModel

from llm4netlab.config import BASE_DIR, RESULTS_DIR


def generate_code():
    time_str = datetime.now().strftime("%m%d%H%M%S")
    return time_str


class SessionKey(BaseModel):
    lab_name: str
    session_id: str
    root_cause_category: str
    root_cause_name: str
    task_level: str
    backend_model: str
    agent_type: str


class Session:
    def __init__(self, session_id = None) -> None:
        if session_id is None:
            pass
        else:
            self.session_id = session_id

    def init_session(self):
        self.session_id = generate_code()

    def load_running_session(self):
        session_meta = json.load(open(f"{BASE_DIR}/runtime/current_session.json", "r"))
        for key, value in session_meta.items():
            setattr(self, key, value)

    def _write_session(self) -> str:
        session_dict = self.__dict__
        with open(f"{BASE_DIR}/runtime/current_session.json", "w") as f:
            f.write(json.dumps(session_dict, indent=4))

    def update_session(self, key: str, value: str):
        setattr(self, key, value)
        self._write_session()

    def set_problem(self, problem, root_cause_name: str):
        self.problem = problem
        if len(root_cause_name) > 1:
            self.root_cause_name = "multiple_faults"
        else:
            self.root_cause_name = root_cause_name

    def write_gt(self, gt: str):
        if hasattr(self, "problem_names") and hasattr(self, "task_level") and hasattr(self, "session_id"):
            if len(self.problem_names) > 1:
                self.root_cause_name = "multiple_faults"
            else:
                self.root_cause_name = self.problem_names[0]
            self.session_dir = f"{RESULTS_DIR}/{self.root_cause_name}/{self.task_level}/{self.session_id}"
            self._write_session()

            os.makedirs(self.session_dir, exist_ok=True)
            with open(self.session_dir + "/ground_truth.json", "w") as f:
                f.write(gt)

    def clear_session(self):
        shutil.move(
            f"{BASE_DIR}/runtime/current_session.json",
            f"{self.session_dir}/session_meta.json",
        )

    def start_session(self):
        self.start_time = datetime.now().timestamp()
        self._write_session()

    def end_session(self):
        self.end_time = datetime.now().timestamp()
        self._write_session()

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)


if __name__ == "__main__":
    session = Session()
    session.load_session()
    print(session)

    session.update_session("lab_name", "test_lab")
    session.update_session("root_cause_category", "connectivity")
    session.update_session("root_cause_name", "missing_route")
    session.update_session("task_level", "easy")
    session.update_session("backend_model", "gpt-4")
    session.update_session("agent_type", "default_agent")

    session._write_session()

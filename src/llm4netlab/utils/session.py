import datetime
import json
import os

from pydantic import BaseModel

from llm4netlab.config import BASE_DIR, RESULTS_DIR


def generate_code():
    time_str = datetime.datetime.now().strftime("%m%d%H%M%S")
    return time_str


class SessionKey(BaseModel):
    lab_name: str
    session_id: str
    root_cause_category: str
    root_cause_name: str
    task_level: str
    backend_model_name: str
    agent_name: str


class Session:
    def __init__(self) -> None:
        pass

    def init_session(self):
        self.start_time = datetime.datetime.now().isoformat()
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
        if hasattr(self, "root_cause_name") and hasattr(self, "task_level") and hasattr(self, "session_id"):
            session_dir = f"{RESULTS_DIR}/{self.root_cause_name}/{self.task_level}/{self.session_id}"
            os.makedirs(session_dir, exist_ok=True)

    def clear_session(self):
        os.remove(f"{BASE_DIR}/runtime/current_session.json")

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
    session.update_session("backend_model_name", "gpt-4")
    session.update_session("agent_name", "default_agent")

    session._write_session()

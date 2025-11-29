import io
import random
import tarfile

import docker

from llm4netlab.config import BASE_DIR
from llm4netlab.generator.fault.injector_host import FaultInjectorHost
from llm4netlab.generator.fault.injector_tc import FaultInjectorTC
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL
from llm4netlab.utils.logger import system_logger

# ==================================================================
# Problem: sender resource contention. Ref. Dapper: Data Plane Performance Diagnosis of TCP
# ==================================================================


class SenderResourceContentionBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.RESOURCE_CONTENTION
    root_cause_name: str = "sender_resource_contention"
    TAGS: str = ["http"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["web"])]

    def inject_fault(self):
        self.injector.inject_stress_all(
            host_name=self.faulty_devices[0],
            duration=600,
        )
        system_logger.info(f"Injected TCP slow sender issue on host {self.faulty_devices[0]}")

    def recover_fault(self):
        self.injector.recover_stress_all(
            host_name=self.faulty_devices[0],
        )
        system_logger.info(f"Recovered TCP slow sender issue on host {self.faulty_devices[0]}")


class SenderResourceContentionDetection(SenderResourceContentionBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=SenderResourceContentionBase.root_cause_category,
        root_cause_name=SenderResourceContentionBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class SenderResourceContentionLocalization(SenderResourceContentionBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=SenderResourceContentionBase.root_cause_category,
        root_cause_name=SenderResourceContentionBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class SenderResourceContentionRCA(SenderResourceContentionBase, RCATask):
    META = ProblemMeta(
        root_cause_category=SenderResourceContentionBase.root_cause_category,
        root_cause_name=SenderResourceContentionBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: Application level delay causing TCP sender issues
# ==================================================================


class SenderApplicationDelayBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.RESOURCE_CONTENTION
    root_cause_name: str = "sender_application_delay"
    TAGS: str = ["http"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorTC(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["host"])]

    def inject_fault(self):
        # backup original web_server.py
        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices[0],
            command="cp web_server.py web_server.py.bak",
        )

        # read the src/llm4netlab/net_env/utils/web/slow_sender_server.py file and replace the web_server.py
        client = docker.from_env()
        container = client.containers.list(filters={"name": f"{self.faulty_devices[0]}"})[0]
        src_path = f"{BASE_DIR}/src/llm4netlab/net_env/utils/web/slow_sender_server.py"

        data = io.BytesIO()
        with tarfile.open(fileobj=data, mode="w") as tar:
            tar.add(src_path, arcname="web_server.py")
        data.seek(0)
        container.put_archive(path="/", data=data)

        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices[0],
            command="systemctl restart web_server.service",
        )
        system_logger.info(f"Injected TCP slow sender issue on host {self.faulty_devices[0]}")

    def recover_fault(self):
        # restore original web_server.py
        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices[0],
            command="mv web_server.py.bak web_server.py",
        )
        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices[0],
            command="systemctl restart web_server.service",
        )
        system_logger.info(f"Recovered TCP sender resource contention issue on host {self.faulty_devices[0]}")


class SenderApplicationDelayDetection(SenderApplicationDelayBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=SenderApplicationDelayBase.root_cause_category,
        root_cause_name=SenderApplicationDelayBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class SenderApplicationDelayLocalization(SenderApplicationDelayBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=SenderApplicationDelayBase.root_cause_category,
        root_cause_name=SenderApplicationDelayBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class SenderApplicationDelayRCA(SenderApplicationDelayBase, RCATask):
    META = ProblemMeta(
        root_cause_category=SenderApplicationDelayBase.root_cause_category,
        root_cause_name=SenderApplicationDelayBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: receiver resource contention
# ==================================================================


class ReceiverResourceContentionBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.RESOURCE_CONTENTION
    root_cause_name: str = "receiver_resource_contention"
    TAGS: str = ["http"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.hosts)]

    def inject_fault(self):
        self.injector.inject_stress_all(
            host_name=self.faulty_devices[0],
            duration=600,
        )
        system_logger.info(f"Injected TCP receiver resource contention on host {self.faulty_devices[0]}")

    def recover_fault(self):
        self.injector.recover_stress_all(
            host_name=self.faulty_devices[0],
        )
        system_logger.info(f"Recovered TCP receiver resource contention on host {self.faulty_devices[0]}")


class ReceiverResourceContentionDetection(ReceiverResourceContentionBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=ReceiverResourceContentionBase.root_cause_category,
        root_cause_name=ReceiverResourceContentionBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class ReceiverResourceContentionLocalization(ReceiverResourceContentionBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=ReceiverResourceContentionBase.root_cause_category,
        root_cause_name=ReceiverResourceContentionBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class ReceiverResourceContentionRCA(ReceiverResourceContentionBase, RCATask):
    META = ProblemMeta(
        root_cause_category=ReceiverResourceContentionBase.root_cause_category,
        root_cause_name=ReceiverResourceContentionBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    problem = SenderApplicationDelayBase(scenario_name="ospf_enterprise_dhcp")
    problem.recover_fault()

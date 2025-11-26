import logging
import random

from llm4netlab.generator.fault.injector_host import FaultInjectorHost
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

# ==================================================================
# Problem: MAC address conflict
# ==================================================================


class MacAddressConflictBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.MISCONFIGURATION
    root_cause_name: str = "mac_address_conflict"
    TAGS: str = ["mac"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        topo = self.net_env.get_topology()
        faulty_link = random.choice(topo)
        device_1, device_2 = faulty_link
        device_1, intf_1 = device_1.split(":")
        device_2, intf_2 = device_2.split(":")
        self.faulty_devices = [device_1, device_2]
        self.falty_links = [intf_1, intf_2]

    def inject_fault(self):
        target_mac = self.kathara_api.get_host_mac_address(self.faulty_devices[1], self.falty_links[1])
        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices[0],
            command=f"ip link set dev eth0 address {target_mac}",
        )
        self.logger.info(
            f"Injected MAC address conflict on {self.faulty_devices[0]} with MAC {target_mac} of {self.faulty_devices[1]}"
        )

    def recover_fault(self):
        random_mac = "12:34:56:78:9a:bb"
        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices[0],
            command=f"ip link set dev eth0 address {random_mac}",
        )
        self.logger.info(f"Recovered MAC address conflict on {self.faulty_devices[0]} by setting MAC to {random_mac}")


class MacAddressConflictDetection(MacAddressConflictBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=MacAddressConflictBase.root_cause_category,
        root_cause_name=MacAddressConflictBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class MacAddressConflictLocalization(MacAddressConflictBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=MacAddressConflictBase.root_cause_category,
        root_cause_name=MacAddressConflictBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class MacAddressConflictRCA(MacAddressConflictBase, RCATask):
    META = ProblemMeta(
        root_cause_category=MacAddressConflictBase.root_cause_category,
        root_cause_name=MacAddressConflictBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    problem = MacAddressConflictBase(scenario_name="ospf_enterprise_static", topo_size="s")
    # problem.inject_fault()
    # problem.recover_fault()

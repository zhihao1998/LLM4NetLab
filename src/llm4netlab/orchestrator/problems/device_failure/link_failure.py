import time

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterpriseDHCP
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==================================================================
# Problem: Link failure by ip link down on host interface
# ==================================================================


class LinkFailureBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    root_cause_name: str = "link_down"

    symptom_desc = "Users report connectivity issues to other hosts."

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or OSPFEnterpriseDHCP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_device = self.net_env.switches[0]
        self.faulty_intf = "eth0"

    def inject_fault(self):
        self.injector.inject_intf_down(
            host_name=self.faulty_device,
            intf_name=self.faulty_intf,
        )
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_intf_down(
            host_name=self.faulty_device,
            intf_name=self.faulty_intf,
        )
        time.sleep(2)


class LinkFailureDetection(LinkFailureBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=LinkFailureBase.root_cause_category,
        root_cause_name=LinkFailureBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class LinkFailureLocalization(LinkFailureBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LinkFailureBase.root_cause_category,
        root_cause_name=LinkFailureBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class LinkFailureRCA(LinkFailureBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LinkFailureBase.root_cause_category,
        root_cause_name=LinkFailureBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==========================================
""" Problem: Link flapping by manual script """


class LinkFlapBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    root_cause_name: str = "link_flap"

    symptom_desc = "Users report connectivity issues to other hosts."

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or OSPFEnterpriseDHCP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_device = self.net_env.switches[0]
        self.faulty_intf = "eth0"

    def inject_fault(self):
        self.injector.inject_link_flap(
            host_name=self.faulty_device,
            intf_name=self.faulty_intf,
            down_time=1,
            up_time=1,
        )
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_link_flap(
            host_name=self.faulty_device,
            intf_name=self.faulty_intf,
        )
        time.sleep(2)


class LinkFlapDetection(LinkFlapBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=LinkFlapBase.root_cause_category,
        root_cause_name=LinkFlapBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class LinkFlapLocalization(LinkFlapBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LinkFlapBase.root_cause_category,
        root_cause_name=LinkFlapBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class LinkFlapRCA(LinkFlapBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LinkFlapBase.root_cause_category,
        root_cause_name=LinkFlapBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==========================================
""" Problem: Link detached. Note: the recover is not working """


class LinkDetachBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    root_cause_name: str = "link_detach"

    symptom_desc = "Users report connectivity issues to other hosts."

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or OSPFEnterpriseDHCP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_device = self.net_env.switches[0]
        self.faulty_intf = "eth0"

    def inject_fault(self):
        self.injector.inject_link_detach(
            host_name=self.faulty_device,
            intf_name=self.faulty_intf,
        )
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_link_detach(
            host_name=self.faulty_device,
            intf_name=self.faulty_intf,
        )
        time.sleep(2)


class LinkDetachDetection(LinkDetachBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=LinkDetachBase.root_cause_category,
        root_cause_name=LinkDetachBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class LinkDetachLocalization(LinkDetachBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LinkDetachBase.root_cause_category,
        root_cause_name=LinkDetachBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class LinkDetachRCA(LinkDetachBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LinkDetachBase.root_cause_category,
        root_cause_name=LinkDetachBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    task = LinkFailureDetection()
    # task.inject_fault()
    # Here you would typically run your detection logic
    task.recover_fault()

import time

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterprise
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission, LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCASubmission, RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
""" Problem: Link failure by ip link down on host interface """


class LinkFailureBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    ROOT_CAUSE_NAME: str = "link_down"

    faulty_device = "switch_dist_1_1"
    faulty_intf = "eth0"
    symptom_desc = "Users report connectivity issues to other hosts."

    def __init__(self):
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

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
        root_cause_category=LinkFailureBase.get.DEVICE_FAILURE,
        root_cause_name=LinkFailureBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class LinkFailureLocalization(LinkFailureBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LinkFailureBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFailureBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[LinkFailureBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class LinkFailureRCA(LinkFailureBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LinkFailureBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFailureBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=LinkFailureBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFailureBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==========================================
""" Problem: Link flapping by manual script """


class LinkFlapBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    ROOT_CAUSE_NAME: str = "link_flap"

    faulty_device = "switch_dist_1_1"
    faulty_intf = "eth0"
    symptom_desc = "Users report connectivity issues to other hosts."

    def __init__(self):
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

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
        root_cause_category=LinkFlapBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFlapBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class LinkFlapLocalization(LinkFlapBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LinkFlapBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFlapBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[LinkFlapBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class LinkFlapRCA(LinkFlapBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LinkFlapBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFlapBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=LinkFlapBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFlapBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==========================================
""" Problem: Link detached. Note: the recover is not working """


class LinkDetachBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    ROOT_CAUSE_NAME: str = "link_detach"

    faulty_device = "switch_dist_1_1"
    faulty_intf = "eth0"
    symptom_desc = "Users report connectivity issues to other hosts."

    def __init__(self):
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

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
        root_cause_category=LinkDetachBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkDetachBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class LinkDetachLocalization(LinkDetachBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LinkDetachBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkDetachBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[LinkDetachBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class LinkDetachRCA(LinkDetachBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LinkDetachBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkDetachBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=LinkDetachBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkDetachBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    task = LinkFailureDetection()
    # task.inject_fault()
    # Here you would typically run your detection logic
    task.recover_fault()

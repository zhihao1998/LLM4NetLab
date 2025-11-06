from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.problems.problem_base import IssueType
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission, LocalizationTask


class FrrDownLocalization(LocalizationTask):
    SUBMISSION = LocalizationSubmission.DeviceFailure(
        issue_type=IssueType.DEVICE_FAILURE,
        problem_id="frr_down_localization",
        failed_device="router1",
        failed_service="frr",
    )

    def __init__(self):
        self.net_env = SimpleBGP()
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_service_down(host_name="router1", service_name="frr")

    def recover_fault(self):
        self.injector.recover_service_down(host_name="router1", service_name="frr")

True
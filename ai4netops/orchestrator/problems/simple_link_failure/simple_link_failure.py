"""Simple Link Failure Problem for Testing the Orchestrator"""

from ai4netops.generator.fault.injector_mininet import FaultInjectorMininet
from ai4netops.generator.workload.workload_mininet import WorkloadMininet


class SimpleLinkFailureBaseTask:
    """Base class for the Simple Link Failure Task."""

    def __init__(self):
        self.fault_injector = FaultInjectorMininet()
        self.workload_generator = WorkloadMininet()

    def start_workload(self):
        """Start the workload."""
        response = self.workload_generator.ping_pair("h1", "10.0.0.2")
        if "0% packet loss" in response:
            return True

    def inject_fault(self):
        """Inject a link down fault."""
        self.fault_injector.inject_link_down("h1", "s1")

    def recover_fault(self):
        """Recover the link down fault."""
        self.fault_injector.recover_link_down("h1", "s1")

    def check_recovery(self):
        """Check if the link is up after recovery."""
        response = self.workload_generator.ping_pair("h1", "10.0.0.2")
        if "0% packet loss" in response:
            return True
        else:
            return False

class SimpleLinkFailureDetectionTask(SimpleLinkFailureBaseTask):
    """Detection task for the Simple Link Failure Problem."""

    def __init__(self):
        super().__init__()

    def detect_fault(self):
        """Detect if the link is down."""
        response = self.workload_generator.ping_pair("h1", "


if __name__ == "__main__":
    task = SimpleLinkFailureBaseTask()
    task.start_workload()
    task.inject_fault()
    task.check_recovery()
    task.recover_fault()
    task.check_recovery()

from llm4netlab.net_env.kathara.l2_basic_forwarding.lab import L2BasicForwarding
from llm4netlab.orchestrator.tasks.discovery import DiscoveryTask
from llm4netlab.service.kathara_api import KatharaAPI


class P4TableEntryMissingBase:
    def __init__(self):
        self.net_env = L2BasicForwarding()
        self.kathara_api = KatharaAPI(lab_name=self.net_env.lab.name)

        self.problem_name = "P4TableEntryMissing"
        self.problem_description = (
            "A simple problem to detect whether the disconnectivity is caused by the missing P4 table entry."
        )


class P4TableEntryMissingDiscovery(P4TableEntryMissingBase, DiscoveryTask):
    def __init__(self):
        P4TableEntryMissingBase.__init__(self)
        DiscoveryTask.__init__(self, self.net_env)
        self.problem_name = "P4TableEntryMissingDiscovery"
        self.problem_description = (
            "Basic discovery problem to detect whether the disconnectivity is caused by the missing P4 table entry."
        )


class P4TableEntryMissingDetection(P4TableEntryMissingBase):
    def __init__(self):
        super().__init__()
        self.problem_name = "P4TableEntryMissingDetection"
        self.problem_description = (
            "A simple detection problem to detect whether the disconnectivity is caused by the missing P4 table entry."
        )

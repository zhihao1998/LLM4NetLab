import random

from llm4netlab.generator.fault.injector_host import FaultInjectorHost
from llm4netlab.generator.fault.injector_tc import FaultInjectorTC
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

# ==================================================================
# Problem: Web service experiencing high DNS lookup latency causing performance degradation.
# ==================================================================


class DNSLookupLatencyBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.PERFORMANCE_DEGRADATION
    root_cause_name: str = "dns_lookup_latency"
    symptom_desc: str = "Users experience high latency when accessing web services."
    TAGS: str = ["dns", "http"]

    def __init__(self, scenario_name: str = "dc_clos_service", **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorTC(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["dns"])]

    def inject_fault(self):
        self.injector.inject_delay(host_name=self.faulty_devices[0], intf_name="eth0", delay_ms=1000)

    def recover_fault(self):
        self.injector.recover_delay(host_name=self.faulty_devices[0], intf_name="eth0")


class DNSLookupLatencyDetection(DNSLookupLatencyBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DNSLookupLatencyBase.root_cause_category,
        root_cause_name=DNSLookupLatencyBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class DNSLookupLatencyLocalization(DNSLookupLatencyBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DNSLookupLatencyBase.root_cause_category,
        root_cause_name=DNSLookupLatencyBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class DNSLookupLatencyRCA(DNSLookupLatencyBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DNSLookupLatencyBase.root_cause_category,
        root_cause_name=DNSLookupLatencyBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: Load balancer overload causing performance degradation.
# ==================================================================


class LoadBalancerOverloadBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.PERFORMANCE_DEGRADATION
    root_cause_name: str = "load_balancer_overload"
    TAGS: str = ["load_balancer", "http"]

    def __init__(self, scenario_name: str = "load_balancer", **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["load_balancer"])]

    def inject_fault(self):
        self.injector.inject_stress_all(host_name=self.faulty_devices[0])

    def recover_fault(self):
        self.injector.recover_stress_all(host_name=self.faulty_devices[0])


class LoadBalancerOverloadDetection(LoadBalancerOverloadBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=LoadBalancerOverloadBase.root_cause_category,
        root_cause_name=LoadBalancerOverloadBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class LoadBalancerOverloadLocalization(LoadBalancerOverloadBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LoadBalancerOverloadBase.root_cause_category,
        root_cause_name=LoadBalancerOverloadBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class LoadBalancerOverloadRCA(LoadBalancerOverloadBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LoadBalancerOverloadBase.root_cause_category,
        root_cause_name=LoadBalancerOverloadBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    # Test the fault injection and recovery
    problem = LoadBalancerOverloadBase()
    problem.inject_fault()
    # problem.recover_fault()

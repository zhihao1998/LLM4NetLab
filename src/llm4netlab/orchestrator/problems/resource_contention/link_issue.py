import logging
import random

from llm4netlab.generator.fault.injector_tc import FaultInjectorTC
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

# ==================================================================
# Problem: High link packet corruption between devices causing performance degradation.
# ==================================================================


class LinkHighPacketCorruptionBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.RESOURCE_CONTENTION
    root_cause_name: str = "link_high_packet_corruption"
    TAGS: str = ["link"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorTC(lab_name=self.net_env.lab.name)
        self.faulty_devices: str = [random.choice(self.net_env.hosts)]

    def inject_fault(self):
        intf_name = self.kathara_api.get_host_interfaces(self.faulty_devices[0])[-1]
        self.injector.inject_packet_corruption(
            host_name=self.faulty_devices[0], intf_name=intf_name, corruption_percentage=60
        )

    def recover_fault(self):
        intf_name = self.kathara_api.get_host_interfaces(self.faulty_devices[0])[-1]
        self.injector.recover_packet_corruption(
            host_name=self.faulty_devices[0],
            intf_name=intf_name,
        )


class LinkHighPacketCorruptionDetection(LinkHighPacketCorruptionBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=LinkHighPacketCorruptionBase.root_cause_category,
        root_cause_name=LinkHighPacketCorruptionBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class LinkHighPacketCorruptionLocalization(LinkHighPacketCorruptionBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LinkHighPacketCorruptionBase.root_cause_category,
        root_cause_name=LinkHighPacketCorruptionBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class LinkHighPacketCorruptionRCA(LinkHighPacketCorruptionBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LinkHighPacketCorruptionBase.root_cause_category,
        root_cause_name=LinkHighPacketCorruptionBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: Bandwidth throttling on a link causing performance degradation.
# ==================================================================


class LinkBandwidthThrottlingBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.RESOURCE_CONTENTION
    root_cause_name: str = "link_bandwidth_throttling"
    TAGS: str = ["link"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorTC(lab_name=self.net_env.lab.name)
        self.faulty_devices: str = [random.choice(self.net_env.hosts)]

    def inject_fault(self):
        intf_name = self.kathara_api.get_host_interfaces(self.faulty_devices[0])[0]
        self.injector.inject_bandwidth_limit(
            host_name=self.faulty_devices[0], intf_name=intf_name, rate="30kbit", burst="64kb", limit="500kb"
        )

    def recover_fault(self):
        intf_name = self.kathara_api.get_host_interfaces(self.faulty_devices[0])[0]
        self.injector.recover_bandwidth_limit(
            host_name=self.faulty_devices[0],
            intf_name=intf_name,
        )


class LinkBandwidthThrottlingDetection(LinkBandwidthThrottlingBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=LinkBandwidthThrottlingBase.root_cause_category,
        root_cause_name=LinkBandwidthThrottlingBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class LinkBandwidthThrottlingLocalization(LinkBandwidthThrottlingBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LinkBandwidthThrottlingBase.root_cause_category,
        root_cause_name=LinkBandwidthThrottlingBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class LinkBandwidthThrottlingRCA(LinkBandwidthThrottlingBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LinkBandwidthThrottlingBase.root_cause_category,
        root_cause_name=LinkBandwidthThrottlingBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: Queue overflow caused by micro-bursts on a link causing performance degradation.
# ==================================================================


class LinkQueueOverflowBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.RESOURCE_CONTENTION
    root_cause_name: str = "link_queue_overflow"
    TAGS: str = ["link"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorTC(lab_name=self.net_env.lab.name)
        self.faulty_devices: str = [
            random.choice(
                self.net_env.routers
                or self.net_env.switches
                or self.net_env.ovs_switches
                or self.net_env.bmv2_switches
                or self.net_env.hosts
            )
        ]

    def inject_fault(self):
        intf_name = self.kathara_api.get_host_interfaces(self.faulty_devices[0])[1]
        self.injector.inject_delay(host_name=self.faulty_devices[0], intf_name=intf_name, delay_ms=50, limit="1")

    def recover_fault(self):
        intf_name = self.kathara_api.get_host_interfaces(self.faulty_devices[0])[1]
        self.injector.recover_delay(
            host_name=self.faulty_devices[0],
            intf_name=intf_name,
        )


class LinkQueueOverflowDetection(LinkQueueOverflowBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=LinkQueueOverflowBase.root_cause_category,
        root_cause_name=LinkQueueOverflowBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class LinkQueueOverflowLocalization(LinkQueueOverflowBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LinkQueueOverflowBase.root_cause_category,
        root_cause_name=LinkQueueOverflowBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class LinkQueueOverflowRCA(LinkQueueOverflowBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LinkQueueOverflowBase.root_cause_category,
        root_cause_name=LinkQueueOverflowBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    task = LinkBandwidthThrottlingBase()
    print(task.faulty_devices)
    # task.recover_fault()
    # task.inject_fault()

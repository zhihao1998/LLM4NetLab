import logging
import random

from llm4netlab.generator.fault.injector_tc import FaultInjectorTC
from llm4netlab.generator.traffic.od_flows import ODFLowGenerator
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL
from llm4netlab.utils.logger import system_logger

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
        self.faulty_devices = [random.choice(self.net_env.hosts)]

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
        self.faulty_devices = [random.choice(self.net_env.hosts)]

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
# Problem: incast traffic causing performance degradation.
# ==================================================================


class IncastTrafficNetworkLimitationBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.RESOURCE_CONTENTION
    root_cause_name: str = "incast_traffic_network_limitation"
    TAGS: str = ["http"]

    def __init__(self, scenario_name: str = "dc_clos_service", **kwargs):
        super().__init__()
        self.scenario_name = scenario_name
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorTC(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["web"])]

    def inject_fault(self):
        self.kathara_api.tc_set_netem(host_name=self.faulty_devices[0], intf_name="eth0", delay_ms=20, handle="1")
        self.kathara_api.tc_set_tbf(
            host_name=self.faulty_devices[0],
            intf_name="eth0",
            rate="1mbit",
            burst="500kb",
            limit="500kb",
            handle="10",
            parent="1:1",
        )
        system_logger.info(f"Injected network limitation on host {self.faulty_devices[0]}")

        generator = ODFLowGenerator(lab_name=self.scenario_name)
        od_dict = {}
        mbps = 20
        for host in self.net_env.hosts:
            od_dict.setdefault(host, {})
            od_dict[host][self.faulty_devices[0]] = mbps
        res = generator.start_traffic_background(od_dicts=od_dict, interval=300, unit="M", udp=True)
        system_logger.info(f"Started background traffic generation {res} to amplify the network limitation effect.")

    def recover_fault(self):
        self.kathara_api.tc_clear_intf(host_name=self.faulty_devices[0], intf_name="eth0")
        system_logger.info(f"Recovered network limitation on host {self.faulty_devices[0]}")
        # stop all background traffic
        for host in self.net_env.hosts:
            self.kathara_api.exec_cmd(host_name=host, command="pkill -f iperf3")
        for server in self.net_env.servers["web"]:
            self.kathara_api.exec_cmd(host_name=server, command="pkill -f iperf3")
        system_logger.info("Stopped all background traffic generation.")


class IncastTrafficNetworkLimitationDetection(IncastTrafficNetworkLimitationBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=IncastTrafficNetworkLimitationBase.root_cause_category,
        root_cause_name=IncastTrafficNetworkLimitationBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class IncastTrafficNetworkLimitationLocalization(IncastTrafficNetworkLimitationBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=IncastTrafficNetworkLimitationBase.root_cause_category,
        root_cause_name=IncastTrafficNetworkLimitationBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class IncastTrafficNetworkLimitationRCA(IncastTrafficNetworkLimitationBase, RCATask):
    META = ProblemMeta(
        root_cause_category=IncastTrafficNetworkLimitationBase.root_cause_category,
        root_cause_name=IncastTrafficNetworkLimitationBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    task = IncastTrafficNetworkLimitationBase(scenario_name="ospf_enterprise_dhcp")
    task.recover_fault()
    # task.inject_fault()

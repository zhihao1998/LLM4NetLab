import logging
import random

from llm4netlab.generator.fault.injector_host import FaultInjectorHost
from llm4netlab.net_env.intradomain_routing.rip_vpn.lab import RIPSmallInternetVPN
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
# Problem: VPN membership missing on end host causing inability to access services over VPN.
# ==========================================


class VPNMembershipMissingBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.END_HOST_FAILURE
    root_cause_name: str = "host_vpn_membership_missing"
    TAGS: str = ["vpn"]

    def __init__(self, scenario_name: str | None, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.net_env = get_net_env_instance(
            scenario_name,
        ) or RIPSmallInternetVPN(**kwargs)
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.vpn_server = self.net_env.servers["vpn"][0]
        self.target_host = random.choice(["host_1", "web_server_1_1", "web_server_1_2"])

        self.faulty_devices = [self.target_host, self.vpn_server]

    def inject_fault(self):
        # backup the real conf and
        self.kathara_api.exec_cmd(
            host_name=self.vpn_server,
            command="cp /etc/wireguard/wg0.conf /etc/wireguard/wg0.conf.bak",
        )
        # remove the vpn conf to simulate missing vpn membership
        self.kathara_api.exec_cmd(
            host_name=self.vpn_server,
            command=f"sed -i '/# {self.target_host}/{{n; s/^/# /; n; s/^/# /; n; s/^/# /;}}' /etc/wireguard/wg0.conf",
        )
        # restart the wg interface
        self.kathara_api.exec_cmd(
            host_name=self.vpn_server,
            command="wg-quick down wg0 && wg-quick up wg0",
        )
        self.logger.info(f"Removed VPN membership of {self.target_host} on {self.vpn_server}.")

    def recover_fault(self):
        # restore the real conf
        self.kathara_api.exec_cmd(
            host_name=self.vpn_server,
            command="mv /etc/wireguard/wg0.conf.bak /etc/wireguard/wg0.conf",
        )
        # restart the wg interface
        self.kathara_api.exec_cmd(
            host_name=self.vpn_server,
            command="wg-quick down wg0 && wg-quick up wg0",
        )
        self.logger.info(f"Restored VPN membership of {self.target_host} on {self.vpn_server}.")


class HostIncorrectDNSDetection(VPNMembershipMissingBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=VPNMembershipMissingBase.root_cause_category,
        root_cause_name=VPNMembershipMissingBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class HostIncorrectDNSLocalization(VPNMembershipMissingBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=VPNMembershipMissingBase.root_cause_category,
        root_cause_name=VPNMembershipMissingBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class HostIncorrectDNSRCA(VPNMembershipMissingBase, RCATask):
    META = ProblemMeta(
        root_cause_category=VPNMembershipMissingBase.root_cause_category,
        root_cause_name=VPNMembershipMissingBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    host_ip_conflict = VPNMembershipMissingBase(scenario_name="rip_small_internet_vpn")
    host_ip_conflict.recover_fault()
    host_ip_conflict.inject_fault()

import logging

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterpriseDHCP
from llm4netlab.net_env.intradomain_routing.ospf_enterprise.lab_static import OSPFEnterpriseStatic
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

logger = logging.getLogger(__name__)
# ==================================================================
# Problem: DNS service down
# ==================================================================


class DNSServiceDownBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.SERVICE_DEPENDENCY_FAILURE
    root_cause_name: str = "dns_service_down"

    faulty_devices = "dns_server"
    symptom_desc = "Some hosts cannot access external websites."

    def __init__(self):
        self.net_env = OSPFEnterpriseDHCP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_service_down(host_name=self.faulty_devices, service_name="named")

    def recover_fault(self):
        self.injector.recover_service_down(host_name=self.faulty_devices, service_name="named")


class DNSServiceDownDetection(DNSServiceDownBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DNSServiceDownBase.root_cause_category,
        root_cause_name=DNSServiceDownBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class DNSServiceDownLocalization(DNSServiceDownBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DNSServiceDownBase.root_cause_category,
        root_cause_name=DNSServiceDownBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class DNSServiceDownRCA(DNSServiceDownBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DNSServiceDownBase.root_cause_category,
        root_cause_name=DNSServiceDownBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: DNS listener port blocked
# ==================================================================


class DNSPortBlockedBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.SERVICE_DEPENDENCY_FAILURE
    root_cause_name: str = "dns_port_blocked"

    faulty_devices = "dns_server"
    symptom_desc = "Some hosts cannot access external websites."

    def __init__(self):
        self.net_env = OSPFEnterpriseDHCP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_acl_rule(
            host_name=self.faulty_devices,
            rule="tcp dport 53 drop",
            table_name="filter",
        )
        self.injector.inject_acl_rule(
            host_name=self.faulty_devices,
            rule="udp dport 53 drop",
            table_name="filter",
        )

    def recover_fault(self):
        self.injector.recover_acl_rule(
            host_name=self.faulty_devices,
            table_name="filter",
        )
        self.injector.recover_acl_rule(
            host_name=self.faulty_devices,
            table_name="filter",
        )


class DNSPortBlockedDetection(DNSPortBlockedBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DNSPortBlockedBase.root_cause_category,
        root_cause_name=DNSPortBlockedBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class DNSPortBlockedLocalization(DNSPortBlockedBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DNSPortBlockedBase.root_cause_category,
        root_cause_name=DNSPortBlockedBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class DNSPortBlockedRCA(DNSPortBlockedBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DNSPortBlockedBase.root_cause_category,
        root_cause_name=DNSPortBlockedBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: DNS record error. Apps resolve domain but connect to wrong host.
# ==================================================================


class DNSRecordErrorBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.SERVICE_DEPENDENCY_FAILURE
    root_cause_name: str = "dns_record_error"

    symptom_desc = "Some hosts cannot access external websites."

    def __init__(self, net_env_name: str | None, **kwargs):
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.servers["dns"][0]
        self.target_website = self.net_env.web_urls[0].split(".")[0]
        if self.target_website.startswith("http://"):
            self.target_website = self.target_website[len("http://") :]
        self.target_domain = self.net_env.web_urls[0].split(".")[1]
        self.right_ip = self.kathara_api.get_host_ip(self.faulty_device)
        self.wrong_ip = self.kathara_api.get_host_ip(self.net_env.hosts[0])

    def inject_fault(self):
        # backup original record
        self.kathara_api.exec_cmd(
            self.faulty_devices,
            f"cp /etc/bind/db.{self.target_domain} /etc/bind/db.{self.target_domain}.bak",
        )
        # inject wrong record
        cmd = r"sed -i 's/^\({name}[[:space:]]\+IN[[:space:]]\+A[[:space:]]\+\)[0-9\.]\+/\1{new_ip}/' /etc/bind/db.{domain}"
        cmd = cmd.format(name=self.target_website, new_ip=self.wrong_ip, domain=self.target_domain)
        self.kathara_api.exec_cmd(self.faulty_devices, cmd)
        # restart dns service
        self.kathara_api.exec_cmd(self.faulty_devices, "systemctl restart named")
        logger.info(
            f"Injecting DNS record error on {self.faulty_device}: mapping {self.target_website}:{self.target_domain} "
            f"to wrong IP {self.wrong_ip} instead of {self.right_ip}"
        )

    def recover_fault(self):
        # restore original record
        self.kathara_api.exec_cmd(
            self.faulty_devices,
            f"mv /etc/bind/db.{self.target_domain}.bak /etc/bind/db.{self.target_domain}",
        )
        # restart dns service
        self.kathara_api.exec_cmd(self.faulty_devices, "systemctl restart named")
        logger.info(f"Recovered DNS record error on {self.faulty_device}")


class DNSRecordErrorDetection(DNSRecordErrorBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DNSRecordErrorBase.root_cause_category,
        root_cause_name=DNSRecordErrorBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class DNSRecordErrorLocalization(DNSRecordErrorBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DNSRecordErrorBase.root_cause_category,
        root_cause_name=DNSRecordErrorBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class DNSRecordErrorRCA(DNSRecordErrorBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DNSRecordErrorBase.root_cause_category,
        root_cause_name=DNSRecordErrorBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dns_error = DNSRecordErrorBase()
    # dns_error.inject_fault()
    dns_error.recover_fault()

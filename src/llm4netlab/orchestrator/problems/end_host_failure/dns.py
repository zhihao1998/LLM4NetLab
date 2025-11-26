import logging
import random

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

logger = logging.getLogger(__name__)


# ==================================================================
# Problem: DNS record error. Apps resolve domain but connect to wrong host.
# ==================================================================


class DNSRecordErrorBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.END_HOST_FAILURE
    root_cause_name: str = "dns_record_error"

    symptom_desc = "Some hosts cannot access external websites."
    TAGS: str = ["dns"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [self.net_env.servers["dns"][0]]
        url = random.choice(self.net_env.web_urls)

        self.target_website = url.split(".")[0]

        if self.target_website.startswith("http://"):
            self.target_website = self.target_website[len("http://") :]

        self.target_domain = url.split(".")[1]
        self.right_ip = self.kathara_api.get_host_ip(self.faulty_devices[0])
        self.wrong_ip = self.kathara_api.get_host_ip(self.net_env.hosts[0])

    def inject_fault(self):
        # backup original record
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"cp /etc/bind/db.{self.target_domain} /etc/bind/db.{self.target_domain}.bak",
        )
        # inject wrong record
        cmd = r"sed -i 's/^\({name}[[:space:]]\+IN[[:space:]]\+A[[:space:]]\+\)[0-9\.]\+/\1{new_ip}/' /etc/bind/db.{domain}"
        cmd = cmd.format(name=self.target_website, new_ip=self.wrong_ip, domain=self.target_domain)
        self.kathara_api.exec_cmd(self.faulty_devices[0], cmd)
        # restart dns service
        self.kathara_api.exec_cmd(self.faulty_devices[0], "systemctl restart named")
        logger.info(
            f"Injecting DNS record error on {self.faulty_devices[0]}: mapping {self.target_website}:{self.target_domain} "
            f"to wrong IP {self.wrong_ip} instead of {self.right_ip}"
        )

    def recover_fault(self):
        # restore original record
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"mv /etc/bind/db.{self.target_domain}.bak /etc/bind/db.{self.target_domain}",
        )
        # restart dns service
        self.kathara_api.exec_cmd(self.faulty_devices[0], "systemctl restart named")
        logger.info(f"Recovered DNS record error on {self.faulty_devices[0]}")


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

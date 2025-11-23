import logging

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.net_env.sdn.lab import SDNOpenFlow
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

# ==================================================================
# Problem: SDN controller crash
# ==================================================================

logger = logging.getLogger(__name__)


class SDNControllerCrashBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.SDN_CONTROL_PLANE_ISSUE
    root_cause_name: str = "sdn_controller_crash"

    def __init__(self, net_env_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or SDNOpenFlow()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices: str = self.net_env.sdn_controllers[0]

    def inject_fault(self):
        self.kathara_api.exec_cmd(
            self.faulty_devices,
            "pkill -f ryu-manager",
        )

    def recover_fault(self):
        self.kathara_api.exec_cmd(
            self.faulty_devices,
            "ryu-manager ryu.app.simple_switch &",
        )


class SDNControllerCrashDetection(SDNControllerCrashBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=SDNControllerCrashBase.root_cause_category,
        root_cause_name=SDNControllerCrashBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class SDNControllerCrashLocalization(SDNControllerCrashBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=SDNControllerCrashBase.root_cause_category,
        root_cause_name=SDNControllerCrashBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class SDNControllerCrashRCA(SDNControllerCrashBase, RCATask):
    META = ProblemMeta(
        root_cause_category=SDNControllerCrashBase.root_cause_category,
        root_cause_name=SDNControllerCrashBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: Southbound port block
# ==================================================================


class SouthboundPortBlockBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.SDN_CONTROL_PLANE_ISSUE
    root_cause_name: str = "southbound_port_block"

    def __init__(self, net_env_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or SDNOpenFlow()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices: str = self.net_env.sdn_controllers[0]
        self.southbound_port: int = 6633  # Default OpenFlow port

    def inject_fault(self):
        self.injector.inject_acl_rule(
            host_name=self.faulty_devices,
            rule=f"tcp dport {self.southbound_port} drop",
        )

    def recover_fault(self):
        self.injector.recover_acl_rule(host_name=self.faulty_device)


class SouthboundPortBlockDetection(SouthboundPortBlockBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=SouthboundPortBlockBase.root_cause_category,
        root_cause_name=SouthboundPortBlockBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class SouthboundPortBlockLocalization(SouthboundPortBlockBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=SouthboundPortBlockBase.root_cause_category,
        root_cause_name=SouthboundPortBlockBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class SouthboundPortBlockRCA(SouthboundPortBlockBase, RCATask):
    META = ProblemMeta(
        root_cause_category=SouthboundPortBlockBase.root_cause_category,
        root_cause_name=SouthboundPortBlockBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: Southbound port mismatch
# ==================================================================


class SouthboundPortMismatchBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.SDN_CONTROL_PLANE_ISSUE
    root_cause_name: str = "southbound_port_mismatch"

    def __init__(self, net_env_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or SDNOpenFlow()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices: str = self.net_env.sdn_controllers[0]
        self.original_port: int = 6633  # Default OpenFlow port
        self.mismatched_port: int = 6653  # Common alternative OpenFlow port

    def inject_fault(self):
        self.kathara_api.exec_cmd(
            self.faulty_devices,
            "pkill -f ryu-manager",
        )
        self.kathara_api.exec_cmd(
            self.faulty_devices,
            f"ryu-manager --ofp-tcp-listen-port {self.mismatched_port} ryu.app.simple_switch &",
        )

    def recover_fault(self):
        self.kathara_api.exec_cmd(
            self.faulty_devices,
            "pkill -f ryu-manager",
        )
        self.kathara_api.exec_cmd(
            self.faulty_devices,
            "ryu-manager ryu.app.simple_switch &",
        )


class SouthboundPortMismatchDetection(SouthboundPortMismatchBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=SouthboundPortMismatchBase.root_cause_category,
        root_cause_name=SouthboundPortMismatchBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class SouthboundPortMismatchLocalization(SouthboundPortMismatchBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=SouthboundPortMismatchBase.root_cause_category,
        root_cause_name=SouthboundPortMismatchBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class SouthboundPortMismatchRCA(SouthboundPortMismatchBase, RCATask):
    META = ProblemMeta(
        root_cause_category=SouthboundPortMismatchBase.root_cause_category,
        root_cause_name=SouthboundPortMismatchBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: Flow rule shadowing
# ==================================================================


class FlowRuleShadowingBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.SDN_CONTROL_PLANE_ISSUE
    root_cause_name: str = "flow_rule_shadowing"

    def __init__(self, net_env_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or SDNOpenFlow()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices: str = self.net_env.ovs_switches[0]

    def inject_fault(self):
        # Inject a shadowing flow rule that matches all traffic and forwards to a blackhole
        self.kathara_api.exec_cmd(
            self.faulty_devices,
            f"ovs-ofctl add-flow {self.faulty_device} 'priority=100,actions=drop'",
        )

    def recover_fault(self):
        # Remove the shadowing flow rule
        self.kathara_api.exec_cmd(
            self.faulty_devices,
            f"ovs-ofctl --strict del-flows {self.faulty_device} 'priority=100'",
        )


class FlowRuleShadowingDetection(FlowRuleShadowingBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=FlowRuleShadowingBase.root_cause_category,
        root_cause_name=FlowRuleShadowingBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class FlowRuleShadowingLocalization(FlowRuleShadowingBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=FlowRuleShadowingBase.root_cause_category,
        root_cause_name=FlowRuleShadowingBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class FlowRuleShadowingRCA(FlowRuleShadowingBase, RCATask):
    META = ProblemMeta(
        root_cause_category=FlowRuleShadowingBase.root_cause_category,
        root_cause_name=FlowRuleShadowingBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: Flow rule loop
# ==================================================================


class FlowRuleLoopBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.SDN_CONTROL_PLANE_ISSUE
    ROOT_CAUSE_NAME: str = "flow_rule_loop"

    def __init__(self, net_env_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or SDNOpenFlow()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices: str = self.net_env.ovs_switches[:2]

    def inject_fault(self):
        # Inject flow rules that create a forwarding loop between two ports
        self.kathara_api.exec_cmd(
            self.faulty_device[0],
            f"ovs-ofctl add-flow {self.faulty_device[0]} 'in_port=eth0,actions=output:eth0'",
        )
        self.kathara_api.exec_cmd(
            self.faulty_device[1],
            f"ovs-ofctl add-flow {self.faulty_device[1]} 'in_port=eth1,actions=output:eth1'",
        )

    def recover_fault(self):
        # Remove the loop-inducing flow rules
        self.kathara_api.exec_cmd(
            self.faulty_device[0],
            f"ovs-ofctl --strict del-flows {self.faulty_device[0]} 'in_port=eth0'",
        )
        self.kathara_api.exec_cmd(
            self.faulty_device[1],
            f"ovs-ofctl --strict del-flows {self.faulty_device[1]} 'in_port=eth1'",
        )


class FlowRuleLoopDetection(FlowRuleLoopBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=FlowRuleLoopBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=FlowRuleLoopBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class FlowRuleLoopLocalization(FlowRuleLoopBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=FlowRuleLoopBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=FlowRuleLoopBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class FlowRuleLoopRCA(FlowRuleLoopBase, RCATask):
    META = ProblemMeta(
        root_cause_category=FlowRuleLoopBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=FlowRuleLoopBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    # For quick test
    logging.basicConfig(level=logging.INFO)
    problem = FlowRuleLoopBase()
    problem.inject_fault()
    # problem.recover_fault()

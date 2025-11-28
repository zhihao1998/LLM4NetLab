import asyncio

from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.base import TaskBase
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask


class MultiFaultBase(TaskBase):
    root_cause_category = RootCauseCategory.MULTIPLE_FAULTS
    root_cause_name = ""  # can only be get after init

    def __init__(self, sub_faults: list[TaskBase], scenario_name: str, **kwargs):
        super().__init__()
        self.sub_faults = sub_faults
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.root_cause_name = [f.root_cause_name for f in sub_faults]
        self.faulty_devices = []
        for sub_fault in self.sub_faults:
            if isinstance(sub_fault.faulty_devices, list):
                self.faulty_devices.extend(sub_fault.faulty_devices)
            else:
                self.faulty_devices.append(sub_fault.faulty_devices)

    async def _inject_fault_async(self):
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(None, fault.inject_fault) for fault in self.sub_faults]
        await asyncio.gather(*tasks)

    async def _recover_fault_async(self):
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(None, fault.recover_fault) for fault in self.sub_faults]
        await asyncio.gather(*tasks)

    def inject_fault(self):
        asyncio.run(self._inject_fault_async())

    def recover_fault(self):
        asyncio.run(self._recover_fault_async())


class MultiFaultDetection(MultiFaultBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=MultiFaultBase.root_cause_category,
        root_cause_name=MultiFaultBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class MultiFaultLocalization(MultiFaultBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=MultiFaultBase.root_cause_category,
        root_cause_name=MultiFaultBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class MultiFaultRCA(MultiFaultBase, RCATask):
    META = ProblemMeta(
        root_cause_category=MultiFaultBase.root_cause_category,
        root_cause_name=MultiFaultBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

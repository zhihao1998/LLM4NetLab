import logging
import os
import random

import polars as pl

from llm4netlab.net_env.net_env_pool import get_net_env_instance
from scripts.step1_net_env_start import start_net_env
from scripts.step2_failure_inject import inject_failure
from scripts.step3_agent_run import start_agent
from scripts.step4_result_eval import eval_results

cur_dir = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger("BenchmarkRunner")
logging.basicConfig(level=logging.INFO)


def run_benchmark():
    """Run benchmark tests based on the benchmark.csv file."""
    benchmark_file = os.path.join(cur_dir, "benchmark.csv")
    df = pl.read_csv(benchmark_file)
    df = df.filter(pl.col("topo_size").is_in(["-", "s"]))[1:2]

    for row in df.iter_rows(named=True):
        problem = row["problem"]
        scenario = row["scenario"]
        topo_size = row["topo_size"]
        logger.info(f"Running benchmark: Problem={problem}, Scenario={scenario}, Topo Size={topo_size}")
        # Start the scenario and inject failure only once per (problem and scenario)
        is_scenario_started = False
        is_failure_injected = False

        # set random seed per problem-scenario to select the consistent failure point
        random.seed(f"{problem}-{scenario}")

        for task_level in ["localization"]:
            if not is_scenario_started:
                # Step 1: Start Network Environment
                start_net_env(scenario, topo_size=topo_size, redeploy=True)
                is_scenario_started = True
            else:
                start_net_env(scenario, topo_size=topo_size, redeploy=False)

            if not is_failure_injected:
                # Step 2: Inject Failure
                inject_failure(problem_names=[problem])
                is_failure_injected = True
            else:
                inject_failure(problem_names=[problem], re_inject=False)

            # Step 3: Start Agent
            start_agent(agent_type="react", backend_model="gpt-oss:20b", max_steps=20)

            # Step 4: Evaluate Results
            eval_results(judge_model="qwen3:32b", destroy_env=False)

        # Finally, destroy the network environment if it was started
        net_env = get_net_env_instance(scenario, topo_size=topo_size)
        if net_env.lab_exists():
            net_env.undeploy()
        break


if __name__ == "__main__":
    run_benchmark()

import os
import random

import polars as pl

from llm4netlab.net_env.net_env_pool import get_net_env_instance
from scripts.step1_net_env_start import start_net_env
from scripts.step2_failure_inject import inject_failure
from scripts.step3_agent_run import start_agent
from scripts.step4_result_eval import eval_results

cur_dir = os.path.dirname(os.path.abspath(__file__))


def run_benchmark():
    """Run benchmark tests based on the benchmark.csv file."""
    benchmark_file = os.path.join(cur_dir, "benchmark.csv")
    df = pl.read_csv(benchmark_file)

    for row in df.iter_rows(named=True):
        problem = row["problem"]
        scenario = row["scenario"]
        topo_size = row["topo_size"]
        # increase topo_size
        if topo_size == "s":
            topo_size = "l"
        elif topo_size == "-":
            continue

        # Start the scenario and inject failure only once per (problem and scenario)
        is_scenario_started = False
        is_failure_injected = False

        # set random seed per problem-scenario to select the consistent failure point
        random.seed(f"{problem}-{scenario}")

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
        start_agent(
            # gpt-oss:20b, gpt-5-mini, qwen3:32b
            agent_type="react",
            backend_model="gpt-5-mini",
            max_steps=40,
        )  # here a tool calling is also a step so we need to *2

        # Step 4: Evaluate Results
        eval_results(judge_model="qwen3:32b", destroy_env=False)

        # Finally, destroy the network environment if it was started
        net_env = get_net_env_instance(scenario, topo_size=topo_size)
        if net_env.lab_exists():
            net_env.undeploy()


if __name__ == "__main__":
    run_benchmark()

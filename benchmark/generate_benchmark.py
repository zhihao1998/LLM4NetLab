import os

from llm4netlab.net_env.net_env_pool import list_all_net_envs
from llm4netlab.orchestrator.problems.prob_pool import list_avail_problem_instances

cur_path = os.path.dirname(os.path.abspath(__file__))


def generate_benchmark():
    net_envs = list_all_net_envs()
    problem_instances = list_avail_problem_instances()
    benchmark_file = open("benchmark/benchmark.csv", "w")
    benchmark_file.write("problem,scenario,topo_size\n")
    for prob_name, prob_task_levels in problem_instances.items():
        for net_env_name, net_env_cls in net_envs.items():
            problem_instance = prob_task_levels["detection"]
            # all tags are in the network environment class
            if not set(problem_instance.TAGS).issubset(set(net_env_cls.TAGS)):
                continue
            if net_env_cls.TOPO_SIZE is None:
                topo_size = ["-"]
            else:
                topo_size = net_env_cls.TOPO_SIZE
            for size in topo_size:
                benchmark_file.write(f"{prob_name},{net_env_name},{size}\n")
    benchmark_file.close()


if __name__ == "__main__":
    generate_benchmark()

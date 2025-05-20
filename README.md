# Problems

1. python environments of mininet and agent is not the same one
 

# Requirements

1. Network env: p4-utils, pyzmq

# Usage


1. Start Mininet
```shell
sudo python3 /home/p4/AI4NetOps/ai4netops/net_env/mininet/topo/p4/01-l2-basic-forwarding/network.py
```

2. Start some script
```shell
poetry run python3 /home/p4/AI4NetOps/ai4netops/orchestrator/problems/simple_link_failure/simple_link_failure.py
```
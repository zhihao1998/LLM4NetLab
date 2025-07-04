import asyncio

from agent.react import ReactAgent
from llm4netlab.orchestrator.orchestrator import Orchestrator

# 1. Define orchestrator and agent
orchestrator = Orchestrator()
agent = ReactAgent()
orchestrator.register_agent(agent, "react")

# 2. Initialize the problem
# Find more problems under `llm4netlab/orchestrator/problems`
task_desc, instructions, actions = orchestrator.init_problem("packet_loss_detection")
print("Task description:", task_desc)
print("Instructions:", instructions)
print("Actions:", actions)

# 3. Initialize the agent context with task description, instructions, and actions
agent.init_context(task_desc, instructions, actions)
print("Agent context initialized.")

# 4. Start the problem with a maximum number of steps
asyncio.run(orchestrator.start_problem(max_steps=30))

# 5. Stop the problem and clean the environments after completion
orchestrator.stop_problem()

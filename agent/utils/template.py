# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""prompt templates to share API documentation and instructions with clients"""

# standard documentation and apis template

DOCS = """{prob_desc}
You are provided with the following APIs to interact with the network:


{discovery_apis}


Finally, you will submit your solution for this task using the following API:


{submit_api}


At each turn think step-by-step and respond with:
Thought: <your thought>
Action: <your action>
"""


RESP_INSTR = """DO NOT REPEAT ACTIONS! Respond with:
Thought: <your thought on the previous output>
Action: <your action towards mitigating>
"""

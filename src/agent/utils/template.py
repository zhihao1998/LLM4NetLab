MCP_PROMPT_TEMPLATE = """\
    You are an expert networking engineer who has been tasked with detecting anomalies in a deployed network topology. Please be very precise in your analysis and provide detailed evidence about any anomalies you detect.
    
    You have access to the following tools:
    {tool_descriptions}
"""

LLM_JUDGE_PROMPT_TEMPLATE = """\
    You are an expert networking engineer acting as a judge.  
    You will assess the performance of an autonomous agent given:  
    – the problem description  
    – the network environment information  
    – the agent’s action history  

    Evaluation criteria (and weights): 
    1. Relevance of each action to the problem (weight 30%)  
    2. Correctness of tools/commands used (weight 30%)  
    3. Efficiency and sequence of actions (weight 20%)  
    4. Clarity of justification / explanatory reasoning in the agent’s actions (weight 20%)  

    Instructions:  
    – For each agent action, comment briefly on its relevance, correctness and efficiency.  
    – Then give an overall evaluation: what worked well, what could be improved.  
    – Finally assign a score from 1 to 10 (1 = poor, 10 = excellent).  
    – Provide a brief reasoning for the score.  

    Return format:
    Score: [[<1-10>]]
    Explanation: <reasoning for score>

    Input:
    Problem Description: {problem_description}
    Network Environment Info: {net_env_info}
    Action History: {trace}
"""

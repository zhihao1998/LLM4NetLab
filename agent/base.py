from typing import List

from pydantic import BaseModel, Field

from agent.utils.template import DOCS, RESP_INSTR


class Character(BaseModel):
    name: str
    age: int
    fact: List[str] = Field(..., description="A list of facts about the character")


class AgentBase:
    def __init__(self):
        self.history = []
        self.llm = None

    def init_context(self, problem_desc: str, instructions: str, apis: str):
        """Initialize the context for the agent."""

        self.submit_api = self._filter_dict(apis, lambda k, _: "submit" in k)
        self.discovery_apis = self._filter_dict(apis, lambda k, _: "submit" not in k)

        def stringify_apis(apis):
            return "\n\n".join([f"{k}\n{v}" for k, v in apis.items()])

        self.system_message = DOCS.format(
            prob_desc=problem_desc,
            discovery_apis=stringify_apis(self.discovery_apis),
            submit_api=stringify_apis(self.submit_api),
        )

        self.task_message = instructions

        self.history.append({"role": "system", "content": self.system_message})
        self.history.append({"role": "user", "content": self.task_message})

    async def get_action(self, input, trace_id) -> str:
        """Wrapper to interface the agent with OpsBench.

        Args:
            input (str): The input from the orchestrator/environment.

        Returns:
            str: The response from the agent.
        """
        self.history.append({"role": "user", "content": self._add_instr(input)})
        response = self.llm.run(self.history)
        self.history.append({"role": "assistant", "content": response[0]})
        return response[0]

    def _filter_dict(self, dictionary, filter_func):
        return {k: v for k, v in dictionary.items() if filter_func(k, v)}

    def _add_instr(self, input):
        return input + "\n\n" + RESP_INSTR


# client = instructor.from_openai(
#     OpenAI(
#         base_url=config.LLM_API_URL,
#         api_key="ollama",  # required, but unused
#     ),
#     mode=instructor.Mode.JSON,
# )

# resp = client.chat.completions.create(
#     model="deepseek-r1:1.5b",
#     messages=[
#         {
#             "role": "user",
#             "content": "how old is Joh biden?",
#         }
#     ],
#     response_model=Character,
# )
# print(resp.model_dump_json(indent=2))

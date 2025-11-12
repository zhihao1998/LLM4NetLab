class AgentBase:
    def __init__(self):
        self.agent = None
        self.agent_name = None
        self.backend_model = None  # LLM backend model name

    async def arun(self) -> str:
        """
        Asynchronous run method to be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def run(self) -> str:
        """
        Synchronous run method to be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

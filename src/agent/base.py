class AgentBase:
    def __init__(self):
        self.name = None
        self.agent = None

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

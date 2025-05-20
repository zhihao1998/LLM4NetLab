class Task:
    """Base class for all tasks."""

    def __init__(self):
        self.results = {}

    def get_task_description(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def get_instructions(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def get_available_actions(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def perform_action(self, action_name, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")

    def add_result(self, key, value):
        """Add an evaluation result to the task."""
        self.results[key] = value

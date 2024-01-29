from src.observer.Event import Event


class PercentChangedEvent(Event):
    event_name = "Percent_Changed"

    def __init__(self, task_name: str, current_percent: float):
        super().__init__()
        self.task_name = task_name
        self.current_percent = current_percent

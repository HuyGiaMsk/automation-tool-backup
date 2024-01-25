from abc import ABC, abstractmethod


class Percentage(ABC):

    def __init__(self):
        super().__init__()
        self.total_element_size: int = 0
        self.current_element_index: int = 0

    @abstractmethod
    def get_current_percent(self) -> float:
        pass

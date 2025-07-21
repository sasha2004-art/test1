from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def generate_quest(self, setting_text: str) -> dict:
        pass

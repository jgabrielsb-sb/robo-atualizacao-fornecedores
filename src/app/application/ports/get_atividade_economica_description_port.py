from abc import ABC, abstractmethod

class GetAtividadeEconomicaDescriptionPort(ABC):
    @abstractmethod
    def get(self, code: str) -> str:
        raise NotImplementedError

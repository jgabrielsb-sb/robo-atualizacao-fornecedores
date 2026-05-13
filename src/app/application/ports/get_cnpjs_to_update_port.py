from abc import ABC, abstractmethod
from app.domain.value_objects import CNPJ


class GetCNPJsToUpdatePort(ABC):
    @abstractmethod
    def get(self) -> list[CNPJ]:
        pass

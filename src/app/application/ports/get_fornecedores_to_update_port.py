from abc import ABC, abstractmethod

from app.domain.entities import Fornecedor


class GetFornecedoresToUpdatePort(ABC):
    @abstractmethod
    def get(self) -> list[Fornecedor]:
        pass

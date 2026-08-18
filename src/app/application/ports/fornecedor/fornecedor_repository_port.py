from abc import ABC, abstractmethod
from typing import Any
from app.domain.entities import Fornecedor


class FornecedorRepositoryPort(ABC):
    @abstractmethod
    def create(self, fornecedor: Fornecedor) -> Any:
        pass

    @abstractmethod
    def update(self, fornecedor: Fornecedor) -> Any:
        pass

from abc import ABC, abstractmethod
from typing import Any
from .models import FornecedorToUpdate

class FornecedorToUpdateRepositoryPort(ABC):
    @abstractmethod
    def save(self, fornecedor: FornecedorToUpdate) -> Any:
        pass
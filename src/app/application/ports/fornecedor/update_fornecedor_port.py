from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities import Fornecedor


class UpdateFornecedorPort(ABC):
    @abstractmethod
    def update(self, fornecedor: Fornecedor) -> Any:
        pass

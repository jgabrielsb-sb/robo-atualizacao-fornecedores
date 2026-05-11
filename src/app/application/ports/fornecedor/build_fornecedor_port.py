from abc import ABC, abstractmethod
from pydantic import BaseModel
from app.domain.entities import Fornecedor

from app.application.ports import FornecedorToUpdate


class BuildFornecedorPort(ABC):
    @abstractmethod
    def build(self, fornecedor_to_update: FornecedorToUpdate) -> Fornecedor:
        pass

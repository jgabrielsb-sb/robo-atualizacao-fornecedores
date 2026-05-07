from abc import ABC, abstractmethod
from pydantic import BaseModel
from app.domain.entities import Fornecedor


class BuildFornecedorInput(BaseModel):
    id: int


class BuildFornecedorPort(ABC):
    @abstractmethod
    def build(self, input: BuildFornecedorInput) -> Fornecedor:
        pass

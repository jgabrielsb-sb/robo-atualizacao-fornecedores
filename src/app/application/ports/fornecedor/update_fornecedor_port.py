from abc import ABC, abstractmethod

from app.domain.entities import Fornecedor
from pydantic import BaseModel

class UpdateFornecedorResult(BaseModel):
    input: dict
    output: dict


class UpdateFornecedorPort(ABC):
    @abstractmethod
    def update(self, fornecedor: Fornecedor) -> UpdateFornecedorResult:
        pass

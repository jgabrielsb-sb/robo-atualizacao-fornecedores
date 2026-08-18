from abc import ABC, abstractmethod
from app.domain.entities import Fornecedor
from app.domain.value_objects import CNPJ


class BuildFornecedorPort(ABC):
    @abstractmethod
    def build(self, cnpj: CNPJ) -> Fornecedor:
        pass

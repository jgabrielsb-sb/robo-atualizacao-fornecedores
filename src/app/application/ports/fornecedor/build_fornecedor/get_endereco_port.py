from abc import ABC, abstractmethod
from app.domain.value_objects import CNPJ, Endereco

class GetEnderecoPort(ABC):
    @abstractmethod
    def get(self, cnpj: CNPJ) -> Endereco:
        pass

    
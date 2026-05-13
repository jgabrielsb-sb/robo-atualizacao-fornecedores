from abc import ABC, abstractmethod

from app.domain.value_objects import CartaoCNPJ
from app.domain.value_objects import CNPJ

class GetCartaoCNPJPort(ABC):
    @abstractmethod
    def get(self, cnpj: CNPJ) -> CartaoCNPJ:
        pass
from abc import ABC, abstractmethod

from app.domain.value_objects import CartaoCNPJ

class GetCartaoCNPJPort(ABC):
    @abstractmethod
    def get(self, cnpj: str) -> CartaoCNPJ:
        pass
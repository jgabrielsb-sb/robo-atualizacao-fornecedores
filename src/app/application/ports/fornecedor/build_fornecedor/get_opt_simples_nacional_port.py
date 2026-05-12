from abc import ABC, abstractmethod

from app.domain.value_objects import CNPJ

class GetOptSimplesNacionalPort(ABC):
    @abstractmethod
    def get(self, cnpj: CNPJ) -> bool:
        pass


from pydantic import BaseModel
from abc import ABC, abstractmethod

from app.domain.value_objects import CNPJ
from .models import FornecedorToUpdate

class GetFornecedoresToUpdatePort(ABC):
    @abstractmethod
    def get(self) -> list[FornecedorToUpdate]:
        pass



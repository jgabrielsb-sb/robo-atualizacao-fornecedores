from abc import ABC, abstractmethod
from app.domain.value_objects import Municipio

class MunicipioLookupPort(ABC):
    @abstractmethod
    def get(self, municipio_name: str) -> Municipio:
        raise NotImplementedError
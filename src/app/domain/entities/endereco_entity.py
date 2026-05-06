from dataclasses import dataclass

from app.domain.value_objects import CEP
from .municipio_entity import Municipio


@dataclass
class Endereco:
    endereco: str
    numero: str
    complemento: str
    cep: CEP
    municipio: Municipio
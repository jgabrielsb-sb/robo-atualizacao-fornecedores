from dataclasses import dataclass

from .cep_value_object import CEP
from .municipio_value_object import Municipio


@dataclass(frozen=True)
class Endereco:
    endereco: str
    numero: str
    complemento: str
    cep: CEP
    municipio: Municipio

    def __post_init__(self):
        if not isinstance(self.endereco, str):
            raise TypeError("endereco must be a string")
        if not isinstance(self.numero, str):
            raise TypeError("numero must be a string")
        if not isinstance(self.complemento, str):
            raise TypeError("complemento must be a string")
        if not isinstance(self.cep, CEP):
            raise TypeError("cep must be a CEP")
        if not isinstance(self.municipio, Municipio):
            raise TypeError("municipio must be a Municipio")

    @classmethod
    def create(
        cls,
        *,
        endereco: str,
        numero: str,
        complemento: str,
        cep: CEP,
        municipio: Municipio,
    ) -> 'Endereco':
        return cls(
            endereco=endereco,
            numero=numero,
            complemento=complemento,
            cep=cep,
            municipio=municipio
        )
        

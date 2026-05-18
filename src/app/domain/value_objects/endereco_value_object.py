from dataclasses import dataclass
from typing import Optional

from .cep_value_object import CEP
from .municipio_value_object import Municipio


@dataclass(frozen=True)
class Endereco:
    endereco: Optional[str] = None
    numero: Optional[str] = None
    bairro: Optional[str] = None
    cep: Optional[CEP] = None
    municipio: Optional[Municipio] = None
    complemento: Optional[str] = None
    uf: Optional[str] = None

    def __post_init__(self):
        if self.endereco and not isinstance(self.endereco, str):
            raise TypeError("endereco must be a string")
        if self.numero and not isinstance(self.numero, str):
            raise TypeError("numero must be a string")
        if self.bairro and not isinstance(self.bairro, str):
            raise TypeError("bairro must be a string")
        if self.complemento and not isinstance(self.complemento, str):
            raise TypeError("complemento must be a string")
        if self.uf and not isinstance(self.uf, str):
            raise TypeError("uf must be a string")
        if self.cep and not isinstance(self.cep, CEP):
            raise TypeError("cep must be a CEP")
        if self.municipio and not isinstance(self.municipio, Municipio):
            raise TypeError("municipio must be a Municipio")

    @classmethod
    def create(
        cls,
        *,
        endereco: Optional[str] = None,
        numero: Optional[str] = None,
        bairro: Optional[str] = None,
        complemento: Optional[str] = None,
        cep: Optional[CEP] = None,
        municipio: Optional[Municipio] = None,
        uf: Optional[str] = None,
    ) -> 'Endereco':
        return cls(
            endereco=endereco,
            numero=numero,
            bairro=bairro,
            complemento=complemento,
            cep=cep,
            municipio=municipio,
            uf=uf,
        )
        

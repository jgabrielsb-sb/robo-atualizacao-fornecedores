from dataclasses import dataclass

from .codigo_municipio_ibge import CodigoMunicipioIBGE


class InvalidMunicipioError(Exception):
    pass


@dataclass
class Municipio:
    nome: str
    codigo_ibge: CodigoMunicipioIBGE

    def __post_init__(self):
        if not isinstance(self.nome, str):
            raise TypeError("nome must be a string")
        if not isinstance(self.codigo_ibge, CodigoMunicipioIBGE):
            raise TypeError("codigo_ibge must be a CodigoMunicipioIBGE")

    @classmethod
    def create(
        cls,
        *,
        nome: str,
        codigo_ibge: CodigoMunicipioIBGE,
    ) -> 'Municipio':
        return cls(nome=nome, codigo_ibge=codigo_ibge)
        

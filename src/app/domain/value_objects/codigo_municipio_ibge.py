import re
from dataclasses import dataclass


class InvalidCodigoMunicipioIBGEError(Exception):
    pass


class InvalidCodigoMunicipioIBGECodeLengthError(InvalidCodigoMunicipioIBGEError):
    def __init__(self, length: int):
        self.length = length

    def __str__(self) -> str:
        return f"Codigo municipio IBGE length must be 7 digits, but got {self.length}"


@dataclass
class CodigoMunicipioIBGE:
    value: str

    @classmethod
    def create(cls, ibge_code: str) -> 'CodigoMunicipioIBGE':
        digits = re.sub(r'\D', '', ibge_code)
        if len(digits) != 7:
            raise InvalidCodigoMunicipioIBGECodeLengthError(len(digits))
        return cls(value=ibge_code)

import unicodedata
from enum import Enum
from typing import Union


class InvalidPorteError(Exception):
    pass


def _normalize(s: str) -> str:
    result = unicodedata.normalize("NFD", s.upper().strip())
    return "".join(c for c in result if unicodedata.category(c) != "Mn")


class PorteEnum(Enum):
    EIRELI = "EMPRESA INDIVIDUAL DE RESPONSABILIDADE LIMITADA"
    EP = "EMPRESA PUBLICA"
    EPP = "EMPRESA DE PEQUENO PORTE"
    ME = "MICRO EMPRESA"
    MEI = "MICROEMPREENDEDOR INDIVIDUAL"
    N = "NORMAL"
    PF = "PESSOA FISICA"
    SFL = "SEM FINS LUCRATIVOS"
    D = "DEMAIS"

    @classmethod
    def from_value(cls, value: Union[str, 'PorteEnum']) -> "PorteEnum":
        if isinstance(value, PorteEnum):
            return value

        if not isinstance(value, str):
            raise TypeError("value must be a string")

        normalized_input = _normalize(value)

        for member in cls:
            if _normalize(member.value) == normalized_input:
                return member

        raise InvalidPorteError(
            f"Invalid Porte: {value}. Valid values: {cls.__members__}"
        )

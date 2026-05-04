import unicodedata
from enum import Enum
from typing import Union


class InvalidVinculoSebraeError(Exception):
    pass


def _normalize(s: str) -> str:
    result = unicodedata.normalize("NFD", s.upper().strip())
    return "".join(c for c in result if unicodedata.category(c) != "Mn")


class VinculoSebraeEnum(Enum):
    C = "CONSELHEIRO"
    D = "DIRETOR"
    F = "FUNCIONARIO"
    G = "GERENTE"
    E = "ESTAGIARIO"
    Z = "SEM VINCULO"

    @classmethod
    def from_value(cls, value: Union[str, 'VinculoSebraeEnum']) -> "VinculoSebraeEnum":
        if isinstance(value, VinculoSebraeEnum):
            return value

        if not isinstance(value, str):
            raise TypeError("value must be a string")

        normalized_input = _normalize(value)

        for member in cls:
            if _normalize(member.value) == normalized_input:
                return member

        raise InvalidVinculoSebraeError(
            f"Invalid VinculoSebrae: {value}. Valid values: {cls.__members__}"
        )

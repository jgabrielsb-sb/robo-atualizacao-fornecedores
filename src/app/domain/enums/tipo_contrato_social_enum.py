import unicodedata
from enum import Enum

from typing import Union

class InvalidTipoContratoSocialError(Exception):
    pass


def _normalize(s: str) -> str:
    result = unicodedata.normalize("NFD", s.upper().strip())
    return "".join(c for c in result if unicodedata.category(c) != "Mn")


class TipoContratoSocialEnum(Enum):
    J = "JURIDICO"
    F = "PESSOA FISICA"
    L = "FAMILIAR"

    @classmethod
    def from_value(cls, value: Union[str, 'TipoContratoSocialEnum']) -> "TipoContratoSocialEnum":
        if isinstance(value, TipoContratoSocialEnum):
            return value

        if not isinstance(value, str):
            raise TypeError("value must be a string")

        normalized_input = _normalize(value)

        for member in cls:
            if _normalize(member.value) == normalized_input:
                return member

        raise InvalidTipoContratoSocialError(
            f"Invalid TipoContratoSocial: {value}. Valid values: {cls.__members__}"
        )

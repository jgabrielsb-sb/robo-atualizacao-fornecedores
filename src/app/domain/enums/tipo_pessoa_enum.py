import unicodedata
from enum import Enum

from typing import Union

class InvalidTipoPessoaError(Exception):
    pass


def _normalize(s: str) -> str:
    result = unicodedata.normalize("NFD", s.upper().strip())
    return "".join(c for c in result if unicodedata.category(c) != "Mn")


class TipoPessoaEnum(Enum):
    CI = "COMERCIO/INDUSTRIA"
    PF = "PESSOA FISICA"
    OS = "PRESTAÇAO DE SERVIÇO"

    @classmethod
    def from_value(cls, value: Union[str, 'TipoPessoaEnum']) -> "TipoPessoaEnum":
        if isinstance(value, TipoPessoaEnum):
            return value

        if not isinstance(value, str):
            raise TypeError("value must be a string")

        normalized_input = _normalize(value)

        for member in cls:
            if _normalize(member.value) == normalized_input:
                return member

        raise InvalidTipoPessoaError(
            f"Invalid TipoPessoa: {value}. Valid values: {cls.__members__}"
        )

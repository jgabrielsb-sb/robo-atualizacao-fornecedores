from enum import Enum
import unicodedata

from typing import Union

class InvalidSituacaoCadastralError(Exception):
    pass

def _normalize(s: str) -> str:
    result = unicodedata.normalize("NFD", s.upper().strip())
    return "".join(c for c in result if unicodedata.category(c) != "Mn")

class SituacaoCadastralEnum(Enum):
    ATIVA = "ATIVA"
    INAPTA = "INAPTA"
    SUSPENSA = "SUSPENSA"
    BAIXADA = "BAIXADA"

    @classmethod
    def from_value(cls, value: Union[str, 'SituacaoCadastralEnum']) -> 'SituacaoCadastralEnum':
        if isinstance(value, SituacaoCadastralEnum):
            return value

        if not isinstance(value, str):
            raise TypeError("value must be a string")

        normalized_input = _normalize(value)

        for member in cls:
            if _normalize(member.value) == normalized_input:
                return member

        raise InvalidSituacaoCadastralError(
            f"Invalid SituacaoCadastral: {value}. Valid values: {cls.__members__}"
        )
import unicodedata

from enum import Enum
from typing import Union


class InvalidFederacaoError(Exception):
    pass

class FederacaoEnum(Enum):
    NAO = "NAO"
    FEDERACAO = "FEDERACAO"
    CONFEDERACAO = "CONFEDERACAO"

    @classmethod
    def from_value(cls, value: Union[str, 'FederacaoEnum']) -> "FederacaoEnum":
        if isinstance(value, FederacaoEnum):
            return value

        if not isinstance(value, str):
            raise TypeError("value must be a string")

        normalized = unicodedata.normalize("NFD", value.upper().strip())
        normalized = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

        for member in cls:
            if member.value == normalized:
                return member

        raise InvalidFederacaoError(
            f"Invalid Federacao: --{value}--. Valid values: {cls.__members__}"
        )



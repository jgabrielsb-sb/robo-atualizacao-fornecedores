import re
from dataclasses import dataclass


class InvalidCNPJLengthError(Exception):
    def __init__(self, length: int):
        if not isinstance(length, int):
            raise TypeError('length must be an integer')
        self.length = length

    def __str__(self) -> str:
        return f"CNPJ length must be 14 digits, but got {self.length}"


@dataclass
class CNPJ:
    value: str
    formatted: str = ""

    def __post_init__(self):
        self.value = re.sub(r'\D', '', self.value)

    @classmethod
    def create(cls, cnpj: str) -> 'CNPJ':
        digits = re.sub(r'\D', '', cnpj)
        if len(digits) != 14:
            raise InvalidCNPJLengthError(len(digits))
        formatted = f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
        return cls(value=digits, formatted=formatted)

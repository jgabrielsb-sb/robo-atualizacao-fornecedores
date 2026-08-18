import re
from dataclasses import dataclass


class InvalidCPFError(Exception):
    pass


class InvalidCPFLengthError(InvalidCPFError):
    def __init__(self, length: int):
        if not isinstance(length, int):
            raise TypeError("length must be an integer")
        self.length = length

    def __str__(self) -> str:
        return f"CPF length must be 11 digits, but got {self.length}"


@dataclass
class CPF:
    value: str
    formatted: str = ""

    def __post_init__(self):
        self.value = re.sub(r"\D", "", self.value)

    @classmethod
    def create(cls, cpf: str) -> "CPF":
        digits = re.sub(r"\D", "", cpf)

        if len(digits) != 11:
            raise InvalidCPFLengthError(len(digits))

        formatted = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

        return cls(value=digits, formatted=formatted)
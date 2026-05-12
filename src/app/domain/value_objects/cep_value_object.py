import re
from dataclasses import dataclass, field


class InvalidCEPError(Exception):
    pass


class InvalidCEPLengthError(InvalidCEPError):
    def __init__(self, length: int):
        self.length = length

    def __str__(self) -> str:
        return f"CEP length must be 8 digits, but got {self.length}"


@dataclass
class CEP:
    value: str
    formatted: str = field(default="", compare=False)

    def __post_init__(self):
        self.value = re.sub(r'\D', '', self.value)

    @classmethod
    def create(cls, cep: str) -> 'CEP':
        digits = re.sub(r'\D', '', cep)
        if len(digits) != 8:
            raise InvalidCEPLengthError(len(digits))
        formatted = f"{digits[:5]}-{digits[5:]}"
        return cls(value=digits, formatted=formatted)

    

    

import re
from dataclasses import dataclass

from .ddd_value_object import DDD

class InvalidTelefoneError(ValueError):
    pass


@dataclass(frozen=True)
class Telefone:
    ddd: DDD
    numero: str

    @classmethod
    def create(cls, value: str) -> "Telefone":
        if not isinstance(value, str):
            raise TypeError("Telefone value must be a string")

        digits = re.sub(r"\D", "", value)

        # Remove Brazilian country code if present.
        if digits.startswith("55") and len(digits) in {12, 13}:
            digits = digits[2:]

        if len(digits) not in {10, 11}:
            raise InvalidTelefoneError(
                "Brazilian phone number must have 10 or 11 digits including DDD"
            )

        ddd = DDD.from_value(digits[:2])
        numero = digits[2:]

        if len(numero) == 9:
            # Common mobile format: 9XXXX-XXXX
            if not numero.startswith("9"):
                raise InvalidTelefoneError(
                    "Brazilian mobile phone number must start with 9"
                )
        return cls(ddd=ddd, numero=numero)

    @property
    def digits(self) -> str:
        return f"{self.ddd}{self.numero}"

    @property
    def formatted(self) -> str:
        if len(self.numero) == 9:
            return f"({self.ddd}) {self.numero[:5]}-{self.numero[5:]}"
        return f"({self.ddd}) {self.numero[:4]}-{self.numero[4:]}"

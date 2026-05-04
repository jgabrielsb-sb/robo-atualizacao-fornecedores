from dataclasses import dataclass


class InvalidDDDError(Exception):
    pass


class InvalidDDDLengthError(InvalidDDDError):
    def __init__(self, length: int):
        self.length = length

    def __str__(self) -> str:
        return f"DDD must have 2 digits, but got {self.length}"


@dataclass
class DDD:
    value: str

    @classmethod
    def from_value(cls, value: str) -> 'DDD':
        if not isinstance(value, str):
            raise TypeError("value must be a string")

        stripped = value.strip()

        try:
            canonical = str(int(stripped))
        except (ValueError, TypeError):
            raise InvalidDDDLengthError(0)

        if len(canonical) != 2:
            raise InvalidDDDLengthError(len(canonical))

        return cls(value=value)

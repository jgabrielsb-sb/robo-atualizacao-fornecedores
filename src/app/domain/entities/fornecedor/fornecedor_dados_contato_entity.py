from dataclasses import dataclass, field
from typing import Optional

from app.domain.value_objects import DDD


class InvalidFornecedorDadosContatoError(Exception):
    pass


@dataclass(frozen=True)
class FornecedorDadosContato:
    ddd: Optional[DDD] = field(default=None)

    def __post_init__(self):
        if self.ddd is not None and not isinstance(self.ddd, DDD):
            raise TypeError("ddd must be a DDD")

    @classmethod
    def create(
        cls,
        *,
        ddd: str | DDD | None = None,
    ) -> 'FornecedorDadosContato':
        resolved = None if ddd is None else (ddd if isinstance(ddd, DDD) else DDD.from_value(ddd))
        return cls(ddd=resolved)

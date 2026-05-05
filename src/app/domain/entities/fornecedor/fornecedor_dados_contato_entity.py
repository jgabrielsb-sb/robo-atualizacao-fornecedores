from dataclasses import dataclass

from app.domain.value_objects import DDD


class InvalidFornecedorDadosContatoError(Exception):
    pass


@dataclass(frozen=True)
class FornecedorDadosContato:
    ddd: DDD

    def __post_init__(self):
        if not isinstance(self.ddd, DDD):
            raise TypeError("ddd must be a DDD")

    @classmethod
    def create(
        cls,
        *,
        ddd: str | DDD,
    ) -> 'FornecedorDadosContato':
        resolved = ddd if isinstance(ddd, DDD) else DDD.from_value(ddd)
        return cls(ddd=resolved)

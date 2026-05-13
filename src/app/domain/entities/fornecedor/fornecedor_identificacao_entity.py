from dataclasses import dataclass
from typing import Optional

from app.domain.value_objects import CNPJ


class InvalidFornecedorIdentificacaoError(Exception):
    pass


@dataclass(frozen=True)
class FornecedorIdentificacao:
    cnpj: CNPJ
    razao_social: str
    nome_fantasia: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.cnpj, CNPJ):
            raise TypeError("cnpj must be a CNPJ")
        if not isinstance(self.razao_social, str):
            raise TypeError("razao_social must be a string")
        if self.nome_fantasia and not isinstance(self.nome_fantasia, str):
            raise TypeError("nome_fantasia must be a string")

    @classmethod
    def create(
        cls,
        *,
        cnpj: str,
        razao_social: str,
        nome_fantasia: Optional[str] = None,
    ) -> 'FornecedorIdentificacao':
        return cls(
            cnpj=CNPJ.create(cnpj),
            razao_social=razao_social,
            nome_fantasia=nome_fantasia,
        )

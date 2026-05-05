from dataclasses import dataclass

from app.domain.enums import (
    FederacaoEnum,
    PorteEnum,
    TipoPessoaEnum,
    VinculoSebraeEnum,
)
from app.domain.value_objects import SituacaoCadastral


class InvalidFornecedorDadosCadastraisError(Exception):
    pass


@dataclass(frozen=True)
class FornecedorDadosCadastrais:
    porte: PorteEnum
    opt_simples_nacional: bool
    situacao_cadastral: SituacaoCadastral
    tipo_pessoa: TipoPessoaEnum
    vinculo_sebrae: VinculoSebraeEnum
    federacao: FederacaoEnum
    cooperativa: bool
    codigo_retencao: str

    def __post_init__(self):
        if not isinstance(self.porte, PorteEnum):
            raise TypeError("porte must be a PorteEnum")
        if not isinstance(self.opt_simples_nacional, bool):
            raise TypeError("opt_simples_nacional must be a bool")
        if not isinstance(self.situacao_cadastral, SituacaoCadastral):
            raise TypeError("situacao_cadastral must be a SituacaoCadastral")
        if not isinstance(self.tipo_pessoa, TipoPessoaEnum):
            raise TypeError("tipo_pessoa must be a TipoPessoaEnum")
        if not isinstance(self.vinculo_sebrae, VinculoSebraeEnum):
            raise TypeError("vinculo_sebrae must be a VinculoSebraeEnum")
        if not isinstance(self.federacao, FederacaoEnum):
            raise TypeError("federacao must be a FederacaoEnum")
        if not isinstance(self.cooperativa, bool):
            raise TypeError("cooperativa must be a bool")
        if not isinstance(self.codigo_retencao, str):
            raise TypeError("codigo_retencao must be a str")

    @classmethod
    def create(
        cls,
        *,
        porte: str | PorteEnum,
        opt_simples_nacional: bool,
        situacao_cadastral: SituacaoCadastral,
        tipo_pessoa: str | TipoPessoaEnum,
        vinculo_sebrae: str | VinculoSebraeEnum,
        federacao: str | FederacaoEnum,
        cooperativa: bool,
        codigo_retencao: str,
    ) -> 'FornecedorDadosCadastrais':
        return cls(
            porte=PorteEnum.from_value(porte),
            opt_simples_nacional=opt_simples_nacional,
            situacao_cadastral=situacao_cadastral,
            tipo_pessoa=TipoPessoaEnum.from_value(tipo_pessoa),
            vinculo_sebrae=VinculoSebraeEnum.from_value(vinculo_sebrae),
            federacao=FederacaoEnum.from_value(federacao),
            cooperativa=cooperativa,
            codigo_retencao=codigo_retencao,
        )

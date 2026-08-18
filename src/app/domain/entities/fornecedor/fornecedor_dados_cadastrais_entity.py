from dataclasses import dataclass

from app.domain.enums import (
    FederacaoEnum,
    PorteEnum,
    TipoPessoaEnum,
    VinculoSebraeEnum,
    TipoContratoSocialEnum,
)
from app.domain.enums import SituacaoCadastralEnum


class InvalidFornecedorDadosCadastraisError(Exception):
    pass


@dataclass(frozen=True)
class FornecedorDadosCadastrais:
    opt_simples_nacional: bool
    vinculo_sebrae: VinculoSebraeEnum
    federacao: FederacaoEnum
    cooperativa: bool
    codigo_retencao: str
    situacao_cadastral: SituacaoCadastralEnum | None = None
    tipo_pessoa: TipoPessoaEnum | None = None
    tipo_contrato_social: TipoContratoSocialEnum | None = None
    porte: PorteEnum | None = None

    def __post_init__(self):
        if self.porte and not isinstance(self.porte, PorteEnum):
            raise TypeError("porte must be a PorteEnum")
        if not isinstance(self.opt_simples_nacional, bool):
            raise TypeError("opt_simples_nacional must be a bool")
        if self.situacao_cadastral and not isinstance(self.situacao_cadastral, SituacaoCadastralEnum):
            raise TypeError("situacao_cadastral must be a SituacaoCadastral")
        if self.tipo_pessoa and not isinstance(self.tipo_pessoa, TipoPessoaEnum):
            raise TypeError("tipo_pessoa must be a TipoPessoaEnum")
        if self.tipo_contrato_social and not isinstance(self.tipo_contrato_social, TipoContratoSocialEnum):
            raise TypeError("tipo_contrato_social must be a TipoContratoSocialEnum")
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
        porte: PorteEnum | None,
        opt_simples_nacional: bool,
        situacao_cadastral: str | SituacaoCadastralEnum,
        tipo_pessoa: str | TipoPessoaEnum | None = None,
        vinculo_sebrae: str | VinculoSebraeEnum,
        federacao: str | FederacaoEnum,
        cooperativa: bool | None,
        codigo_retencao: str,
        tipo_contrato_social: str | TipoContratoSocialEnum | None = None,
    ) -> 'FornecedorDadosCadastrais':
        
        return cls(
            porte=PorteEnum.from_value(porte) if porte else None,
            opt_simples_nacional=opt_simples_nacional,
            situacao_cadastral=SituacaoCadastralEnum.from_value(situacao_cadastral),
            tipo_pessoa=TipoPessoaEnum.from_value(tipo_pessoa) if tipo_pessoa else None,
            vinculo_sebrae=VinculoSebraeEnum.from_value(vinculo_sebrae),
            federacao=FederacaoEnum.from_value(federacao),
            cooperativa=cooperativa if cooperativa is not None else False,
            codigo_retencao=codigo_retencao,
            tipo_contrato_social=TipoContratoSocialEnum.from_value(tipo_contrato_social) if tipo_contrato_social else None,
        )

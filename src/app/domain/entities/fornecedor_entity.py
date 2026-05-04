from dataclasses import dataclass

from app.domain.value_objects import DDD

from app.domain.enums import (
    PorteEnum, 
    SituacaoCadastralEnum, 
    TipoPessoaEnum,
    VinculoSebraeEnum,
    FederacaoEnum
)

from .endereco_entity import Endereco

@dataclass
class Fornecedor:
    opt_simples_nacional: bool
    razao_social: str
    nome_fantasia: str
    porte: PorteEnum
    endereco: Endereco
    ddd: DDD
    situacao_cadastral: SituacaoCadastralEnum
    tipo_pessoa: TipoPessoaEnum
    vinculo_sebrae: VinculoSebraeEnum
    federacao: FederacaoEnum
    cooperativa: bool
    codigo_retencao: str




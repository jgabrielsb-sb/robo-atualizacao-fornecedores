import pytest
pytestmark = pytest.mark.unit

from app.domain.entities.fornecedor.fornecedor_dados_cadastrais_entity import FornecedorDadosCadastrais
from app.domain.enums import FederacaoEnum, PorteEnum, TipoPessoaEnum, VinculoSebraeEnum, SituacaoCadastralEnum
from app.domain.value_objects import SituacaoCadastral


@pytest.fixture
def situacao_cadastral():
    return SituacaoCadastral.create(ativo=True, bloqueado=False, motivo_bloqueio=None)


def test_should_create_fornecedor_dados_cadastrais_from_strings(
    situacao_cadastral: SituacaoCadastral,
):
    dados = FornecedorDadosCadastrais.create(
        porte="EMPRESA DE PEQUENO PORTE",
        opt_simples_nacional=True,
        situacao_cadastral="ATIVA",
        tipo_pessoa="PESSOA FISICA",
        vinculo_sebrae="SEM VINCULO",
        federacao="NAO",
        cooperativa=False,
        codigo_retencao="12345",
    )
    assert dados.porte == PorteEnum.EPP
    assert dados.opt_simples_nacional is True
    assert dados.situacao_cadastral == SituacaoCadastralEnum.ATIVA
    assert dados.tipo_pessoa == TipoPessoaEnum.PF
    assert dados.vinculo_sebrae == VinculoSebraeEnum.Z
    assert dados.federacao == FederacaoEnum.NAO
    assert dados.cooperativa is False
    assert dados.codigo_retencao == "12345"


def test_should_create_fornecedor_dados_cadastrais_from_enum_values(
    situacao_cadastral: SituacaoCadastral,
):
    dados = FornecedorDadosCadastrais.create(
        porte=PorteEnum.EPP,
        opt_simples_nacional=False,
        situacao_cadastral=SituacaoCadastralEnum.ATIVA,
        tipo_pessoa=TipoPessoaEnum.PF,
        vinculo_sebrae=VinculoSebraeEnum.Z,
        federacao=FederacaoEnum.NAO,
        cooperativa=True,
        codigo_retencao="99999",
    )
    assert dados.porte == PorteEnum.EPP
    assert dados.cooperativa is True

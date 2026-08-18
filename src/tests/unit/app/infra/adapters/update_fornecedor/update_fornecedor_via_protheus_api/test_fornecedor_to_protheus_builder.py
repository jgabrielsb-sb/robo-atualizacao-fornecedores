import pytest
pytestmark = pytest.mark.unit
from app.domain.enums import SituacaoCadastralEnum, TipoPessoaEnum
from app.infra.adapters.update_fornecedor.update_fornecedor_via_protheus_api.fornecedor_to_protheus_builder import (
    FornecedorToProtheusBuilder,
)
from app.infra.api_requester.protheus_api_requester.models import (
    SimNaoProtheus,
    TipoFornecedorProtheus,
    VinculoSebraeProtheus,
)

from conftest import make_dados_cadastrais, make_fornecedor


def test_vinculo_sebrae_should_always_be_sem_vinculo(builder: FornecedorToProtheusBuilder):
    fornecedor = make_fornecedor()
    result = builder.build(fornecedor)
    assert result.Vinc_Seb == VinculoSebraeProtheus.SEM_VINCULO


def test_cooperativa_should_be_sim_when_cooperativa_is_true(builder: FornecedorToProtheusBuilder):
    fornecedor = make_fornecedor(
        dados_cadastrais=make_dados_cadastrais(cooperativa=True, codigo_retencao="3280")
    )
    result = builder.build(fornecedor)
    assert result.Cooperat == SimNaoProtheus.SIM


def test_cooperativa_should_be_nao_when_cooperativa_is_false(builder: FornecedorToProtheusBuilder):
    fornecedor = make_fornecedor(
        dados_cadastrais=make_dados_cadastrais(cooperativa=False, codigo_retencao="1708")
    )
    result = builder.build(fornecedor)
    assert result.Cooperat == SimNaoProtheus.NAO


def test_codigo_retencao_should_be_3280_when_is_cooperativa(builder: FornecedorToProtheusBuilder):
    fornecedor = make_fornecedor(
        dados_cadastrais=make_dados_cadastrais(cooperativa=True, codigo_retencao="3280")
    )
    result = builder.build(fornecedor)
    assert result.Cod_Rete == "3280"


def test_codigo_retencao_should_be_1708_when_is_not_cooperativa(builder: FornecedorToProtheusBuilder):
    fornecedor = make_fornecedor(
        dados_cadastrais=make_dados_cadastrais(cooperativa=False, codigo_retencao="1708")
    )
    result = builder.build(fornecedor)
    assert result.Cod_Rete == "1708"


def test_for_ativ_must_be_s_when_situacao_cadastral_is_ativa(
    builder: FornecedorToProtheusBuilder,
):
    fornecedor = make_fornecedor(
        dados_cadastrais=make_dados_cadastrais(situacao_cadastral=SituacaoCadastralEnum.ATIVA)
    )
    result = builder.build(fornecedor)
    assert result.For_Ativ == SimNaoProtheus.SIM


def test_for_ativ_must_be_n_when_situacao_cadastral_is_inapta(
    builder: FornecedorToProtheusBuilder,
):
    fornecedor = make_fornecedor(
        dados_cadastrais=make_dados_cadastrais(situacao_cadastral=SituacaoCadastralEnum.INAPTA)
    )
    result = builder.build(fornecedor)
    assert result.For_Ativ == SimNaoProtheus.NAO


def test_for_ativ_must_be_n_when_situacao_cadastral_is_suspensa(
    builder: FornecedorToProtheusBuilder,
):
    fornecedor = make_fornecedor(
        dados_cadastrais=make_dados_cadastrais(situacao_cadastral=SituacaoCadastralEnum.SUSPENSA)
    )
    result = builder.build(fornecedor)
    assert result.For_Ativ == SimNaoProtheus.NAO


def test_for_ativ_must_be_n_when_situacao_cadastral_is_baixada(
    builder: FornecedorToProtheusBuilder,
):
    fornecedor = make_fornecedor(
        dados_cadastrais=make_dados_cadastrais(situacao_cadastral=SituacaoCadastralEnum.BAIXADA)
    )
    result = builder.build(fornecedor)
    assert result.For_Ativ == SimNaoProtheus.NAO


# NOTE: The CI/OS tipo_pessoa rule ("if atividade economica principal contains COMERCIO or
# INDUSTRIA → CI, else OS") is applied when *building* the Fornecedor entity from the CartaoCNPJ
# data (in FornecedorBuilderService). By the time the Protheus builder runs, tipo_pessoa is
# already resolved on the domain entity. The Protheus API field Tipo_Forn (F/J/X) is a distinct
# concept — it represents the legal entity type, and for this workflow it is always PESSOA_JURIDICA.
# These two tests verify that invariant regardless of what tipo_pessoa is on the domain entity.

def test_tipo_forn_is_always_pessoa_juridica_when_tipo_pessoa_is_ci(builder: FornecedorToProtheusBuilder):
    fornecedor = make_fornecedor(
        dados_cadastrais=make_dados_cadastrais(tipo_pessoa=TipoPessoaEnum.CI)
    )
    result = builder.build(fornecedor)
    assert result.Tipo_Forn == TipoFornecedorProtheus.PESSOA_JURIDICA


def test_tipo_forn_is_always_pessoa_juridica_when_tipo_pessoa_is_os(builder: FornecedorToProtheusBuilder):
    fornecedor = make_fornecedor(
        dados_cadastrais=make_dados_cadastrais(tipo_pessoa=TipoPessoaEnum.OS)
    )
    result = builder.build(fornecedor)
    assert result.Tipo_Forn == TipoFornecedorProtheus.PESSOA_JURIDICA

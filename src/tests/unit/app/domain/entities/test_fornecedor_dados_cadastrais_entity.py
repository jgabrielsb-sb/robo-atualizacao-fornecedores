import pytest

from app.domain.entities.fornecedor.fornecedor_dados_cadastrais_entity import FornecedorDadosCadastrais
from app.domain.enums import FederacaoEnum, PorteEnum, TipoPessoaEnum, VinculoSebraeEnum
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
        situacao_cadastral=situacao_cadastral,
        tipo_pessoa="PESSOA FISICA",
        vinculo_sebrae="SEM VINCULO",
        federacao="NAO",
        cooperativa=False,
        codigo_retencao="12345",
    )
    assert dados.porte == PorteEnum.EPP
    assert dados.opt_simples_nacional is True
    assert dados.situacao_cadastral == situacao_cadastral
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
        situacao_cadastral=situacao_cadastral,
        tipo_pessoa=TipoPessoaEnum.PF,
        vinculo_sebrae=VinculoSebraeEnum.Z,
        federacao=FederacaoEnum.NAO,
        cooperativa=True,
        codigo_retencao="99999",
    )
    assert dados.porte == PorteEnum.EPP
    assert dados.cooperativa is True


def test_should_raise_error_when_types_are_wrong(situacao_cadastral: SituacaoCadastral):
    # porte: int is neither str nor PorteEnum → TypeError from PorteEnum.from_value
    with pytest.raises(TypeError):
        FornecedorDadosCadastrais.create(
            porte=123,
            opt_simples_nacional=True,
            situacao_cadastral=situacao_cadastral,
            tipo_pessoa="PESSOA FISICA",
            vinculo_sebrae="SEM VINCULO",
            federacao="NAO",
            cooperativa=False,
            codigo_retencao="12345",
        )

    # opt_simples_nacional: str instead of bool → TypeError from __post_init__
    with pytest.raises(TypeError) as e:
        FornecedorDadosCadastrais.create(
            porte="EMPRESA DE PEQUENO PORTE",
            opt_simples_nacional="True",
            situacao_cadastral=situacao_cadastral,
            tipo_pessoa="PESSOA FISICA",
            vinculo_sebrae="SEM VINCULO",
            federacao="NAO",
            cooperativa=False,
            codigo_retencao="12345",
        )
    assert "opt_simples_nacional" in str(e.value)

    # situacao_cadastral: str instead of SituacaoCadastral → TypeError from __post_init__
    with pytest.raises(TypeError) as e:
        FornecedorDadosCadastrais.create(
            porte="EMPRESA DE PEQUENO PORTE",
            opt_simples_nacional=True,
            situacao_cadastral="not-a-situacao",
            tipo_pessoa="PESSOA FISICA",
            vinculo_sebrae="SEM VINCULO",
            federacao="NAO",
            cooperativa=False,
            codigo_retencao="12345",
        )
    assert "situacao_cadastral" in str(e.value)

    # tipo_pessoa: int is neither str nor TipoPessoaEnum → TypeError from TipoPessoaEnum.from_value
    with pytest.raises(TypeError):
        FornecedorDadosCadastrais.create(
            porte="EMPRESA DE PEQUENO PORTE",
            opt_simples_nacional=True,
            situacao_cadastral=situacao_cadastral,
            tipo_pessoa=123,
            vinculo_sebrae="SEM VINCULO",
            federacao="NAO",
            cooperativa=False,
            codigo_retencao="12345",
        )

    # vinculo_sebrae: int is neither str nor VinculoSebraeEnum → TypeError from VinculoSebraeEnum.from_value
    with pytest.raises(TypeError):
        FornecedorDadosCadastrais.create(
            porte="EMPRESA DE PEQUENO PORTE",
            opt_simples_nacional=True,
            situacao_cadastral=situacao_cadastral,
            tipo_pessoa="PESSOA FISICA",
            vinculo_sebrae=123,
            federacao="NAO",
            cooperativa=False,
            codigo_retencao="12345",
        )

    # federacao: int is neither str nor FederacaoEnum → TypeError from FederacaoEnum.from_value
    with pytest.raises(TypeError):
        FornecedorDadosCadastrais.create(
            porte="EMPRESA DE PEQUENO PORTE",
            opt_simples_nacional=True,
            situacao_cadastral=situacao_cadastral,
            tipo_pessoa="PESSOA FISICA",
            vinculo_sebrae="SEM VINCULO",
            federacao=123,
            cooperativa=False,
            codigo_retencao="12345",
        )

    # cooperativa: str instead of bool → TypeError from __post_init__
    with pytest.raises(TypeError) as e:
        FornecedorDadosCadastrais.create(
            porte="EMPRESA DE PEQUENO PORTE",
            opt_simples_nacional=True,
            situacao_cadastral=situacao_cadastral,
            tipo_pessoa="PESSOA FISICA",
            vinculo_sebrae="SEM VINCULO",
            federacao="NAO",
            cooperativa="False",
            codigo_retencao="12345",
        )
    assert "cooperativa" in str(e.value)

    # codigo_retencao: int instead of str → TypeError from __post_init__
    with pytest.raises(TypeError) as e:
        FornecedorDadosCadastrais.create(
            porte="EMPRESA DE PEQUENO PORTE",
            opt_simples_nacional=True,
            situacao_cadastral=situacao_cadastral,
            tipo_pessoa="PESSOA FISICA",
            vinculo_sebrae="SEM VINCULO",
            federacao="NAO",
            cooperativa=False,
            codigo_retencao=12345,
        )
    assert "codigo_retencao" in str(e.value)

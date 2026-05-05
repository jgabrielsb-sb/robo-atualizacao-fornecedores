import pytest
from uuid import UUID

from app.domain.entities.fornecedor.fornecedor_entity import Fornecedor
from app.domain.entities.fornecedor.fornecedor_identificacao_entity import FornecedorIdentificacao
from app.domain.entities.fornecedor.fornecedor_dados_cadastrais_entity import FornecedorDadosCadastrais
from app.domain.entities.fornecedor.fornecedor_dados_contato_entity import FornecedorDadosContato
from app.domain.enums import FederacaoEnum, PorteEnum, TipoPessoaEnum, VinculoSebraeEnum
from app.domain.value_objects import (
    CEP,
    CNPJ,
    CodigoMunicipioIBGE,
    DDD,
    Endereco,
    Municipio,
    SituacaoCadastral,
)


@pytest.fixture
def endereco():
    municipio = Municipio.create(
        nome="Belo Horizonte",
        codigo_ibge=CodigoMunicipioIBGE.create(ibge_code="3106200"),
    )
    cep = CEP.create(cep="31310240")
    return Endereco.create(
        endereco="Rua das Flores",
        numero="123",
        complemento="Apto 1",
        cep=cep,
        municipio=municipio,
    )


@pytest.fixture
def identificacao():
    return FornecedorIdentificacao.create(
        cnpj="12345678000195",
        razao_social="Empresa XYZ Ltda",
        nome_fantasia="XYZ",
    )


@pytest.fixture
def dados_cadastrais():
    situacao_cadastral = SituacaoCadastral.create(
        ativo=True, bloqueado=False, motivo_bloqueio=None
    )
    return FornecedorDadosCadastrais.create(
        porte="EMPRESA DE PEQUENO PORTE",
        opt_simples_nacional=True,
        situacao_cadastral=situacao_cadastral,
        tipo_pessoa="PESSOA FISICA",
        vinculo_sebrae="SEM VINCULO",
        federacao="NAO",
        cooperativa=False,
        codigo_retencao="12345",
    )


@pytest.fixture
def dados_contato():
    return FornecedorDadosContato.create(ddd="11")


def test_should_create_fornecedor_from_valid_values(
    endereco: Endereco,
    identificacao: FornecedorIdentificacao,
    dados_cadastrais: FornecedorDadosCadastrais,
    dados_contato: FornecedorDadosContato,
):
    fornecedor = Fornecedor.create(
        endereco=endereco,
        identificacao=identificacao,
        dados_cadastrais=dados_cadastrais,
        dados_contato=dados_contato,
    )
    assert isinstance(fornecedor.id, UUID)
    assert fornecedor.endereco == endereco
    assert fornecedor.identificacao == identificacao
    assert fornecedor.dados_cadastrais == dados_cadastrais
    assert fornecedor.dados_contato == dados_contato


def test_should_raise_error_when_types_are_wrong(
    endereco: Endereco,
    identificacao: FornecedorIdentificacao,
    dados_cadastrais: FornecedorDadosCadastrais,
    dados_contato: FornecedorDadosContato,
):
    with pytest.raises(TypeError) as e:
        Fornecedor.create(
            endereco="not-an-endereco",
            identificacao=identificacao,
            dados_cadastrais=dados_cadastrais,
            dados_contato=dados_contato,
        )
    assert "endereco" in str(e.value)

    with pytest.raises(TypeError) as e:
        Fornecedor.create(
            endereco=endereco,
            identificacao="not-an-identificacao",
            dados_cadastrais=dados_cadastrais,
            dados_contato=dados_contato,
        )
    assert "identificacao" in str(e.value)

    with pytest.raises(TypeError) as e:
        Fornecedor.create(
            endereco=endereco,
            identificacao=identificacao,
            dados_cadastrais="not-dados-cadastrais",
            dados_contato=dados_contato,
        )
    assert "dados_cadastrais" in str(e.value)

    with pytest.raises(TypeError) as e:
        Fornecedor.create(
            endereco=endereco,
            identificacao=identificacao,
            dados_cadastrais=dados_cadastrais,
            dados_contato="not-dados-contato",
        )
    assert "dados_contato" in str(e.value)

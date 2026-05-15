import pytest

from app.infra.adapters.get_cartao_cnpj import CartaoCNPJBuilder
from conftest import DATA


@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_porte(data, cartao_cnpj_builder: CartaoCNPJBuilder):
    result = cartao_cnpj_builder.build(data["queue_response"])
    assert result.porte == data["expected_result"].porte


@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_razao_social(data, cartao_cnpj_builder: CartaoCNPJBuilder):
    result = cartao_cnpj_builder.build(data["queue_response"])
    assert result.razao_social == data["expected_result"].razao_social


@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_nome_fantasia(data, cartao_cnpj_builder: CartaoCNPJBuilder):
    result = cartao_cnpj_builder.build(data["queue_response"])
    assert result.nome_fantasia == data["expected_result"].nome_fantasia


@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_atividade_economica_principal_str(data, cartao_cnpj_builder: CartaoCNPJBuilder):
    result = cartao_cnpj_builder.build(data["queue_response"])
    assert result.atividade_economica_principal_str == data["expected_result"].atividade_economica_principal_str


@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_endereco(data, cartao_cnpj_builder: CartaoCNPJBuilder):
    result = cartao_cnpj_builder.build(data["queue_response"])
    assert result.endereco == data["expected_result"].endereco


@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_natureza_juridica(data, cartao_cnpj_builder: CartaoCNPJBuilder):
    result = cartao_cnpj_builder.build(data["queue_response"])
    assert result.natureza_juridica == data["expected_result"].natureza_juridica


@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_situacao_cadastral(data, cartao_cnpj_builder: CartaoCNPJBuilder):
    result = cartao_cnpj_builder.build(data["queue_response"])
    assert result.situacao_cadastral == data["expected_result"].situacao_cadastral

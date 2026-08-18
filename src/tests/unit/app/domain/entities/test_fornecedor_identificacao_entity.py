import pytest
pytestmark = pytest.mark.unit

from app.domain.entities.fornecedor.fornecedor_identificacao_entity import FornecedorIdentificacao
from app.domain.value_objects import CNPJ, InvalidCNPJLengthError


def test_should_create_fornecedor_identificacao_from_valid_values():
    identificacao = FornecedorIdentificacao.create(
        cnpj="12345678000195",
        razao_social="Empresa XYZ Ltda",
        nome_fantasia="XYZ",
    )
    assert isinstance(identificacao.cnpj, CNPJ)
    assert identificacao.razao_social == "Empresa XYZ Ltda"
    assert identificacao.nome_fantasia == "XYZ"


def test_should_raise_error_when_cnpj_is_invalid():
    with pytest.raises(InvalidCNPJLengthError):
        FornecedorIdentificacao.create(
            cnpj="123",
            razao_social="Empresa XYZ Ltda",
            nome_fantasia="XYZ",
        )


def test_should_raise_error_when_types_are_wrong():
    # cnpj: int instead of str → TypeError from re.sub inside CNPJ.create
    with pytest.raises(TypeError):
        FornecedorIdentificacao.create(
            cnpj=123,
            razao_social="Empresa XYZ Ltda",
            nome_fantasia="XYZ",
        )

    # razao_social: int instead of str → TypeError from __post_init__
    with pytest.raises(TypeError) as e:
        FornecedorIdentificacao.create(
            cnpj="12345678000195",
            razao_social=123,
            nome_fantasia="XYZ",
        )
    assert "razao_social" in str(e.value)

    # nome_fantasia: int instead of str → TypeError from __post_init__
    with pytest.raises(TypeError) as e:
        FornecedorIdentificacao.create(
            cnpj="12345678000195",
            razao_social="Empresa XYZ Ltda",
            nome_fantasia=123,
        )
    assert "nome_fantasia" in str(e.value)

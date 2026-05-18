import pytest
pytestmark = pytest.mark.unit

from app.domain.entities.fornecedor.fornecedor_dados_contato_entity import FornecedorDadosContato
from app.domain.value_objects import DDD


@pytest.fixture
def ddd():
    return DDD.from_value("11")


def test_should_create_fornecedor_dados_contato_from_string():
    contato = FornecedorDadosContato.create(ddd="11")
    assert isinstance(contato.ddd, DDD)
    assert contato.ddd.value == "11"


def test_should_create_fornecedor_dados_contato_from_ddd_instance(ddd: DDD):
    contato = FornecedorDadosContato.create(ddd=ddd)
    assert contato.ddd == ddd


def test_should_raise_error_when_ddd_is_wrong_type():
    # int is neither str nor DDD → TypeError from DDD.from_value
    with pytest.raises(TypeError):
        FornecedorDadosContato.create(ddd=11)

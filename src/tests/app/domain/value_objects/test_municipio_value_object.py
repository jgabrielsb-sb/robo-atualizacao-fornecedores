import pytest

from app.domain.value_objects import CodigoMunicipioIBGE, Municipio

@pytest.fixture
def codigo_ibge():
    return CodigoMunicipioIBGE.create(ibge_code="1234567")

def test_should_create_municipio_from_valid_values(codigo_ibge):
    municipio = Municipio.create(nome="São Paulo", codigo_ibge=codigo_ibge)
    assert municipio.nome == "São Paulo"
    assert municipio.codigo_ibge == codigo_ibge

def test_should_raise_when_nome_is_not_a_string(codigo_ibge):
    with pytest.raises(TypeError):
        Municipio.create(nome=1234567, codigo_ibge=codigo_ibge)

def test_should_raise_when_codigo_ibge_is_not_a_CodigoMunicipioIBGE(codigo_ibge):
    with pytest.raises(TypeError):
        Municipio.create(nome="São Paulo", codigo_ibge="1234567")

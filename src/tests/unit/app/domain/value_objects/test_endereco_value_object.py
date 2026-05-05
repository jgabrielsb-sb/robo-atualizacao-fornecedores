from app.domain.value_objects import Endereco, Municipio, CEP, CodigoMunicipioIBGE

import pytest

@pytest.fixture
def municipio():
    return Municipio.create(
        nome='São Paulo',
        codigo_ibge=CodigoMunicipioIBGE.create(ibge_code='1234567')
    )

@pytest.fixture
def cep():
    return CEP.create(cep='31310240')

def test_should_create_endereco_from_valid_values(
    cep: CEP, 
    municipio: Municipio
):
    endereco = Endereco.create(
        endereco='Rua das Flores',
        numero='123',
        complemento='Apto 101',
        cep=cep,
        municipio=municipio
    )
    assert endereco.endereco == 'Rua das Flores'
    assert endereco.numero == '123'
    assert endereco.complemento == 'Apto 101'
    assert endereco.cep == cep
    assert endereco.municipio == municipio

def test_should_raise_error_when_types_are_wrong(
    cep: CEP, 
    municipio: Municipio
):
    # endereco is not a string
    with pytest.raises(TypeError) as e:
        Endereco.create(
            endereco=123,
            numero='123',
            complemento='Apto 101',
            cep=cep,
            municipio=municipio
        )
    assert "endereco" in str(e.value)

    # numero is not a string
    with pytest.raises(TypeError) as e:
        Endereco.create(
            endereco='Rua das Flores',
            numero=123,
            complemento='Apto 101',
            cep=cep,
            municipio=municipio
        )
    assert "numero" in str(e.value)

    # complemento is not a string
    with pytest.raises(TypeError) as e:
        Endereco.create(
            endereco='Rua das Flores',
            numero='123',
            complemento=123,
            cep=cep,
            municipio=municipio
        )
    assert "complemento" in str(e.value)
    # cep is not a CEP
    with pytest.raises(TypeError) as e:
        Endereco.create(
            endereco='Rua das Flores',
            numero='123',
            complemento='Apto 101',
            cep='31310240',
            municipio=municipio
        )
    assert "cep must be a CEP" in str(e.value)

    # municipio is not a Municipio
    with pytest.raises(TypeError) as e:
        Endereco.create(
            endereco='Rua das Flores',
            numero='123',
            complemento='Apto 101',
            cep=cep,
            municipio='São Paulo'
        )
    assert "municipio" in str(e.value)
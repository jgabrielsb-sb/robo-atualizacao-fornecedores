"""
The main goal of those tests is to verify if the adapter is being capable
of handling the real data that comes from the API.

This adapter receives an API requester and a port:
    * The http server must be mocked for the API Requester:
    * The port must be mocked as a whole.

OBS: The Endereco object returned does not have required fields. All them are optional.

We must test:
    - test_should_return_endereco_with_all_none_fields_if_endereco_returned_by_api_has_all_fields_none()
    - test_should_return_endereco_with_all_fields_populated_if_endereco_returned_by_api_has_all_fields_populated()
    - test_should_return_endereco_with_complemento_none_and_all_other_fields_populated_if_endereco_returned_by_api_has_complemento_none_and_all_other_fields_populated()
    - test_should_raise_error_while_getting_external_data_error_if_municipio_port_fails()
"""
import pytest
from pytest_httpserver import HTTPServer
from app.infra.api_requester import ReceitaAPIRequester

from app.infra.adapters import (
    GetEnderecoViaReceitaAPIRequester, 
    ErrorWhileGettingExternalDataError,
)
from app.application.ports import (
    MunicipioLookupPort,
)
from app.domain.value_objects import (
    CNPJ, 
    Municipio, 
    CodigoMunicipioIBGE,
    Endereco,
)

@pytest.fixture
def endereco_all_none_fields_data() -> dict:
    return {
        "CEP": None,
        "NOME_EMPRESARIAL": None,
        "NOME_FANTASIA": None,
        "SIT_CADASTAL": None,
        "MOT_SIT_CADASTAL": None,
        "DT_SIT_CADASTAL": None,
        "DT_ABERTURA_ESTAB": None,
        "CNAE_PRINCIPAL_COD": None,
        "END_UF": None,
        "OPCAO_MEI": None,
        "PORTE": None,
        "LISTA_QSA_SOCIO_NOME": None,
        "END_TIPO_LOGRADOURO": None,
        "END_LOGRADOURO": None,
        "END_NUMERO": None,
        "END_COMPLEMENTO": None,
        "END_BAIRRO": None,
        "END_CEP": None,
        "END_MUNICIPIO": None,
        "DDD1": None,
        "TELEFONE1": None,
        "DDD2": None,
        "TELEFONE2": None,
        "EMAIL": None,
        "RESPONSAVEL_CPF": None,
        "RESPONSAVEL_NOME": None,
        "HASH": None
    }

@pytest.fixture
def endereco_data_with_all_fields_populated() -> dict:
    return {
        "CEP": "57312330",
        "NOME_EMPRESARIAL": "CLINICA CARDIOVIDA LTDA",
        "NOME_FANTASIA": "CARDIOVIDA",
        "SIT_CADASTAL": "ATIVA",
        "MOT_SIT_CADASTAL": "ATIVIDADE ECONOMICA PRINCIPAL",
        "DT_SIT_CADASTAL": 20170927,
        "DT_ABERTURA_ESTAB": 20170927,
        "CNAE_PRINCIPAL_COD": "8630502",
        "END_UF": "AL",
        "OPCAO_MEI": "N",
        "PORTE": "ME",
        "LISTA_QSA_SOCIO_NOME": "JOAO DA SILVA",
        "END_TIPO_LOGRADOURO": "RUA",
        "END_LOGRADOURO": "BARAO DE ALAGOAS",
        "END_NUMERO": "118",
        "END_COMPLEMENTO": "SALA 01",
        "END_BAIRRO": "ALTO DO CRUZEIRO",
        "END_CEP": "57312330",
        "END_MUNICIPIO": "ARAPIRACA",
        "DDD1": "82",
        "TELEFONE1": "33456789",
        "DDD2": "82",
        "TELEFONE2": "33456789",
        "EMAIL": "clinica@cardiovida.com.br",
        "RESPONSAVEL_CPF": "12345678901",
        "RESPONSAVEL_NOME": "JOAO DA SILVA",
        "HASH": "abc123"
    }

@pytest.fixture
def endereco_data_with_complemento_none_and_all_other_fields_populated() -> dict:
    return {
        "CEP": "57312330",
        "NOME_EMPRESARIAL": "CLINICA CARDIOVIDA LTDA",
        "NOME_FANTASIA": "CARDIOVIDA",
        "SIT_CADASTAL": "ATIVA",
        "MOT_SIT_CADASTAL": "ATIVIDADE ECONOMICA PRINCIPAL",
        "DT_SIT_CADASTAL": 20170927,
        "DT_ABERTURA_ESTAB": 20170927,
        "CNAE_PRINCIPAL_COD": "8630502",
        "END_UF": "AL",
        "OPCAO_MEI": "N",
        "PORTE": "ME",
        "LISTA_QSA_SOCIO_NOME": "JOAO DA SILVA",
        "END_TIPO_LOGRADOURO": "RUA",
        "END_LOGRADOURO": "BARAO DE ALAGOAS",
        "END_NUMERO": "118",
        "END_COMPLEMENTO": None,
        "END_BAIRRO": "ALTO DO CRUZEIRO",
        "END_CEP": "57312330",
        "END_MUNICIPIO": "ARAPIRACA",
        "DDD1": "82",
        "TELEFONE1": "33456789",
        "DDD2": "82",
        "TELEFONE2": "33456789",
        "EMAIL": "clinica@cardiovida.com.br",
        "RESPONSAVEL_CPF": "12345678901",
        "RESPONSAVEL_NOME": "JOAO DA SILVA",
        "HASH": "abc123"
    }

@pytest.fixture
def municipio_lookup_port() -> type[MunicipioLookupPort]:
    class MunicipioLookupPortStub(MunicipioLookupPort):
        def __init__(self, return_error: bool = False):
            self._return_error = return_error

        def get(self, municipio_name: str) -> Municipio:
            if self._return_error:
                raise Exception("Error while getting municipio")

            return Municipio(
                nome=municipio_name,
                codigo_ibge=CodigoMunicipioIBGE(value="123456"),
            )

    return MunicipioLookupPortStub

receita_api_requester_url_get_company = "/receita/api/v1/empresa-receita/get-by-cnpj/{cnpj_value}"
cnpj = CNPJ.create(cnpj="08626186000109")

def test_should_return_endereco_with_all_none_fields_if_endereco_returned_by_api_has_all_fields_none(
    httpserver: HTTPServer,
    municipio_lookup_port: type[MunicipioLookupPort],
    endereco_all_none_fields_data: dict,
):
    
    url = receita_api_requester_url_get_company.format(cnpj_value=cnpj.value)
    httpserver.expect_request(url).respond_with_json(endereco_all_none_fields_data)

    requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))

    adapter = GetEnderecoViaReceitaAPIRequester(
        municipio_lookup_port=municipio_lookup_port(),
        receita_api_requester=requester
    )

    result = adapter.get(cnpj)

    assert isinstance(result, Endereco)
    assert result.cep is None
    assert result.municipio is None
    assert result.endereco is None
    assert result.numero is None
    assert result.complemento is None

def test_should_return_endereco_with_all_fields_populated_if_endereco_returned_by_api_has_all_fields_populated(
    httpserver: HTTPServer,
    municipio_lookup_port: type[MunicipioLookupPort],
    endereco_data_with_all_fields_populated: dict,
):
    url = receita_api_requester_url_get_company.format(cnpj_value=cnpj.value)
    httpserver.expect_request(url).respond_with_json(endereco_data_with_all_fields_populated)

    requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))

    adapter = GetEnderecoViaReceitaAPIRequester(
        municipio_lookup_port=municipio_lookup_port(),
        receita_api_requester=requester
    )

    result = adapter.get(cnpj)

    assert isinstance(result, Endereco)
    assert result.cep is not None
    assert result.municipio is not None
    assert result.endereco is not None
    assert result.numero is not None
    assert result.complemento is not None

def test_should_return_endereco_with_complemento_none_and_all_other_fields_populated_if_endereco_returned_by_api_has_complemento_none_and_all_other_fields_populated(
    httpserver: HTTPServer,
    municipio_lookup_port: type[MunicipioLookupPort],
    endereco_data_with_complemento_none_and_all_other_fields_populated: dict,
):
    url = receita_api_requester_url_get_company.format(cnpj_value=cnpj.value)
    httpserver.expect_request(url).respond_with_json(endereco_data_with_complemento_none_and_all_other_fields_populated)

    requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))

    adapter = GetEnderecoViaReceitaAPIRequester(
        municipio_lookup_port=municipio_lookup_port(),
        receita_api_requester=requester
    )

    result = adapter.get(cnpj)

    assert isinstance(result, Endereco)
    assert result.cep is not None
    assert result.municipio is not None
    assert result.endereco is not None
    assert result.numero is not None
    assert result.complemento is None

def test_should_raise_error_while_getting_external_data_error_if_municipio_port_fails(
    httpserver: HTTPServer,
    municipio_lookup_port: type[MunicipioLookupPort],
    endereco_data_with_all_fields_populated: dict,
):
    url = receita_api_requester_url_get_company.format(cnpj_value=cnpj.value)
    httpserver.expect_request(url).respond_with_json(endereco_data_with_all_fields_populated)

    requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))

    adapter = GetEnderecoViaReceitaAPIRequester(
        municipio_lookup_port=municipio_lookup_port(return_error=True),
        receita_api_requester=requester
    )
    with pytest.raises(ErrorWhileGettingExternalDataError):
        adapter.get(cnpj)
from http import HTTPStatus
import pytest
from pytest_httpserver import HTTPServer

from app.domain.value_objects import CNPJ
from app.infra.api_requester.exceptions import APIRequesterException, NotFoundError
from app.infra.api_requester.receita_api_requester import ReceitaAPIGetCompanyResponse, ReceitaAPIRequester


pytestmark = pytest.mark.integration_tests

CNPJ_VALUE = "28738609000181"

@pytest.fixture
def company_data() -> dict:
    return {
        "CNPJ": CNPJ_VALUE,
        "NOME_EMPRESARIAL": "CLINICA CARDIOVIDA LTDA",
        "NOME_FANTASIA": "CARDIOVIDA",
        "SIT_CADASTAL": "ATIVA",
        "MOT_SIT_CADASTAL": None,
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
        "DDD2": None,
        "TELEFONE2": None,
        "EMAIL": "clinica@cardiovida.com.br",
        "RESPONSAVEL_CPF": "12345678901",
        "RESPONSAVEL_NOME": "JOAO DA SILVA",
        "HASH": "abc123"
    }

@pytest.fixture
def company_data_with_all_null_fields() -> dict:
    return {
        "CNPJ": None,
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


class TestGetCompany:
    url_get_company = "/receita/api/v1/empresa-receita/get-by-cnpj/{cnpj_value}"

    def test_should_return_company_response_when_api_returns_200_with_all_fields_populated(
        self,
        httpserver: HTTPServer,
        company_data: dict,
    ):
        url = self.url_get_company.format(cnpj_value=CNPJ_VALUE)

        # 1 - Define what the server expects and returns
        httpserver.expect_request(url).respond_with_json(company_data)

        # 2 - Point the real requester at the mock server
        requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))

        # 3 - Call the real method
        result = requester.get_company(CNPJ(value=CNPJ_VALUE))

        # 4 - Assert on the result
        assert isinstance(result, ReceitaAPIGetCompanyResponse)
        assert result.CNPJ == CNPJ_VALUE
        assert result.NOME_EMPRESARIAL == "CLINICA CARDIOVIDA LTDA"
        assert result.NOME_FANTASIA == "CARDIOVIDA"
        assert result.END_LOGRADOURO == "BARAO DE ALAGOAS"
        assert result.END_MUNICIPIO == "ARAPIRACA"
        assert result.DDD1 == "82"

    def test_should_return_company_response_with_all_none_fields_when_api_returns_200_with_null_fields(
        self,
        httpserver: HTTPServer,
        company_data_with_all_null_fields: dict,
    ):
        url = self.url_get_company.format(cnpj_value=CNPJ_VALUE)

        httpserver.expect_request(url).respond_with_json(company_data_with_all_null_fields)

        requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))

        result = requester.get_company(CNPJ(value=CNPJ_VALUE))

        assert isinstance(result, ReceitaAPIGetCompanyResponse)
        assert result.CNPJ is None
        assert result.NOME_EMPRESARIAL is None
        assert result.END_LOGRADOURO is None
        assert result.END_MUNICIPIO is None
        assert result.DDD1 is None

    def test_should_raise_not_found_error_when_api_returns_404(
        self,
        httpserver: HTTPServer,
    ):
        url = self.url_get_company.format(cnpj_value=CNPJ_VALUE)

        httpserver.expect_request(url).respond_with_json(
            {"error": "company not found"},
            status=HTTPStatus.NOT_FOUND,
        )

        requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))

        with pytest.raises(NotFoundError) as e:
            requester.get_company(CNPJ(value=CNPJ_VALUE))

        assert CNPJ_VALUE in str(e.value)

    def test_should_raise_api_requester_exception_when_api_returns_non_200_with_json_body(
        self,
        httpserver: HTTPServer,
    ):
        url = self.url_get_company.format(cnpj_value=CNPJ_VALUE)

        httpserver.expect_request(url).respond_with_json(
            {"error": "internal server error"},
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

        requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))

        with pytest.raises(APIRequesterException) as e:
            requester.get_company(CNPJ(value=CNPJ_VALUE))

        assert CNPJ_VALUE in str(e.value)
        assert "500" in str(e.value)

    def test_should_raise_api_requester_exception_when_api_returns_non_200_with_non_json_body(
        self,
        httpserver: HTTPServer,
    ):
        url = self.url_get_company.format(cnpj_value=CNPJ_VALUE)

        httpserver.expect_request(url).respond_with_data(
            "ERROR DATA",
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

        requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))

        with pytest.raises(APIRequesterException) as e:
            requester.get_company(CNPJ(value=CNPJ_VALUE))

        assert CNPJ_VALUE in str(e.value)
        assert "ERROR DATA" in str(e.value)

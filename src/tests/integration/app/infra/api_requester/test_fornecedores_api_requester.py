"""
By now, FornecedoresAPIRequester has two methods:
    * get_municipio_by_name;
    * get_fornecedores_to_update;
"""
from http import HTTPStatus
import pytest
from pytest_httpserver import HTTPServer

from app.domain.value_objects import CodigoMunicipioIBGE, Municipio
from app.infra.api_requester.exceptions import APIRequesterException, NotFoundError
from app.infra.api_requester.fornecedores_api_requester import FornecedorToUpdate, FornecedoresAPIRequester


pytestmark = pytest.mark.integration_tests

@pytest.fixture
def municipio_data() -> dict:
    return {
        "id": 1697,
        "municipio_name": "MACEIO",
        "codigo_ibge": "2704302",
        "created_at": "2026-05-12T11:43:55.670378-03:00",
        "updated_at": "2026-05-12T11:43:55.670378-03:00"
    }


class TestGetMunicipioByName:
    url_municipio_by_name = "/api/v1/municipios/name/{municipio_name}"
    
    def test_should_raise_not_found_error_if_municipio_wuth_that_name_is_not_found(
        self,
        httpserver: HTTPServer,
    ):
        municipio_name = "TEST"
        url = self.url_municipio_by_name.format(municipio_name=municipio_name)
        httpserver.expect_request(url).respond_with_json(
            {"error": "not found error"},
            status=HTTPStatus.NOT_FOUND
        )

        requester = FornecedoresAPIRequester(
            base_url=httpserver.url_for("")
        )
 
        with pytest.raises(NotFoundError) as e:
            requester.get_municipio_by_name(municipio_name)

        assert municipio_name in str(e.value)

    def test_should_raise_api_requester_exception_if_request_fails_and_response_is_json(
        self,
        httpserver: HTTPServer
    ):  
        municipio_name = "TEST"
        url = self.url_municipio_by_name.format(municipio_name=municipio_name)
        
        httpserver.expect_request(url).respond_with_json(
            {"error": "internal server error"},
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

        requester = FornecedoresAPIRequester(
            base_url=httpserver.url_for("")
        )

        with pytest.raises(APIRequesterException) as e:
            requester.get_municipio_by_name(municipio_name)

        assert "internal server error" in str(e.value)

    def test_should_raise_api_requester_exception_if_request_fails_and_response_is_not_json(
        self,
        httpserver: HTTPServer
    ):
        municipio_name = "TEST"
        url = self.url_municipio_by_name.format(municipio_name=municipio_name)
        
        httpserver.expect_request(url).respond_with_data(
            "ERROR DATA",
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

        requester = FornecedoresAPIRequester(
            base_url=httpserver.url_for("")
        )

        with pytest.raises(APIRequesterException) as e:
            requester.get_municipio_by_name(municipio_name)

        assert "ERROR DATA" in str(e.value)


    def test_should_return_municipio_if_there_is_municipio_with_that_name(
        self,
        httpserver: HTTPServer,
        municipio_data: dict
    ):
        municipio_name = "MACEIO"
        url = self.url_municipio_by_name.format(municipio_name=municipio_name)

        httpserver.expect_request(
            url
        ).respond_with_json(
            municipio_data
        )

        requester = FornecedoresAPIRequester(
            base_url=httpserver.url_for("")
        )

        result = requester.get_municipio_by_name(municipio_name)

        assert isinstance(result, Municipio)
        assert result == Municipio(
            nome="MACEIO",
            codigo_ibge=CodigoMunicipioIBGE(
                value="2704302"
            )
        )

class TestGetFornecedoresToUpdate:
    url_fornecedores_to_update =  "/api/v1/fornecedores-to-update/"

    def test_should_return_list_of_fornecedores_to_update_when_there_are_fornecedores_to_update_and_response_is_200(
        self,
        httpserver: HTTPServer,
        fornecedor_to_update_with_cpf_data: dict,
        fornecedor_to_update_with_cnpj_data: dict
    ):
        # 1 - Define what the server expects and returns
        httpserver.expect_request(
            self.url_fornecedores_to_update
        ).respond_with_json(
            [
                fornecedor_to_update_with_cnpj_data,
                fornecedor_to_update_with_cpf_data
            ]
        )

        # 2 - Point the real requester at the mock server
        requester = FornecedoresAPIRequester(
            base_url=httpserver.url_for("")
        )

        # 3 - Call the real method
        result = requester.get_fornecedores_to_update()

        # 4 - Assert on the result
        assert len(result) == 2
        assert all(isinstance(element, FornecedorToUpdate) for element in result)
        assert result[0].CPF_CNPJ == "08626186000109"
        assert result[1].CPF_CNPJ == "08325475498"

    def test_should_return_empty_list_when_there_are_no_fornecedores_to_update_and_response_is_200(
        self,
        httpserver: HTTPServer
    ):
        httpserver.expect_request(
            self.url_fornecedores_to_update
        ).respond_with_json([])

        requester = FornecedoresAPIRequester(
            base_url=httpserver.url_for("")
        )

        result = requester.get_fornecedores_to_update()

        assert result == []
        

    def test_should_return_api_requester_exception_when_status_code_is_not_200_and_response_is_json(
        self,
        httpserver: HTTPServer
    ):
        dict_error = {"error": "internal server error"}
        httpserver.expect_request(
            self.url_fornecedores_to_update
        ).respond_with_json(
            dict_error,
            status=500
        )

        requester = FornecedoresAPIRequester(
            base_url=httpserver.url_for("")
        )

        with pytest.raises(APIRequesterException) as e:
           requester.get_fornecedores_to_update()

        assert "500" in str(e.value)
        assert "internal server error" in str(e.value)

    def test_should_return_api_requester_exception_when_status_code_is_not_200_and_response_is_not_json(
        self,
        httpserver: HTTPServer
    ):
        error_data = "ERROR"
        
        httpserver.expect_request(
            self.url_fornecedores_to_update
        ).respond_with_data(
            error_data,
            status=500
        )

        requester = FornecedoresAPIRequester(
            base_url=httpserver.url_for("")
        )

        with pytest.raises(APIRequesterException) as e:
            requester.get_fornecedores_to_update()

        assert "ERROR" in str(e.value)


    



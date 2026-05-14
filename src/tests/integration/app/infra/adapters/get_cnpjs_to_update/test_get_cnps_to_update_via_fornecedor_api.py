"""
Those integration tests have the goal to answer:
- Does the logic work with the real data that the API produces?
    * To test that, we must mock the HTTP server with the expected 
    API responses data.

Additionally, we must answer other questions:
1 - Does the adpater raise Error when there are identifier that are not 
CPF nor CNPJ?
    * On that case, we must raise error cause we that fornecedor has an
    invalid identifier. It should be a CPF or CNPJ.

2 - Does the adapter are returning just the CNPJ's and succesfully ignoring
the CPF's?
    * The CPF's must be ignored cause we are just dealing with CNPJ's by now.

3 - Does the adapter returns an empty list where there are no fornecedores to update?

4 - Does the adapter propagates the API requester exception if the request fails?
"""
from http import HTTPStatus
import pytest 
from pytest_httpserver import HTTPServer

from app.domain.value_objects import CNPJ
from app.infra.adapters import (
    GetCNPJsToUpdateViaFornecedoresAPI, 
    InvalidIdentifierError
)
from app.infra.adapters.get_cnpjs_to_update.get_cnpjs_to_update_via_fornecedor_api import GetCNPJsToUpdateViaFornecedoresAPIError
from app.infra.api_requester.exceptions import APIRequesterException
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester

url_fornecedores_to_update =  "/api/v1/fornecedores-to-update"

def test_should_raise_invalid_identifier_error_if_identifier_is_not_cpf_nor_cnpj(
    httpserver: HTTPServer,
    fornecedor_to_update_with_cpf_data: dict,
    fornecedor_to_update_with_invalid_identifier_data: dict

):
    httpserver.expect_request(
        url_fornecedores_to_update
    ).respond_with_json(
        [
            fornecedor_to_update_with_cpf_data,
            fornecedor_to_update_with_invalid_identifier_data
        ]
    )

    requester = FornecedoresAPIRequester(
        base_url=httpserver.url_for("")
    )

    adapter = GetCNPJsToUpdateViaFornecedoresAPI(
        fornecedores_api_requester=requester
    )

    with pytest.raises(InvalidIdentifierError) as e:
        adapter.get()

    assert fornecedor_to_update_with_invalid_identifier_data["CPF_CNPJ"] in str(e.value)

    

def test_should_ignore_cpf_and_return_only_a_list_of_cnpjs(
    httpserver: HTTPServer,
    fornecedor_to_update_with_cpf_data: dict,
    fornecedor_to_update_with_cnpj_data: dict
):
    httpserver.expect_request(
        url_fornecedores_to_update
    ).respond_with_json(
        [
            fornecedor_to_update_with_cnpj_data,
            fornecedor_to_update_with_cpf_data
        ]
    )

    requester = FornecedoresAPIRequester(
        base_url=httpserver.url_for("")
    )

    adapter = GetCNPJsToUpdateViaFornecedoresAPI(
        fornecedores_api_requester=requester
    )

    result = adapter.get()

    assert len(result) == 1
    assert isinstance(result[0], CNPJ)
    #assert result[0].value == fornecedor_to_update_with_cnpj_data["CPF_CNPJ"]

def test_should_return_empty_list_when_there_are_no_fornecedores_to_update(
    httpserver: HTTPServer,
):
    httpserver.expect_request(
        url_fornecedores_to_update
    ).respond_with_json(
        []
    )

    requester = FornecedoresAPIRequester(
        base_url=httpserver.url_for("")
    )

    adapter = GetCNPJsToUpdateViaFornecedoresAPI(
        fornecedores_api_requester=requester
    )

    result = adapter.get()

    assert result == []

def test_should_raise_api_requester_exception_when_the_request_fails(
    httpserver: HTTPServer
):
    httpserver.expect_request(
        url_fornecedores_to_update
    ).respond_with_json(
        {"error": "internal server error"},
        status=HTTPStatus.INTERNAL_SERVER_ERROR
    )

    requester = FornecedoresAPIRequester(
        base_url=httpserver.url_for("")
    )

    adapter = GetCNPJsToUpdateViaFornecedoresAPI(
        fornecedores_api_requester=requester
    )

    with pytest.raises(APIRequesterException):
        adapter.get()

    
"""
Those integration tests have the goal to answer:
- Does the logic work with the real data that the Fornecedores API produces?
    * To test that, we must mock the HTTP server with the expected
    API responses data (both fornecedores-to-update and municipio lookup).

Additionally, we must answer other questions:
2 - Does the adapter return just the Fornecedores built from CNPJs,
successfully ignoring the CPFs?
    * The CPF's must be ignored cause we are just dealing with CNPJ's by now.

3 - Does the adapter returns an empty list where there are no fornecedores to update?

4 - Does the adapter propagates the API requester exception if the request fails?
"""
from http import HTTPStatus
import pytest
pytestmark = pytest.mark.integration_tests
from pytest_httpserver import HTTPServer

from app.domain.entities import Fornecedor
from app.domain.value_objects import CNPJ
from app.infra.adapters.get_fornecedores_to_update import (
    GetFornecedoresToUpdateViaFornecedoresAPI,
)
from app.infra.adapters.municipio_lookup.municipio_lookup_via_fornecedores_api import (
    MunicipioLookupViaFornecedoresAPI,
)
from app.infra.api_requester.exceptions import APIRequesterException
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester

url_fornecedores_to_update = "/api/v1/fornecedores-to-update/"
url_municipio_by_name = "/api/v1/municipios/name/MACEIO"


@pytest.fixture
def municipio_data() -> dict:
    return {
        "id": 1697,
        "municipio_name": "MACEIO",
        "codigo_ibge": "2704302",
        "created_at": "2026-05-12T11:43:55.670378-03:00",
        "updated_at": "2026-05-12T11:43:55.670378-03:00",
    }


def make_adapter(httpserver: HTTPServer) -> GetFornecedoresToUpdateViaFornecedoresAPI:
    requester = FornecedoresAPIRequester(base_url=httpserver.url_for(""))
    return GetFornecedoresToUpdateViaFornecedoresAPI(
        fornecedores_api_requester=requester,
        municipio_lookup_port=MunicipioLookupViaFornecedoresAPI(
            fornecedores_api_requester=requester,
        ),
    )


def test_should_ignore_cpf_and_return_only_fornecedores_built_from_cnpjs(
    httpserver: HTTPServer,
    fornecedor_to_update_with_cpf_data: dict,
    fornecedor_to_update_with_cnpj_data: dict,
    municipio_data: dict,
):
    httpserver.expect_request(url_fornecedores_to_update).respond_with_json(
        [fornecedor_to_update_with_cnpj_data, fornecedor_to_update_with_cpf_data]
    )
    httpserver.expect_request(url_municipio_by_name).respond_with_json(municipio_data)

    adapter = make_adapter(httpserver)

    result = adapter.get()

    assert len(result) == 1
    assert isinstance(result[0], Fornecedor)
    assert result[0].identificacao.cnpj == CNPJ.create(
        cnpj=fornecedor_to_update_with_cnpj_data["CPF_CNPJ"]
    )


def test_should_return_empty_list_when_there_are_no_fornecedores_to_update(
    httpserver: HTTPServer,
):
    httpserver.expect_request(url_fornecedores_to_update).respond_with_json([])

    adapter = make_adapter(httpserver)

    result = adapter.get()

    assert result == []


def test_should_raise_api_requester_exception_when_the_request_fails(
    httpserver: HTTPServer,
):
    httpserver.expect_request(url_fornecedores_to_update).respond_with_json(
        {"error": "internal server error"},
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    adapter = make_adapter(httpserver)

    with pytest.raises(APIRequesterException):
        adapter.get()

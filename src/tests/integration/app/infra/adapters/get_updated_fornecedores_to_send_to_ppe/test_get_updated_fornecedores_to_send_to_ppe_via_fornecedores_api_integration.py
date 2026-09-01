"""
Those integration tests have the goal to answer:
- Does the adapter correctly translate the Fornecedores API response into
  PersistUpdatedFornecedorResult instances?
- Does the adapter return an empty list where there is nothing pending?
- Does the adapter wrap a request failure into a single exception type?
"""
from http import HTTPStatus
import pytest
pytestmark = pytest.mark.integration_tests
from pytest_httpserver import HTTPServer

from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)
from app.infra.adapters.get_updated_fornecedores_to_send_to_ppe import (
    GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPI,
    GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPIError,
)
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester


def make_adapter(httpserver: HTTPServer) -> GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPI:
    return GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPI(
        fornecedores_api_requester=FornecedoresAPIRequester(base_url=httpserver.url_for("")),
    )


def test_should_return_pending_fornecedores_when_the_api_has_data(
    httpserver: HTTPServer,
    atualizacao_fornecedor_data: dict,
    url_atualizacoes_fornecedores_to_update_on_ppe: str,
):
    httpserver.expect_request(
        url_atualizacoes_fornecedores_to_update_on_ppe
    ).respond_with_json([atualizacao_fornecedor_data])

    adapter = make_adapter(httpserver)

    result = adapter.get()

    assert len(result) == 1
    assert isinstance(result[0], PersistUpdatedFornecedorResult)
    assert result[0].id == atualizacao_fornecedor_data["id"]
    assert result[0].cnpj == atualizacao_fornecedor_data["cnpj"]


def test_should_return_empty_list_when_there_is_nothing_pending(
    httpserver: HTTPServer,
    url_atualizacoes_fornecedores_to_update_on_ppe: str,
):
    httpserver.expect_request(
        url_atualizacoes_fornecedores_to_update_on_ppe
    ).respond_with_json([])

    adapter = make_adapter(httpserver)

    assert adapter.get() == []


def test_should_raise_adapter_error_when_the_request_fails(
    httpserver: HTTPServer,
    url_atualizacoes_fornecedores_to_update_on_ppe: str,
):
    httpserver.expect_request(
        url_atualizacoes_fornecedores_to_update_on_ppe
    ).respond_with_json(
        {"error": "internal server error"},
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    adapter = make_adapter(httpserver)

    with pytest.raises(GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPIError):
        adapter.get()

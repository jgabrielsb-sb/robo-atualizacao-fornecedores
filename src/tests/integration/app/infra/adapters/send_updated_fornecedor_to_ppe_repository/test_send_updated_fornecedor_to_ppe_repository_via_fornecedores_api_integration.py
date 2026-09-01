"""
Those integration tests have the goal to answer:
- Does the adapter send the correct status ("SUCCESSFULL" or "ERROR") based
  on whether why_error is set?
- Does the adapter translate the API response back into a
  PersistUpdatedFornecedorResult?
- Does the adapter wrap any failure into a single exception type?
"""
from http import HTTPStatus
import pytest
pytestmark = pytest.mark.integration_tests
from pytest_httpserver import HTTPServer

from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)
from app.infra.adapters.send_updated_fornecedor_to_ppe_repository import (
    SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPI,
    SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPIError,
)
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester


def make_adapter(httpserver: HTTPServer) -> SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPI:
    return SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPI(
        fornecedores_api_requester=FornecedoresAPIRequester(base_url=httpserver.url_for("")),
    )


def make_atualizacao_fornecedor(data: dict) -> PersistUpdatedFornecedorResult:
    return PersistUpdatedFornecedorResult(**data)


def test_should_send_successfull_status_when_there_is_no_why_error(
    httpserver: HTTPServer,
    atualizacao_fornecedor_data: dict,
    url_update_on_ppe_attempt: str,
):
    url = url_update_on_ppe_attempt.format(id=atualizacao_fornecedor_data["id"])
    httpserver.expect_request(
        url,
        method="POST",
        json={"status": "SUCCESSFULL"},
    ).respond_with_json(atualizacao_fornecedor_data, status=HTTPStatus.OK)

    adapter = make_adapter(httpserver)

    result = adapter.save(make_atualizacao_fornecedor(atualizacao_fornecedor_data))

    assert isinstance(result, PersistUpdatedFornecedorResult)
    assert result.id == atualizacao_fornecedor_data["id"]


def test_should_send_error_status_and_why_error_when_why_error_is_set(
    httpserver: HTTPServer,
    atualizacao_fornecedor_data: dict,
    url_update_on_ppe_attempt: str,
):
    url = url_update_on_ppe_attempt.format(id=atualizacao_fornecedor_data["id"])
    httpserver.expect_request(
        url,
        method="POST",
        json={"status": "ERROR", "why_error": "connection refused"},
    ).respond_with_json(atualizacao_fornecedor_data, status=HTTPStatus.OK)

    adapter = make_adapter(httpserver)

    result = adapter.save(
        make_atualizacao_fornecedor(atualizacao_fornecedor_data),
        why_error="connection refused",
    )

    assert isinstance(result, PersistUpdatedFornecedorResult)


def test_should_raise_adapter_error_when_the_stage_is_already_finished(
    httpserver: HTTPServer,
    atualizacao_fornecedor_data: dict,
    url_update_on_ppe_attempt: str,
):
    url = url_update_on_ppe_attempt.format(id=atualizacao_fornecedor_data["id"])
    httpserver.expect_request(url, method="POST").respond_with_json(
        {"error": "stage already finished"},
        status=HTTPStatus.FORBIDDEN,
    )

    adapter = make_adapter(httpserver)

    with pytest.raises(SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPIError):
        adapter.save(make_atualizacao_fornecedor(atualizacao_fornecedor_data))


def test_should_raise_adapter_error_when_the_request_fails(
    httpserver: HTTPServer,
    atualizacao_fornecedor_data: dict,
    url_update_on_ppe_attempt: str,
):
    url = url_update_on_ppe_attempt.format(id=atualizacao_fornecedor_data["id"])
    httpserver.expect_request(url, method="POST").respond_with_json(
        {"error": "internal server error"},
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    adapter = make_adapter(httpserver)

    with pytest.raises(SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPIError):
        adapter.save(make_atualizacao_fornecedor(atualizacao_fornecedor_data))

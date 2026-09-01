"""
Those integration tests have the goal to answer:
- Does the adapter correctly delegate to the Fornecedores API and translate
  its response into a PersistUpdatedFornecedorResult?
- Does the adapter wrap any failure (API error or unexpected exception) into
  a PersistUpdatedFornecedorViaFornecedoresAPIError so callers only need to
  catch one exception type?
"""
from http import HTTPStatus
import pytest
pytestmark = pytest.mark.integration_tests
from pytest_httpserver import HTTPServer

from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)
from app.domain.value_objects import CNPJ
from app.infra.adapters.persist_updated_fornecedor import (
    PersistUpdatedFornecedorViaFornecedoresAPI,
    PersistUpdatedFornecedorViaFornecedoresAPIError,
)
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester


def make_adapter(httpserver: HTTPServer) -> PersistUpdatedFornecedorViaFornecedoresAPI:
    return PersistUpdatedFornecedorViaFornecedoresAPI(
        fornecedores_api_requester=FornecedoresAPIRequester(base_url=httpserver.url_for("")),
    )


def test_should_return_persist_result_when_the_api_creates_the_record(
    httpserver: HTTPServer,
    atualizacao_fornecedor_data: dict,
    url_atualizacoes_fornecedores: str,
):
    httpserver.expect_request(
        url_atualizacoes_fornecedores, method="POST"
    ).respond_with_json(atualizacao_fornecedor_data, status=HTTPStatus.CREATED)

    adapter = make_adapter(httpserver)

    result = adapter.create(CNPJ.create(cnpj=atualizacao_fornecedor_data["cnpj"]))

    assert isinstance(result, PersistUpdatedFornecedorResult)
    assert result.id == atualizacao_fornecedor_data["id"]
    assert result.cnpj == atualizacao_fornecedor_data["cnpj"]


def test_should_raise_adapter_error_when_the_api_rejects_the_payload(
    httpserver: HTTPServer,
    url_atualizacoes_fornecedores: str,
):
    httpserver.expect_request(
        url_atualizacoes_fornecedores, method="POST"
    ).respond_with_json(
        {"error": "unprocessable entity"},
        status=HTTPStatus.UNPROCESSABLE_ENTITY,
    )

    adapter = make_adapter(httpserver)

    with pytest.raises(PersistUpdatedFornecedorViaFornecedoresAPIError):
        adapter.create(CNPJ.create(cnpj="08626186000109"))


def test_should_raise_adapter_error_when_the_request_fails(
    httpserver: HTTPServer,
    url_atualizacoes_fornecedores: str,
):
    httpserver.expect_request(
        url_atualizacoes_fornecedores, method="POST"
    ).respond_with_json(
        {"error": "internal server error"},
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    adapter = make_adapter(httpserver)

    with pytest.raises(PersistUpdatedFornecedorViaFornecedoresAPIError):
        adapter.create(CNPJ.create(cnpj="08626186000109"))

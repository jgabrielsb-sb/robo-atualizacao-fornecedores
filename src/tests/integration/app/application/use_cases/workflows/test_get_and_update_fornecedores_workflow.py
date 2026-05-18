"""
Workflow integration tests — real adapters, controlled input.

What is being tested:
    GetAndUpdateFornecedoresWorkflow composed with production adapters,
    verifying that the full build → persist pipeline works against the
    real test environment APIs.

Wiring:
    get_cnpjs_to_update  → FakeGetCNPJsToUpdatePort   (controlled — inject specific CNPJs)
    build_fornecedor     → FornecedorBuilderService    (real: queue, Receita API, Selenium)
    update_fornecedor    → UpdateFornecedorViaProtheusAPI (real: Protheus test API)

Requirements:
    - RabbitMQ queue must be reachable (cartao CNPJ)
    - Receita API must be reachable (endereco fallback)
    - Protheus test API must be reachable
    - CNPJs used must exist in the Protheus test database

Run:
    pytest -m real_case_tests
"""
import pytest

pytestmark = pytest.mark.integration_tests
from app.domain.value_objects import CNPJ

multiple_cnpjs = [
    CNPJ(value="02356937000120"),
    CNPJ(value="08422461000164"),
    CNPJ(value="12415352000197"),
    CNPJ(value="12269296000200"),
    CNPJ(value="12630679000181"),
]


@pytest.mark.real_case_tests
def test_should_successfully_build_and_update_a_single_fornecedor(make_workflow):
    cnpjs = [CNPJ(value="02356937000120")]  # TODO: replace with a real CNPJ from the test DB

    result = make_workflow(cnpjs).run()

    assert result.fornecedores_to_update_count == 1
    assert result.successfully_built_fornecedores_count == 1
    assert result.failed_built_fornecedores_count == 0
    assert result.successfully_updated_fornecedores_count == 1
    assert result.failed_updated_fornecedores_count == 0


@pytest.mark.real_case_tests
def test_should_successfully_build_and_update_multiple_fornecedores(make_workflow):
    result = make_workflow(multiple_cnpjs).run()

    assert result.fornecedores_to_update_count == len(multiple_cnpjs)
    assert result.successfully_built_fornecedores_count == len(multiple_cnpjs)
    assert result.failed_built_fornecedores_count == 0
    assert result.successfully_updated_fornecedores_count == len(multiple_cnpjs)
    assert result.failed_updated_fornecedores_count == 0


@pytest.mark.real_case_tests
def test_should_return_zero_counts_when_no_cnpjs_are_provided(make_workflow):
    result = make_workflow([]).run()

    assert result.fornecedores_to_update_count == 0
    assert result.successfully_built_fornecedores_count == 0
    assert result.failed_built_fornecedores_count == 0
    assert result.successfully_updated_fornecedores_count == 0
    assert result.failed_updated_fornecedores_count == 0

import pytest
pytestmark = pytest.mark.unit

from app.application.use_cases.workflows.send_updated_fornecedores_to_ppe_workflow import (
    SendUpdatedFornecedoresToPPEWorkflow,
    SendUpdatedFornecedoresToPPEWorkflowError,
)
from tests.unit.app.application.use_cases.workflows.send_updated_fornecedores_to_ppe_workflow.fakes import (
    make_fake_atualizacao_fornecedor,
    FakeGetUpdatedFornecedoresToSendToPPEPort,
    FakeSendUpdatedFornecedorToPPEPort,
    FakeSendUpdatedFornecedorToPPERepositoryPort,
)


def make_workflow(
    atualizacoes_fornecedores=None,
    get_error=None,
    fail_send_ids=None,
    fail_register_ids=None,
):
    send_port = FakeSendUpdatedFornecedorToPPEPort(fail_fornecedores_ids=fail_send_ids)
    repository_port = FakeSendUpdatedFornecedorToPPERepositoryPort(fail_fornecedores_ids=fail_register_ids)
    workflow = SendUpdatedFornecedoresToPPEWorkflow(
        get_updated_fornecedores_to_send_to_ppe=FakeGetUpdatedFornecedoresToSendToPPEPort(
            atualizacoes_fornecedores=atualizacoes_fornecedores, error=get_error
        ),
        send_updated_fornecedor_to_ppe=send_port,
        send_updated_fornecedor_to_ppe_repository=repository_port,
    )
    return workflow, send_port, repository_port


def test_should_send_and_register_all_fornecedores():
    atualizacoes_fornecedores = [
        make_fake_atualizacao_fornecedor(1),
        make_fake_atualizacao_fornecedor(2),
        make_fake_atualizacao_fornecedor(3),
    ]
    workflow, _, _ = make_workflow(atualizacoes_fornecedores=atualizacoes_fornecedores)
    result = workflow.run()

    assert result.fornecedores_to_send_count == 3
    assert result.successfully_sent_fornecedores_count == 3
    assert result.failed_sent_fornecedores_count == 0
    assert result.successfully_registered_fornecedores_count == 3
    assert result.failed_registered_fornecedores_count == 0


def test_should_return_zero_counts_when_there_is_nothing_to_send():
    workflow, _, _ = make_workflow(atualizacoes_fornecedores=[])
    result = workflow.run()

    assert result.fornecedores_to_send_count == 0
    assert result.successfully_sent_fornecedores_count == 0
    assert result.failed_sent_fornecedores_count == 0
    assert result.successfully_registered_fornecedores_count == 0
    assert result.failed_registered_fornecedores_count == 0


def test_should_raise_workflow_error_when_get_fails():
    workflow, _, _ = make_workflow(get_error=Exception("Failed to get atualizacoes fornecedores"))

    with pytest.raises(SendUpdatedFornecedoresToPPEWorkflowError):
        workflow.run()


def test_should_still_register_attempt_when_send_fails():
    """The attempt must be registered even when sending to PPE fails."""
    atualizacoes_fornecedores = [make_fake_atualizacao_fornecedor(1)]
    workflow, send_port, repository_port = make_workflow(
        atualizacoes_fornecedores=atualizacoes_fornecedores,
        fail_send_ids=[1],
    )
    result = workflow.run()

    assert result.failed_sent_fornecedores_count == 1
    assert result.successfully_registered_fornecedores_count == 1
    assert len(repository_port.calls) == 1


def test_should_register_error_status_with_why_error_message_when_send_fails():
    atualizacoes_fornecedores = [make_fake_atualizacao_fornecedor(1)]
    workflow, _, repository_port = make_workflow(
        atualizacoes_fornecedores=atualizacoes_fornecedores,
        fail_send_ids=[1],
    )
    workflow.run()

    _, why_error = repository_port.calls[0]
    assert why_error is not None
    assert "Error sending updated fornecedor to PPE" in why_error


def test_should_register_success_with_no_why_error_message_when_send_succeeds():
    atualizacoes_fornecedores = [make_fake_atualizacao_fornecedor(1)]
    workflow, _, repository_port = make_workflow(atualizacoes_fornecedores=atualizacoes_fornecedores)
    workflow.run()

    _, why_error = repository_port.calls[0]
    assert why_error is None


def test_should_count_correctly_when_some_sends_fail():
    atualizacoes_fornecedores = [
        make_fake_atualizacao_fornecedor(1),
        make_fake_atualizacao_fornecedor(2),
        make_fake_atualizacao_fornecedor(3),
    ]
    workflow, _, _ = make_workflow(
        atualizacoes_fornecedores=atualizacoes_fornecedores,
        fail_send_ids=[2],
    )
    result = workflow.run()

    assert result.fornecedores_to_send_count == 3
    assert result.successfully_sent_fornecedores_count == 2
    assert result.failed_sent_fornecedores_count == 1
    assert result.successfully_registered_fornecedores_count == 3
    assert result.failed_registered_fornecedores_count == 0


def test_should_count_correctly_when_some_registers_fail():
    atualizacoes_fornecedores = [
        make_fake_atualizacao_fornecedor(1),
        make_fake_atualizacao_fornecedor(2),
        make_fake_atualizacao_fornecedor(3),
    ]
    workflow, _, _ = make_workflow(
        atualizacoes_fornecedores=atualizacoes_fornecedores,
        fail_register_ids=[2],
    )
    result = workflow.run()

    assert result.fornecedores_to_send_count == 3
    assert result.successfully_sent_fornecedores_count == 3
    assert result.failed_sent_fornecedores_count == 0
    assert result.successfully_registered_fornecedores_count == 2
    assert result.failed_registered_fornecedores_count == 1


def test_should_count_correctly_when_both_send_and_register_fail_for_different_fornecedores():
    atualizacoes_fornecedores = [
        make_fake_atualizacao_fornecedor(1),
        make_fake_atualizacao_fornecedor(2),
        make_fake_atualizacao_fornecedor(3),
    ]
    workflow, _, _ = make_workflow(
        atualizacoes_fornecedores=atualizacoes_fornecedores,
        fail_send_ids=[1],
        fail_register_ids=[2],
    )
    result = workflow.run()

    assert result.fornecedores_to_send_count == 3
    assert result.successfully_sent_fornecedores_count == 2
    assert result.failed_sent_fornecedores_count == 1
    assert result.successfully_registered_fornecedores_count == 2
    assert result.failed_registered_fornecedores_count == 1


def test_should_process_every_fornecedor_even_when_all_sends_fail():
    atualizacoes_fornecedores = [
        make_fake_atualizacao_fornecedor(1),
        make_fake_atualizacao_fornecedor(2),
        make_fake_atualizacao_fornecedor(3),
    ]
    workflow, send_port, repository_port = make_workflow(
        atualizacoes_fornecedores=atualizacoes_fornecedores,
        fail_send_ids=[1, 2, 3],
    )
    result = workflow.run()

    assert result.failed_sent_fornecedores_count == 3
    assert result.successfully_registered_fornecedores_count == 3
    assert len(send_port.calls) == 3
    assert len(repository_port.calls) == 3

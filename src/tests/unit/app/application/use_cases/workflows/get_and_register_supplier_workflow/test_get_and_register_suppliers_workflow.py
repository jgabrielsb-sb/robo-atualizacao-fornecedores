import logging

import pytest

from tests.unit.app.application.use_cases.workflows.get_and_register_supplier_workflow.fakes import (
    FakeFornecedorToUpdate,
    FakeGetFornecedoresToUpdate,
    SpyFornecedorToUpdateRepository,
)

from app.application.use_cases import (
    GetAndRegisterFornecedoresToUpdateWorkflow,
    GetAndRegisterFornecedoresToUpdateWorkflowError,
    GetAndRegisterFornecedoresToUpdateWorkflowResult,
)


class TestWorkflow:
    def test_should_get_and_register_all_fornecedores_to_update(self):
        fornecedores = [
            FakeFornecedorToUpdate(id=1),
            FakeFornecedorToUpdate(id=2),
            FakeFornecedorToUpdate(id=3)
        ]
        
        get_fornecedores = FakeGetFornecedoresToUpdate(
            fornecedores=fornecedores,
            error=None
        )

        repository = SpyFornecedorToUpdateRepository(
            fail_fornecedores=None
        )

        workflow = GetAndRegisterFornecedoresToUpdateWorkflow(
            get_fornecedores_to_update=get_fornecedores,
            fornecedor_to_update_repository=repository
        )



        result = workflow.run()
        assert result.workflow_trace_id is not None
        assert result.fornecedores_to_update_count == 3
        assert result.registered_fornecedores_count == 3
        assert result.failed_fornecedores_count == 0

    def test_should_return_zero_counts_when_there_are_no_fornecedores_to_update(self):
        fornecedores = []

        get_fornecedores = FakeGetFornecedoresToUpdate(
            fornecedores=fornecedores,
            error=None
        )

        repository = SpyFornecedorToUpdateRepository(
            fail_fornecedores=None
        )
        
        workflow = GetAndRegisterFornecedoresToUpdateWorkflow(
            get_fornecedores_to_update=get_fornecedores,
            fornecedor_to_update_repository=repository
        )

        result = workflow.run()
        assert result.workflow_trace_id is not None
        assert result.fornecedores_to_update_count == 0
        assert result.registered_fornecedores_count == 0
        assert result.failed_fornecedores_count == 0

    def test_should_raise_workflow_error_when_get_fornecedores_fails(self):
        error = Exception("Failed to get fornecedores")
        get_fornecedores = FakeGetFornecedoresToUpdate(
            error=error
        )

        repository = SpyFornecedorToUpdateRepository(
            fail_fornecedores=None
        )

        workflow = GetAndRegisterFornecedoresToUpdateWorkflow(
            get_fornecedores_to_update=get_fornecedores,
            fornecedor_to_update_repository=repository
        )

        with pytest.raises(GetAndRegisterFornecedoresToUpdateWorkflowError):
            workflow.run()

    def test_should_continue_registering_when_one_fornecedor_fails_to_save(self):
        fornecedores = [
            FakeFornecedorToUpdate(id=1),
            FakeFornecedorToUpdate(id=2),
            FakeFornecedorToUpdate(id=3)
        ]
        
        get_fornecedores = FakeGetFornecedoresToUpdate(
            fornecedores=fornecedores,
            error=None
        )

        repository = SpyFornecedorToUpdateRepository(
            fail_fornecedores=[FakeFornecedorToUpdate(id=2)]
        )

        workflow = GetAndRegisterFornecedoresToUpdateWorkflow(
            get_fornecedores_to_update=get_fornecedores,
            fornecedor_to_update_repository=repository
        )

        result = workflow.run()
        assert result.workflow_trace_id is not None
        assert result.fornecedores_to_update_count == 3
        assert result.registered_fornecedores_count == 2
        assert result.failed_fornecedores_count == 1

    def test_should_return_all_failed_when_every_save_fails(self):
        fornecedores = [
            FakeFornecedorToUpdate(id=1),
            FakeFornecedorToUpdate(id=2),
            FakeFornecedorToUpdate(id=3)
        ]
        
        get_fornecedores = FakeGetFornecedoresToUpdate(
            fornecedores=fornecedores,
            error=None
        )

        repository = SpyFornecedorToUpdateRepository(
            fail_fornecedores=fornecedores
        )

        workflow = GetAndRegisterFornecedoresToUpdateWorkflow(
            get_fornecedores_to_update=get_fornecedores,
            fornecedor_to_update_repository=repository
        )

        result = workflow.run()
        assert result.workflow_trace_id is not None
        assert result.fornecedores_to_update_count == 3
        assert result.registered_fornecedores_count == 0
        assert result.failed_fornecedores_count == 3

class TestLogging:
    def test_should_log_success_summary_when_all_fornecedores_are_registered(self, caplog):
        pass

    def test_should_log_warning_summary_when_some_fornecedores_fail(self, caplog):
        pass
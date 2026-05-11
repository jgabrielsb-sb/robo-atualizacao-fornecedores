import pytest

from app.application.use_cases.workflows.get_and_update_fornecedores_workflow import (
    GetAndUpdateFornecedoresWorkflow,
    GetAndUpdateFornecedoresWorkflowError,
)
from tests.unit.app.application.use_cases.workflows.get_and_update_fornecedores_workflow.fakes import (
    FakeFornecedorToUpdate,
    FakeGetFornecedoresToUpdatePort,
    FakeBuildFornecedorPort,
    FakeFornecedorRepositoryPort,
)


def make_workflow(
    fornecedores=None,
    get_error=None,
    fail_build_ids=None,
    fail_update_ids=None,
) -> GetAndUpdateFornecedoresWorkflow:
    return GetAndUpdateFornecedoresWorkflow(
        get_fornecedores_to_update=FakeGetFornecedoresToUpdatePort(
            fornecedores=fornecedores, error=get_error
        ),
        build_fornecedor=FakeBuildFornecedorPort(fail_fornecedores_ids=fail_build_ids),
        fornecedor_repository=FakeFornecedorRepositoryPort(fail_fornecedores_ids=fail_update_ids),
    )


def test_should_build_and_update_all_fornecedores():
    fornecedores = [FakeFornecedorToUpdate(id=1), FakeFornecedorToUpdate(id=2), FakeFornecedorToUpdate(id=3)]
    result = make_workflow(fornecedores=fornecedores).run()

    assert result.fornecedores_to_update_count == 3
    assert result.successfully_built_fornecedores_count == 3
    assert result.failed_built_fornecedores_count == 0
    assert result.successfully_updated_fornecedores_count == 3
    assert result.failed_updated_fornecedores_count == 0


def test_should_return_zero_counts_when_no_fornecedores_to_update():
    result = make_workflow(fornecedores=[]).run()

    assert result.fornecedores_to_update_count == 0
    assert result.successfully_built_fornecedores_count == 0
    assert result.failed_built_fornecedores_count == 0
    assert result.successfully_updated_fornecedores_count == 0
    assert result.failed_updated_fornecedores_count == 0


def test_should_raise_workflow_error_when_get_fornecedores_fails():
    workflow = make_workflow(get_error=Exception("Failed to get fornecedores"))

    with pytest.raises(GetAndUpdateFornecedoresWorkflowError):
        workflow.run()


def test_should_skip_and_continue_when_some_builds_fail():
    """1 of 3 fails to build; the 2 successfully built are updated."""
    fornecedores = [FakeFornecedorToUpdate(id=1), FakeFornecedorToUpdate(id=2), FakeFornecedorToUpdate(id=3)]
    result = make_workflow(fornecedores=fornecedores, fail_build_ids=[2]).run()

    assert result.fornecedores_to_update_count == 3
    assert result.successfully_built_fornecedores_count == 2
    assert result.failed_built_fornecedores_count == 1
    assert result.successfully_updated_fornecedores_count == 2
    assert result.failed_updated_fornecedores_count == 0


def test_should_return_all_failed_builds_when_every_build_fails():
    fornecedores = [FakeFornecedorToUpdate(id=1), FakeFornecedorToUpdate(id=2), FakeFornecedorToUpdate(id=3)]
    result = make_workflow(fornecedores=fornecedores, fail_build_ids=[1, 2, 3]).run()

    assert result.fornecedores_to_update_count == 3
    assert result.successfully_built_fornecedores_count == 0
    assert result.failed_built_fornecedores_count == 3
    assert result.successfully_updated_fornecedores_count == 0
    assert result.failed_updated_fornecedores_count == 0


def test_should_skip_and_continue_when_some_updates_fail():
    """All 3 build successfully; 1 of 3 fails to update."""
    fornecedores = [FakeFornecedorToUpdate(id=1), FakeFornecedorToUpdate(id=2), FakeFornecedorToUpdate(id=3)]
    result = make_workflow(fornecedores=fornecedores, fail_update_ids=[2]).run()

    assert result.fornecedores_to_update_count == 3
    assert result.successfully_built_fornecedores_count == 3
    assert result.failed_built_fornecedores_count == 0
    assert result.successfully_updated_fornecedores_count == 2
    assert result.failed_updated_fornecedores_count == 1


def test_should_return_all_failed_updates_when_every_update_fails():
    fornecedores = [FakeFornecedorToUpdate(id=1), FakeFornecedorToUpdate(id=2), FakeFornecedorToUpdate(id=3)]
    result = make_workflow(fornecedores=fornecedores, fail_update_ids=[1, 2, 3]).run()

    assert result.fornecedores_to_update_count == 3
    assert result.successfully_built_fornecedores_count == 3
    assert result.failed_built_fornecedores_count == 0
    assert result.successfully_updated_fornecedores_count == 0
    assert result.failed_updated_fornecedores_count == 3


def test_should_count_correctly_when_both_build_and_update_partially_fail():
    """1 of 3 fails to build; of the 2 built, 1 fails to update."""
    fornecedores = [FakeFornecedorToUpdate(id=1), FakeFornecedorToUpdate(id=2), FakeFornecedorToUpdate(id=3)]
    result = make_workflow(fornecedores=fornecedores, fail_build_ids=[1], fail_update_ids=[2]).run()

    assert result.fornecedores_to_update_count == 3
    assert result.successfully_built_fornecedores_count == 2
    assert result.failed_built_fornecedores_count == 1
    assert result.successfully_updated_fornecedores_count == 1
    assert result.failed_updated_fornecedores_count == 1

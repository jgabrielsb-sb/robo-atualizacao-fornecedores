
from app.application.use_cases.workflows.update_fornecedores_workflow import UpdateFornecedoresWorkflow
from tests.unit.app.application.use_cases.workflows.update_fornecedor_workflow.fakes import (
    FakeFornecedorToUpdate,
    FakeGetFornecedoresToUpdatePort,
    FakeBuildFornecedorPort,
    FakeFornecedorRepositoryPort
)
from app.domain.enums import StatusEnum


def test_should_get_build_and_update_all_fornecedores():
    """
    Caso 0:
        * Obteve 3 fornecedores para atualizar, construiu e salvou todos.
        - Neste caso, o workflow retorna:
            1 - status = SUCCESS
            2 - fornecedores_to_update_count = 3;
            3 - built_fornecedores = 3;
            4 - failed_built_fornecedores = 0;
            5 - updated_fornecedores = 3;
            6 - failed_updated_fornecedores = 0;
    """
    fornecedores_to_update = [
        FakeFornecedorToUpdate(id=1),
        FakeFornecedorToUpdate(id=2),
        FakeFornecedorToUpdate(id=3)
    ]

    get_fornecedores = FakeGetFornecedoresToUpdatePort(fornecedores=fornecedores_to_update)
    build_fornecedor = FakeBuildFornecedorPort()
    fornecedor_repositoy=FakeFornecedorRepositoryPort()

    workflow = UpdateFornecedoresWorkflow(
        get_fornecedores_to_update=get_fornecedores,
        build_fornecedor=build_fornecedor,
        fornecedor_repository=fornecedor_repositoy
    )

    result = workflow.run()

    assert result.status == StatusEnum.SUCCESS
    assert result.fornecedores_to_update_count == 3
    assert result.successfully_built_fornecedores_count == 3
    assert result.failed_built_fornecedores_count == 0
    assert result.successfully_updated_fornecedores_count == 3
    assert result.failed_updated_fornecedores_count == 0



def test_should_return_correct_count_and_error_status_when_got_error_on_getting_fornecedores_to_update():
    """
    Caso 1:
        * Erro ao obter os fornecedores que devem ser atualizados.
        - Neste caso, o workflow retorna:
            1 - status = ERROR
            2 - fornecedores_to_update_count = None;
            3 - built_fornecedores = None;
            4 - failed_built_fornecedores = None;
            5 - updated_fornecedores = None;
            6 - failed_updated_fornecedores = None;
    """
    get_fornecedores = FakeGetFornecedoresToUpdatePort(error=Exception('Error getting fornecedores to update'))
    build_fornecedor = FakeBuildFornecedorPort()
    fornecedor_repositoy=FakeFornecedorRepositoryPort()

    workflow = UpdateFornecedoresWorkflow(
        get_fornecedores_to_update=get_fornecedores,
        build_fornecedor=build_fornecedor,
        fornecedor_repository=fornecedor_repositoy
    )

    result = workflow.run()

    assert result.status == StatusEnum.ERROR
    assert result.fornecedores_to_update_count == 0
    assert result.successfully_built_fornecedores_count == 0
    assert result.failed_built_fornecedores_count == 0
    assert result.successfully_updated_fornecedores_count == 0
    assert result.failed_updated_fornecedores_count == 0

def test_should_return_correct_count_when_partial_failure_when_building_fornecedores():
    """
    Caso 2:
        * De 3 fornecedores, 1 retornou erro ao ser construído;
        * Todos os fornecedores construidos (2) foram atualizados
        - Neste caso, o worfkflow retorna:
            1 - status = PARTIAL
            2 - fornecedores_to_update_count = 3
            3 - built_fornecedores = 2
            4 - failed_built_fornecedores = 1
            5 - updated_fornecedores = 2
            6 - failed_updated_fornecedores = 0
    """
    fornecedores_to_update = [
        FakeFornecedorToUpdate(id=1),
        FakeFornecedorToUpdate(id=2),
        FakeFornecedorToUpdate(id=3)
    ]
    get_fornecedores = FakeGetFornecedoresToUpdatePort(fornecedores=fornecedores_to_update)
    build_fornecedor = FakeBuildFornecedorPort(fail_fornecedores_ids=[1])
    fornecedor_repositoy=FakeFornecedorRepositoryPort()
    workflow = UpdateFornecedoresWorkflow(
        get_fornecedores_to_update=get_fornecedores,
        build_fornecedor=build_fornecedor,
        fornecedor_repository=fornecedor_repositoy
    )
    result = workflow.run()
    assert result.status == StatusEnum.PARTIAL
    assert result.fornecedores_to_update_count == 3
    assert result.successfully_built_fornecedores_count == 2
    assert result.failed_built_fornecedores_count == 1
    assert result.successfully_updated_fornecedores_count == 2
    assert result.failed_updated_fornecedores_count == 0

def test_should_return_correct_count_when_partial_failed_when_building_and_updating_fornecedores():
    """
    Caso 3:
        * De 3 fornecedores, 1 retornou erro ao ser construido;
        * De 2 fornecedores construidos, 1 retornou erro ao ser salvo;
        - Neste caso, o worflow retorna:
            1 - status = PARTIAL
            2 - fornecedores_to_update_count = 3
            3 - successfully_built_fornecedores = 2
            4 - failed_built_fornecedores = 1
            5 - successfully_updated_fornecedores = 1
            6 - failed_updated_fornecedores = 1
    """
    fornecedores_to_update = [
        FakeFornecedorToUpdate(id=1),
        FakeFornecedorToUpdate(id=2),
        FakeFornecedorToUpdate(id=3)
    ]
    get_fornecedores = FakeGetFornecedoresToUpdatePort(fornecedores=fornecedores_to_update)
    build_fornecedor = FakeBuildFornecedorPort(fail_fornecedores_ids=[1])
    fornecedor_repositoy=FakeFornecedorRepositoryPort(fail_fornecedores_ids=[2])
    workflow = UpdateFornecedoresWorkflow(
        get_fornecedores_to_update=get_fornecedores,
        build_fornecedor=build_fornecedor,
        fornecedor_repository=fornecedor_repositoy
    )
    result = workflow.run()
    assert result.status == StatusEnum.PARTIAL
    assert result.fornecedores_to_update_count == 3
    assert result.successfully_built_fornecedores_count == 2
    assert result.failed_built_fornecedores_count == 1
    assert result.successfully_updated_fornecedores_count == 1
    assert result.failed_updated_fornecedores_count == 1

def test_should_return_zero_count_when_there_are_no_fornecedores_to_update():
    """
    Caso 4:
        * Nenhum fornecedor a ser atualizado;
        - Neste caso, o worflow retorna:
            1 - status = SUCCESS
            2 - fornecedores_to_update_count = 0
            3 - successfully_built_fornecedores = 0
            4 - failed_built_fornecedores = 0
            5 - successfully_updated_fornecedores = 0
            6 - failed_updated_fornecedores = 0
    """
    fornecedores_to_update = []
    get_fornecedores = FakeGetFornecedoresToUpdatePort(fornecedores=fornecedores_to_update)
    build_fornecedor = FakeBuildFornecedorPort()
    fornecedor_repositoy=FakeFornecedorRepositoryPort()
    workflow = UpdateFornecedoresWorkflow(
        get_fornecedores_to_update=get_fornecedores,
        build_fornecedor=build_fornecedor,
        fornecedor_repository=fornecedor_repositoy
    )
    result = workflow.run()
    assert result.status == StatusEnum.SUCCESS
    assert result.fornecedores_to_update_count == 0
    assert result.successfully_built_fornecedores_count == 0
    assert result.failed_built_fornecedores_count == 0
    assert result.successfully_updated_fornecedores_count == 0
    assert result.failed_updated_fornecedores_count == 0




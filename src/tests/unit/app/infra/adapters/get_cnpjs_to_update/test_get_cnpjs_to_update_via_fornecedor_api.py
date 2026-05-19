import pytest
pytestmark = pytest.mark.unit

from app.infra.adapters.get_cnpjs_to_update import (
    GetCNPJsToUpdateViaFornecedoresAPI,
    InvalidIdentifierError,
)
from app.infra.api_requester.fornecedores_api_requester  import (
    FornecedoresAPIRequester, 
    FornecedorToUpdate,
)
from app.domain.value_objects import CNPJ

def fake_fornecedores_api_requester(
    mock_get_fornecedores_to_update: list[FornecedorToUpdate] | None = None,
) -> FornecedoresAPIRequester:
    class FakeFornecedoresAPIRequester(FornecedoresAPIRequester):
        def __init__(
            self, 
            mock_get_fornecedores_to_update: list[FornecedorToUpdate] | None = None,
        ):
            self._mock_get_fornecedores_to_update = mock_get_fornecedores_to_update
        
        def get_fornecedores_to_update(self) -> list[FornecedorToUpdate] | None:
            return self._mock_get_fornecedores_to_update
        
    return FakeFornecedoresAPIRequester(mock_get_fornecedores_to_update)

@pytest.fixture
def fornecedor_to_update_with_cpf() -> FornecedorToUpdate:
    return FornecedorToUpdate(
        LOJA="test loja",
        CODIGO="test codigo",
        NOME="test nome",
        NOME_FANTASIA="test nome fantasia",
        CPF_CNPJ="529.982.247-25",
    )

@pytest.fixture
def fornecedor_to_update_with_cnpj() -> FornecedorToUpdate:
    return FornecedorToUpdate(
        LOJA="test loja",
        CODIGO="test codigo",
        NOME="test nome",
        NOME_FANTASIA="test nome fantasia",
        CPF_CNPJ="62.173.620/0001-80",
    )

@pytest.fixture
def fornecedor_to_update_with_invalid_identifier() -> FornecedorToUpdate:
    return FornecedorToUpdate(
        LOJA="test loja",
        CODIGO="test codigo",
        NOME="test nome",
        NOME_FANTASIA="test nome fantasia",
        CPF_CNPJ="123",
    )

def test_should_return_just_cnpjs_when_some_fornecedores_have_cpfs(
    fornecedor_to_update_with_cpf: FornecedorToUpdate,
    fornecedor_to_update_with_cnpj: FornecedorToUpdate,
):
    mock_get_fornecedores_to_update = [
        fornecedor_to_update_with_cpf,
        fornecedor_to_update_with_cnpj,
    ]

    fornecedores_api_requester = fake_fornecedores_api_requester(
        mock_get_fornecedores_to_update=mock_get_fornecedores_to_update,
    )

    get_cnpjs_to_update_via_fornecedor_api = GetCNPJsToUpdateViaFornecedoresAPI(
        fornecedores_api_requester=fornecedores_api_requester,
    )

    result = get_cnpjs_to_update_via_fornecedor_api.get()
    
    assert len(result) == 1
    assert isinstance(result[0], CNPJ)

def test_should_return_empty_list_when_all_fornecedores_have_cpfs(
    fornecedor_to_update_with_cpf: FornecedorToUpdate,
):
    fornecedores_api_requester = fake_fornecedores_api_requester(
        mock_get_fornecedores_to_update=[
            fornecedor_to_update_with_cpf,
            fornecedor_to_update_with_cpf,
        ],
    )

    get_cnpjs_to_update_via_fornecedor_api = GetCNPJsToUpdateViaFornecedoresAPI(
        fornecedores_api_requester=fornecedores_api_requester,
    )

    result = get_cnpjs_to_update_via_fornecedor_api.get()
    assert len(result) == 0

# def test_should_raise_error_when_fornecedor_has_identifier_that_is_not_a_cpf_or_cnpj(
#     fornecedor_to_update_with_invalid_identifier: FornecedorToUpdate,
#     fornecedor_to_update_with_cnpj: FornecedorToUpdate,
#     fornecedor_to_update_with_cpf: FornecedorToUpdate,
# ):
#     fornecedores_api_requester = fake_fornecedores_api_requester(
#         mock_get_fornecedores_to_update=[
#             fornecedor_to_update_with_invalid_identifier,
#             fornecedor_to_update_with_cnpj,
#         ],
#     )

#     get_cnpjs_to_update_via_fornecedor_api = GetCNPJsToUpdateViaFornecedoresAPI(
#         fornecedores_api_requester=fornecedores_api_requester,
#     )

#     with pytest.raises(InvalidIdentifierError):
#         get_cnpjs_to_update_via_fornecedor_api.get()

def test_should_raise_empty_list_when_there_are_no_fornecedores_to_update():
    
    mock_values = [
        None,
        [],
    ]

    for mock_value in mock_values:
        fornecedores_api_requester = fake_fornecedores_api_requester(
            mock_get_fornecedores_to_update=mock_value,
        )

        get_cnpjs_to_update_via_fornecedor_api = GetCNPJsToUpdateViaFornecedoresAPI(
            fornecedores_api_requester=fornecedores_api_requester,
        )

        result = get_cnpjs_to_update_via_fornecedor_api.get()
        assert len(result) == 0



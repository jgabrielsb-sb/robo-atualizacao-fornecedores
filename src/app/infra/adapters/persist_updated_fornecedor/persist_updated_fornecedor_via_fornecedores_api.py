from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    UpdatedFornecedorRepositoryPort,
    PersistUpdatedFornecedorResult,
)
from app.domain.value_objects import CNPJ
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester


class PersistUpdatedFornecedorViaFornecedoresAPIError(Exception):
    pass


class PersistUpdatedFornecedorViaFornecedoresAPI(UpdatedFornecedorRepositoryPort):
    def __init__(
        self,
        fornecedores_api_requester: FornecedoresAPIRequester,
    ):
        self._fornecedores_api_requester = fornecedores_api_requester

    def create(self, cnpj: CNPJ) -> PersistUpdatedFornecedorResult:
        try:
            atualizacao_fornecedor = self._fornecedores_api_requester.create_atualizacao_fornecedor(cnpj.value)
            return PersistUpdatedFornecedorResult(**atualizacao_fornecedor.model_dump())
        except Exception as e:
            raise PersistUpdatedFornecedorViaFornecedoresAPIError(
                f"Failed to persist updated fornecedor {cnpj.value}: {e}"
            ) from e

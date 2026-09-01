from typing import Optional

from app.application.ports.fornecedor.send_updated_fornecedor_to_ppe_repository_port import (
    SendUpdatedFornecedorToPPERepositoryPort,
)
from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)
from app.infra.api_requester.fornecedores_api_requester import (
    AttemptStatus,
    FornecedoresAPIRequester,
)


class SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPIError(Exception):
    pass


class SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPI(SendUpdatedFornecedorToPPERepositoryPort):
    def __init__(
        self,
        fornecedores_api_requester: FornecedoresAPIRequester,
    ):
        self._fornecedores_api_requester = fornecedores_api_requester

    def save(
        self,
        atualizacao_fornecedor: PersistUpdatedFornecedorResult,
        why_error: Optional[str] = None,
    ) -> PersistUpdatedFornecedorResult:
        status = AttemptStatus.ERROR if why_error is not None else AttemptStatus.SUCCESSFULL

        try:
            updated_atualizacao_fornecedor = self._fornecedores_api_requester.register_update_on_ppe_attempt(
                id=atualizacao_fornecedor.id,
                status=status,
                why_error=why_error,
            )
            return PersistUpdatedFornecedorResult(**updated_atualizacao_fornecedor.model_dump())
        except Exception as e:
            raise SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPIError(
                f"Failed to register update_on_ppe attempt for atualizacao_fornecedor {atualizacao_fornecedor.id}: {e}"
            ) from e

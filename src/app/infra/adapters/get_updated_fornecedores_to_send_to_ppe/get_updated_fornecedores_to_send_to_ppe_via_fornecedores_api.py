from app.application.ports.fornecedor.get_updated_fornecedores_to_send_to_ppe_port import (
    GetUpdatedFornecedoresToSendToPPEPort,
)
from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester


class GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPIError(Exception):
    pass


class GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPI(GetUpdatedFornecedoresToSendToPPEPort):
    def __init__(
        self,
        fornecedores_api_requester: FornecedoresAPIRequester,
    ):
        self._fornecedores_api_requester = fornecedores_api_requester

    def get(self) -> list[PersistUpdatedFornecedorResult]:
        try:
            atualizacoes_fornecedores = self._fornecedores_api_requester.get_atualizacoes_fornecedores_pending_update_on_ppe()
            return [
                PersistUpdatedFornecedorResult(**atualizacao_fornecedor.model_dump())
                for atualizacao_fornecedor in atualizacoes_fornecedores
            ]
        except Exception as e:
            raise GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPIError(
                f"Failed to get updated fornecedores to send to PPE: {e}"
            ) from e

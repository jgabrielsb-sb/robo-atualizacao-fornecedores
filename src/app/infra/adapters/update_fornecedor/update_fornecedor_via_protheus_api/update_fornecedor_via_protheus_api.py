from app.application.ports.fornecedor.update_fornecedor_port import UpdateFornecedorPort
from app.domain.entities import Fornecedor
from app.infra.adapters.update_fornecedor.update_fornecedor_via_protheus_api.fornecedor_to_protheus_builder import FornecedorToProtheusBuilder
from app.infra.api_requester import ProtheusAPIRequester
from app.application.ports.fornecedor.update_fornecedor_port import UpdateFornecedorResult


class UpdateFornecedorViaProtheusAPIError(Exception):
    pass


class UpdateFornecedorViaProtheusAPI(UpdateFornecedorPort):
    def __init__(
        self,
        protheus_api_requester: ProtheusAPIRequester,
    ):
        self._protheus_api_requester = protheus_api_requester
        self._builder = FornecedorToProtheusBuilder()

    def update(self, fornecedor: Fornecedor) -> UpdateFornecedorResult:
        try:
            payload = self._builder.build(fornecedor)
            protheus_update_result = self._protheus_api_requester.update_fornecedor(payload)
            return UpdateFornecedorResult(
                input=payload.model_dump(),
                output=protheus_update_result.model_dump(),
            )
        except Exception as e:
            raise UpdateFornecedorViaProtheusAPIError(
                f"Failed to update fornecedor {fornecedor.identificacao.cnpj.value}: {e}"
            ) from e

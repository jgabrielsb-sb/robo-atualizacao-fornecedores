from typing import Any, Dict

from app.application.ports import GetCartaoCNPJPort, MunicipioLookupPort
from app.domain.value_objects import CNPJ, CartaoCNPJ
from app.infra.adapters.get_cartao_cnpj.cartao_cnpj_builder import CartaoCNPJBuilder
from app.infra.adapters.exceptions import ErrorWhileGettingExternalDataError
from app.infra.queue.rpc_queue_requester import RPCCartaoCNPJQueueRequester

class GetCartaoCNPJViaQueueRequesterError(Exception):
    pass

class GetCartaoCNPJViaQueueRequester(GetCartaoCNPJPort):
    def __init__(
        self,
        queue_requester: RPCCartaoCNPJQueueRequester,
        municipio_lookup_port: MunicipioLookupPort,
    ) -> None:
        self._queue_requester = queue_requester
        self._builder = CartaoCNPJBuilder(municipio_lookup_port=municipio_lookup_port)

    def _get_response_from_external_source(self, cnpj: CNPJ) -> Dict[str, Any]:
        try:
            return self._queue_requester.get_response(cnpj)
        except Exception as e:
            raise ErrorWhileGettingExternalDataError(
                f"error while getting the external data from the queue: {e}"
            ) from e

    def _validate_response(self, response: Dict[str, Any]) -> None:
        try:
            status = response["status"]
        except KeyError:
            raise GetCartaoCNPJViaQueueRequesterError(
                f"error while trying to get 'status' field from the response: {response}."
            ) from KeyError

        if status != "ok":
            raise GetCartaoCNPJViaQueueRequesterError(
                f"got status {status} from the response: {response}, but expected 'ok'."
            )

    def get(self, cnpj: CNPJ) -> CartaoCNPJ:
        response = self._get_response_from_external_source(cnpj)
        self._validate_response(response)
        return self._builder.build(response)

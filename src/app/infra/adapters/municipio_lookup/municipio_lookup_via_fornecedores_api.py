from app.application.ports import MunicipioLookupPort
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester

from app.domain.value_objects import Municipio

class MunicipioLookupViaFornecedoresAPI(MunicipioLookupPort):
    def __init__(
        self,
        fornecedores_api_requester: FornecedoresAPIRequester,
    ):
        self._fornecedores_api_requester = fornecedores_api_requester

    def get(self, municipio_name: str) -> Municipio:
        return self._fornecedores_api_requester.get_municipio_by_name(municipio_name)
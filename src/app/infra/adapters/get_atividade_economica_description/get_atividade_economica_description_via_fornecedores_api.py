from app.application.ports import GetAtividadeEconomicaDescriptionPort
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester

class GetAtividadeEconomicaDescriptionViaFornecedoresAPI(GetAtividadeEconomicaDescriptionPort):
    def __init__(
        self,
        fornecedores_api_requester: FornecedoresAPIRequester,
    ):
        self._fornecedores_api_requester = fornecedores_api_requester

    def get(self, code: str) -> str:
        cnae = self._fornecedores_api_requester.get_cnae_by_code(code)
        return cnae.description

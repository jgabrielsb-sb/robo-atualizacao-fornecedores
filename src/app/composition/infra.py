from dataclasses import dataclass

from config.settings import settings
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester

@dataclass
class InfraProvider:
    def get_fornecedores_api_requester(self) -> FornecedoresAPIRequester:
        return FornecedoresAPIRequester(
            base_url=settings.FORNECEDORES_API_BASE_URL
        )

    

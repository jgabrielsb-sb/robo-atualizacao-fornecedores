from dataclasses import dataclass

from config.settings import settings
from app.infra.api_requester import (
    FornecedoresAPIRequester, 
    ReceitaAPIRequester,
)

@dataclass
class InfraProvider:
    def get_fornecedores_api_requester(self) -> FornecedoresAPIRequester:
        return FornecedoresAPIRequester(
            base_url=settings.FORNECEDORES_API_BASE_URL
        )

    def get_receita_api_requester(self) -> ReceitaAPIRequester:
        return ReceitaAPIRequester(
            base_url=settings.RECEITA_API_BASE_URL
        )
    

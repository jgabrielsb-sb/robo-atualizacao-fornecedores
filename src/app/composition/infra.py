from dataclasses import dataclass

from config.settings import settings
from app.infra.api_requester import (
    FornecedoresAPIRequester,
    ProtheusAPIRequester,
    ReceitaAPIRequester,
)
from app.infra.queue.rpc_queue_requester import RPCCartaoCNPJQueueRequester, QueueConfig

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

    def get_protheus_api_requester(self) -> ProtheusAPIRequester:
        return ProtheusAPIRequester(
            base_url=settings.PROTHEUS_API_BASE_URL,
            c_auth=settings.PROTHEUS_C_AUTH,
            authorization_token=settings.PROTHEUS_AUTHORIZATION_TOKEN,
        )

    def get_rpc_cartao_cnpj_queue_requester(self) -> RPCCartaoCNPJQueueRequester:
        return RPCCartaoCNPJQueueRequester(
            config=QueueConfig(
                host=settings.RABBIT_HOST,
                port=str(settings.RABBIT_PORT),
                virtual_host=settings.RABBIT_VIRTUAL_HOST,
                username=settings.RABBIT_USER,
                password=settings.RABBIT_PASSWORD,
                connection_name=settings.RABBIT_CONNECTION_NAME,
                queue_name=settings.RABBIT_QUEUE_NAME,
            )
        )

    def get_ppe_queue_config(self) -> QueueConfig:
        return QueueConfig(
            host=settings.RABBIT_PPE_HOST,
            port=str(settings.RABBIT_PPE_PORT),
            virtual_host=settings.RABBIT_PPE_VIRTUAL_HOST,
            username=settings.RABBIT_PPE_USER,
            password=settings.RABBIT_PPE_PASSWORD,
            connection_name="robo_atualizacao_fornecedores_ppe",
            queue_name=settings.RABBIT_PPE_QUEUE_NAME,
        )


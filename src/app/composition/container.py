from dataclasses import dataclass

from app.composition.adapter import AdapterProvider
from app.composition.infra import InfraProvider

from app.application.use_cases.workflows import GetAndUpdateFornecedoresWorkflow
from app.application.services.fornecedor_builder_service import FornecedorBuilderService

@dataclass
class Container:
    def __init__(self):
        self.adapter_provider = AdapterProvider()
        self.infra_provider = InfraProvider()

    def get_build_fornecedor_service(self) -> FornecedorBuilderService:
        return FornecedorBuilderService(
            get_opt_simples_nacional_port=self.adapter_provider.get_get_opt_simples_nacional_with_selenium_adapter(),
            get_cartao_cnpj_port=self.adapter_provider.get_get_cartao_cnpj_via_queue_requester_adapter(),
            get_endereco_port=self.adapter_provider.get_get_endereco_via_receita_api_requester_adapter(),
        )

    def get_get_and_update_fornecedores_workflow(self) -> GetAndUpdateFornecedoresWorkflow:
        return GetAndUpdateFornecedoresWorkflow(
            get_fornecedores_to_update=self.adapter_provider.get_get_fornecedores_to_update_via_fornecedores_api_adapter(),
            build_fornecedor=self.adapter_provider.get_build_fornecedor_via_receita_api_adapter(),
            update_fornecedor=self.adapter_provider.get_update_fornecedor_via_protheus_api_adapter(),
        )

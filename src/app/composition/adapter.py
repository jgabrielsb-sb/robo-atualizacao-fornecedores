from dataclasses import dataclass

from app.infra.adapters import (
    GetOptSimplesNacionalWithSelenium,
    GetFornecedoresToUpdateViaFornecedoresAPI,
    UpdateFornecedorViaProtheusAPI,
    GetCartaoCNPJViaQueueRequester,
    MunicipioLookupViaFornecedoresAPI,
    GetEnderecoViaReceitaAPIRequester,
    BuildFornecedorViaReceitaAPI,
    GetAtividadeEconomicaDescriptionViaFornecedoresAPI,
    PersistUpdatedFornecedorViaFornecedoresAPI,
    GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPI,
    SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPI,
    SendUpdatedFornecedorToPPEViaQueue,
)

from app.composition.infra import InfraProvider


@dataclass
class AdapterProvider:
    def __init__(self):
        self.infra_provider = InfraProvider()
    
    def get_get_opt_simples_nacional_with_selenium_adapter(self) -> GetOptSimplesNacionalWithSelenium:
        return GetOptSimplesNacionalWithSelenium()

    def get_get_municipio_via_fornecedores_api_adapter(self) -> MunicipioLookupViaFornecedoresAPI:
        return MunicipioLookupViaFornecedoresAPI(
            fornecedores_api_requester=self.infra_provider.get_fornecedores_api_requester(),
        )

    def get_get_cartao_cnpj_via_queue_requester_adapter(self) -> GetCartaoCNPJViaQueueRequester:
        return GetCartaoCNPJViaQueueRequester(
            queue_requester=self.infra_provider.get_rpc_cartao_cnpj_queue_requester(),
            municipio_lookup_port=self.get_get_municipio_via_fornecedores_api_adapter(),
        )

    def get_get_endereco_via_receita_api_requester_adapter(self) -> GetEnderecoViaReceitaAPIRequester:
        return GetEnderecoViaReceitaAPIRequester(
            municipio_lookup_port=self.get_get_municipio_via_fornecedores_api_adapter(),
            receita_api_requester=self.infra_provider.get_receita_api_requester(),
        )

    def get_get_fornecedores_to_update_via_fornecedores_api_adapter(self) -> GetFornecedoresToUpdateViaFornecedoresAPI:
        return GetFornecedoresToUpdateViaFornecedoresAPI(
            fornecedores_api_requester=self.infra_provider.get_fornecedores_api_requester(),
            municipio_lookup_port=self.get_get_municipio_via_fornecedores_api_adapter(),
        )

    def get_update_fornecedor_via_protheus_api_adapter(self) -> UpdateFornecedorViaProtheusAPI:
        return UpdateFornecedorViaProtheusAPI(
            protheus_api_requester=self.infra_provider.get_protheus_api_requester(),
        )

    def get_persist_updated_fornecedor_via_fornecedores_api_adapter(self) -> PersistUpdatedFornecedorViaFornecedoresAPI:
        return PersistUpdatedFornecedorViaFornecedoresAPI(
            fornecedores_api_requester=self.infra_provider.get_fornecedores_api_requester(),
        )

    def get_get_updated_fornecedores_to_send_to_ppe_via_fornecedores_api_adapter(self) -> GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPI:
        return GetUpdatedFornecedoresToSendToPPEViaFornecedoresAPI(
            fornecedores_api_requester=self.infra_provider.get_fornecedores_api_requester(),
        )

    def get_send_updated_fornecedor_to_ppe_repository_via_fornecedores_api_adapter(self) -> SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPI:
        return SendUpdatedFornecedorToPPERepositoryViaFornecedoresAPI(
            fornecedores_api_requester=self.infra_provider.get_fornecedores_api_requester(),
        )

    def get_send_updated_fornecedor_to_ppe_via_queue_adapter(self) -> SendUpdatedFornecedorToPPEViaQueue:
        return SendUpdatedFornecedorToPPEViaQueue(
            config=self.infra_provider.get_ppe_queue_config(),
        )

    def get_get_atividade_economica_description_via_fornecedores_api_adapter(self) -> GetAtividadeEconomicaDescriptionViaFornecedoresAPI:
        return GetAtividadeEconomicaDescriptionViaFornecedoresAPI(
            fornecedores_api_requester=self.infra_provider.get_fornecedores_api_requester(),
        )

    def get_build_fornecedor_via_receita_api_adapter(self) -> BuildFornecedorViaReceitaAPI:
        return BuildFornecedorViaReceitaAPI(
            get_opt_simples_nacional_port=self.get_get_opt_simples_nacional_with_selenium_adapter(),
            get_atividade_economica_description_port=self.get_get_atividade_economica_description_via_fornecedores_api_adapter(),
            municipio_lookup_port=self.get_get_municipio_via_fornecedores_api_adapter(),
            receita_api_requester=self.infra_provider.get_receita_api_requester(),
        )


    

    
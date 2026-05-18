import pytest

from app.application.ports import GetCNPJsToUpdatePort
from app.application.services.fornecedor_builder_service import FornecedorBuilderService
from app.application.use_cases.workflows import GetAndUpdateFornecedoresWorkflow
from app.composition.infra import InfraProvider
from app.domain.value_objects import CNPJ
from app.infra.adapters.get_cartao_cnpj.get_cartao_cnpj_via_queue_requester import GetCartaoCNPJViaQueueRequester
from app.infra.adapters.get_endereco.get_endereco_via_receita_api_requester import GetEnderecoViaReceitaAPIRequester
from app.infra.adapters.get_opt_simples_nacional.get_opt_simples_nacional_with_selenium import GetOptSimplesNacionalWithSelenium
from app.infra.adapters.municipio_lookup.municipio_lookup_via_fornecedores_api import MunicipioLookupViaFornecedoresAPI
from app.infra.adapters.update_fornecedor.update_fornecedor_via_protheus_api.update_fornecedor_via_protheus_api import UpdateFornecedorViaProtheusAPI


class FakeGetCNPJsToUpdatePort(GetCNPJsToUpdatePort):
    def __init__(self, cnpjs: list[CNPJ]):
        self._cnpjs = cnpjs

    def get(self) -> list[CNPJ]:
        return self._cnpjs

@pytest.fixture(scope="session")
def infra():
    return InfraProvider()


@pytest.fixture(scope="session")
def municipio_lookup(infra: InfraProvider):
    return MunicipioLookupViaFornecedoresAPI(
        fornecedores_api_requester=infra.get_fornecedores_api_requester(),
    )


@pytest.fixture(scope="session")
def real_build_fornecedor(infra: InfraProvider, municipio_lookup: MunicipioLookupViaFornecedoresAPI):
    return FornecedorBuilderService(
        get_opt_simples_nacional_port=GetOptSimplesNacionalWithSelenium(),
        get_cartao_cnpj_port=GetCartaoCNPJViaQueueRequester(
            queue_requester=infra.get_rpc_cartao_cnpj_queue_requester(),
            municipio_lookup_port=municipio_lookup,
        ),
        get_endereco_port=GetEnderecoViaReceitaAPIRequester(
            municipio_lookup_port=municipio_lookup,
            receita_api_requester=infra.get_receita_api_requester(),
        ),
    )


@pytest.fixture(scope="session")
def real_update_fornecedor(infra: InfraProvider):
    return UpdateFornecedorViaProtheusAPI(
        protheus_api_requester=infra.get_protheus_api_requester(),
    )


@pytest.fixture
def make_workflow(real_build_fornecedor: FornecedorBuilderService, real_update_fornecedor: UpdateFornecedorViaProtheusAPI):
    def _make(cnpjs: list[CNPJ]) -> GetAndUpdateFornecedoresWorkflow:
        return GetAndUpdateFornecedoresWorkflow(
            get_cnpjs_to_update=FakeGetCNPJsToUpdatePort(cnpjs),
            build_fornecedor=real_build_fornecedor,
            update_fornecedor=real_update_fornecedor,
        )
    return _make


@pytest.fixture(scope="session")
def fake_get_cnpjs_to_update(infra: InfraProvider):
    return FakeGetCNPJsToUpdatePort(
        cnpjs=[CNPJ(value="02356937000120")],
    )
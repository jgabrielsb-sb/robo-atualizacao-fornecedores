import pytest

from app.application.ports import GetFornecedoresToUpdatePort
from app.application.services.fornecedor_builder_service import FornecedorBuilderService
from app.application.use_cases.workflows import GetAndUpdateFornecedoresWorkflow
from app.composition.infra import InfraProvider
from app.domain.entities import Fornecedor
from app.domain.entities.fornecedor import (
    FornecedorDadosCadastrais,
    FornecedorDadosContato,
    FornecedorIdentificacao,
)
from app.domain.enums import (
    FederacaoEnum,
    PorteEnum,
    SituacaoCadastralEnum,
    TipoPessoaEnum,
    VinculoSebraeEnum,
)
from app.domain.value_objects import CNPJ, Endereco
from app.infra.adapters.get_cartao_cnpj.get_cartao_cnpj_via_queue_requester import GetCartaoCNPJViaQueueRequester
from app.infra.adapters.get_endereco.get_endereco_via_receita_api_requester import GetEnderecoViaReceitaAPIRequester
from app.infra.adapters.get_opt_simples_nacional.get_opt_simples_nacional_with_selenium import GetOptSimplesNacionalWithSelenium
from app.infra.adapters.municipio_lookup.municipio_lookup_via_fornecedores_api import MunicipioLookupViaFornecedoresAPI
from app.infra.adapters.update_fornecedor.update_fornecedor_via_protheus_api.update_fornecedor_via_protheus_api import UpdateFornecedorViaProtheusAPI


def _wrap_cnpj_as_fornecedor(cnpj: CNPJ) -> Fornecedor:
    """
    The real workflow only needs identificacao.cnpj out of what
    get_fornecedores_to_update returns — build_fornecedor re-enriches by CNPJ.
    """
    return Fornecedor.create(
        endereco=Endereco(),
        identificacao=FornecedorIdentificacao(cnpj=cnpj, razao_social="Fake Fornecedor"),
        dados_cadastrais=FornecedorDadosCadastrais(
            porte=PorteEnum.ME,
            opt_simples_nacional=False,
            situacao_cadastral=SituacaoCadastralEnum.ATIVA,
            tipo_pessoa=TipoPessoaEnum.CI,
            vinculo_sebrae=VinculoSebraeEnum.Z,
            federacao=FederacaoEnum.NAO,
            cooperativa=False,
            codigo_retencao="0000",
        ),
        dados_contato=FornecedorDadosContato(),
    )


class FakeGetFornecedoresToUpdatePort(GetFornecedoresToUpdatePort):
    def __init__(self, cnpjs: list[CNPJ]):
        self._fornecedores = [_wrap_cnpj_as_fornecedor(cnpj) for cnpj in cnpjs]

    def get(self) -> list[Fornecedor]:
        return self._fornecedores

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
            get_fornecedores_to_update=FakeGetFornecedoresToUpdatePort(cnpjs),
            build_fornecedor=real_build_fornecedor,
            update_fornecedor=real_update_fornecedor,
        )
    return _make


@pytest.fixture(scope="session")
def fake_get_fornecedores_to_update(infra: InfraProvider):
    return FakeGetFornecedoresToUpdatePort(
        cnpjs=[CNPJ(value="02356937000120")],
    )
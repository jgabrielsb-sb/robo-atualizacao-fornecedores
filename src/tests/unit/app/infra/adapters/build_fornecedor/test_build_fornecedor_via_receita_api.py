import pytest
pytestmark = pytest.mark.unit

from app.application.ports import MunicipioLookupPort, GetAtividadeEconomicaDescriptionPort
from app.application.ports.fornecedor.build_fornecedor.get_opt_simples_nacional_port import GetOptSimplesNacionalPort
from app.domain.enums import PorteEnum, SituacaoCadastralEnum, TipoPessoaEnum, TipoContratoSocialEnum
from app.domain.value_objects import CNPJ, Municipio, CodigoMunicipioIBGE
from app.infra.adapters.build_fornecedor.build_fornecedor_via_receita_api import (
    BuildFornecedorViaReceitaAPI,
    GetReceitaAPICompanyResponseError,
    GetMunicipioError,
    GetAtividadeEconomicaDescriptionError,
)
from app.infra.api_requester.receita_api_requester import ReceitaAPIGetCompanyResponse

_EX_1 = {
    "CNPJ": "28738609000181",
    "NOME_EMPRESARIAL": "CLINICA CARDIOVIDA LTDA",
    "NOME_FANTASIA": "CARDIOVIDA",
    "SIT_CADASTRAL": "02",
    "MOT_SIT_CADASTAL": None,
    "DT_SIT_CADASTAL": None,
    "DT_ABERTURA_ESTAB": 20170927,
    "CNAE_PRINCIPAL_COD": "8630502",
    "END_UF": "AL",
    "OPCAO_MEI": "N",
    "PORTE": "01",
    "LISTA_QSA_SOCIO_NOME": "DEISE MEDEIROS MOREIRA RIBEIRO|JOAO PAULO MOREIRA RIBEIRO",
    "END_TIPO_LOGRADOURO": "RUA",
    "END_LOGRADOURO": "BARAO DE ALAGOAS",
    "END_NUMERO": "118",
    "END_COMPLEMENTO": "SALA  03",
    "END_BAIRRO": "ALTO DO CRUZEIRO",
    "END_CEP": "57312330",
    "END_MUNICIPIO": "ARAPIRACA",
    "DDD1": "31",
    "TELEFONE1": "93840004",
    "DDD2": None,
    "TELEFONE2": None,
    "EMAIL": "INOVA@INOVAA.COM.BR",
    "RESPONSAVEL_CPF": "7573399642",
    "RESPONSAVEL_NOME": "JOAO PAULO MOREIRA RIBEIRO",
    "HASH": None,
}

_CNPJ = CNPJ.create("28738609000181")

# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------

class FakeMunicipioLookupPort(MunicipioLookupPort):
    def get(self, municipio_name: str) -> Municipio:
        return Municipio(nome=municipio_name, codigo_ibge=CodigoMunicipioIBGE(value="2704302"))


class FakeFailingMunicipioLookupPort(MunicipioLookupPort):
    def get(self, municipio_name: str) -> Municipio:
        raise Exception("municipio lookup failed")


class FakeGetOptSimplesNacionalPort(GetOptSimplesNacionalPort):
    def __init__(self, value: bool):
        self._value = value

    def get(self, cnpj: CNPJ) -> bool:
        return self._value


class FakeGetAtividadeEconomicaDescriptionPort(GetAtividadeEconomicaDescriptionPort):
    def __init__(self, description: str):
        self._description = description

    def get(self, code: str) -> str:
        return self._description


class FakeFailingGetAtividadeEconomicaDescriptionPort(GetAtividadeEconomicaDescriptionPort):
    def get(self, code: str) -> str:
        raise Exception("atividade economica description failed")


class FakeReceitaAPIRequester:
    def __init__(self, response: ReceitaAPIGetCompanyResponse):
        self._response = response

    def get_company(self, cnpj: CNPJ) -> ReceitaAPIGetCompanyResponse:
        return self._response


class FakeFailingReceitaAPIRequester:
    def get_company(self, cnpj: CNPJ) -> ReceitaAPIGetCompanyResponse:
        raise Exception("receita api failed")


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------

def make_api_response(**overrides) -> ReceitaAPIGetCompanyResponse:
    return ReceitaAPIGetCompanyResponse(**{**_EX_1, **overrides})


def make_adapter(
    api_response: ReceitaAPIGetCompanyResponse | None = None,
    opt_simples_nacional: bool = False,
    atividade_economica_description: str = "SERVICO DE SAUDE",
    failing_receita_api: bool = False,
    failing_municipio: bool = False,
    failing_atividade_economica: bool = False,
) -> BuildFornecedorViaReceitaAPI:
    receita_requester = (
        FakeFailingReceitaAPIRequester()
        if failing_receita_api
        else FakeReceitaAPIRequester(api_response or make_api_response())
    )
    atividade_port = (
        FakeFailingGetAtividadeEconomicaDescriptionPort()
        if failing_atividade_economica
        else FakeGetAtividadeEconomicaDescriptionPort(atividade_economica_description)
    )
    municipio_port = (
        FakeFailingMunicipioLookupPort()
        if failing_municipio
        else FakeMunicipioLookupPort()
    )
    return BuildFornecedorViaReceitaAPI(
        get_opt_simples_nacional_port=FakeGetOptSimplesNacionalPort(opt_simples_nacional),
        get_atividade_economica_description_port=atividade_port,
        municipio_lookup_port=municipio_port,
        receita_api_requester=receita_requester,
    )


# ---------------------------------------------------------------------------
# Error-propagation tests
# ---------------------------------------------------------------------------

def test_raise_proper_error_if_could_not_get_atividade_economica_description():
    adapter = make_adapter(failing_atividade_economica=True)

    with pytest.raises(GetAtividadeEconomicaDescriptionError):
        adapter.get_tipo_pessoa("8630502")


def test_raise_proper_error_if_could_not_get_receita_api_company():
    adapter = make_adapter(failing_receita_api=True)

    with pytest.raises(GetReceitaAPICompanyResponseError):
        adapter.get_receita_api_company(_CNPJ)


def test_raise_proper_error_if_could_not_get_municipio():
    adapter = make_adapter(failing_municipio=True)

    with pytest.raises(GetMunicipioError):
        adapter.get_municipio("ARAPIRACA")


# ---------------------------------------------------------------------------
# Mapping validation tests
# ---------------------------------------------------------------------------

def test_raise_value_error_if_porte_is_not_one_of_the_expected_values():
    adapter = make_adapter()

    with pytest.raises(ValueError):
        adapter.get_porte("99")


def test_raise_value_error_if_situacao_cadastral_is_not_one_of_the_expected_values():
    adapter = make_adapter()

    with pytest.raises(ValueError):
        adapter.get_situacao_cadastral("99")


# ---------------------------------------------------------------------------
# Porte tests
# ---------------------------------------------------------------------------

def test_build_returns_fornecedor_with_porte_me_when_porte_returned_by_receita_api_is_01():
    adapter = make_adapter(api_response=make_api_response(PORTE="01"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.porte == PorteEnum.ME


def test_build_returns_fornecedor_with_porte_epp_when_porte_returned_by_receita_api_is_03():
    adapter = make_adapter(api_response=make_api_response(PORTE="03"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.porte == PorteEnum.EPP


def test_build_returns_fornecedor_with_porte_d_when_porte_returned_by_receita_api_is_05():
    adapter = make_adapter(api_response=make_api_response(PORTE="05"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.porte == PorteEnum.D


def test_build_returns_fornecedor_with_porte_none_when_porte_returned_by_receita_api_is_00():
    adapter = make_adapter(api_response=make_api_response(PORTE="00"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.porte is None


# ---------------------------------------------------------------------------
# Opt simples nacional tests
# ---------------------------------------------------------------------------

def test_build_returns_fornecedor_with_opt_simples_nacional_true_when_opt_simples_nacional_returned_by_receita_api_is_true():
    adapter = make_adapter(opt_simples_nacional=True)
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.opt_simples_nacional is True


def test_build_returns_fornecedor_with_opt_simples_nacional_false_when_opt_simples_nacional_returned_by_receita_api_is_false():
    adapter = make_adapter(opt_simples_nacional=False)
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.opt_simples_nacional is False


# ---------------------------------------------------------------------------
# Situacao cadastral tests
# ---------------------------------------------------------------------------

def test_build_returns_fornecedor_with_situacao_cadastral_ativa_when_situacao_cadastral_returned_by_receita_api_is_02():
    adapter = make_adapter(api_response=make_api_response(SIT_CADASTRAL="02"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.situacao_cadastral == SituacaoCadastralEnum.ATIVA


def test_build_returns_fornecedor_with_situacao_cadastral_suspensa_when_situacao_cadastral_returned_by_receita_api_is_03():
    adapter = make_adapter(api_response=make_api_response(SIT_CADASTRAL="03"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.situacao_cadastral == SituacaoCadastralEnum.SUSPENSA


def test_build_returns_fornecedor_with_situacao_cadastral_inapta_when_situacao_cadastral_returned_by_receita_api_is_04():
    adapter = make_adapter(api_response=make_api_response(SIT_CADASTRAL="04"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.situacao_cadastral == SituacaoCadastralEnum.INAPTA


def test_build_returns_fornecedor_with_situacao_cadastral_baixada_when_situacao_cadastral_returned_by_receita_api_is_08():
    adapter = make_adapter(api_response=make_api_response(SIT_CADASTRAL="08"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.situacao_cadastral == SituacaoCadastralEnum.BAIXADA


def test_build_returns_fornecedor_with_situacao_cadastral_nula_when_situacao_cadastral_returned_by_receita_api_is_01():
    adapter = make_adapter(api_response=make_api_response(SIT_CADASTRAL="01"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.situacao_cadastral == SituacaoCadastralEnum.NULA


# ---------------------------------------------------------------------------
# Tipo pessoa tests
# ---------------------------------------------------------------------------

def test_build_returns_fornecedor_with_tipo_pessoa_ci_when_atividade_economica_description_contains_comercio_or_industria():
    adapter = make_adapter(atividade_economica_description="COMERCIO VAREJISTA DE ALIMENTOS")
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.tipo_pessoa == TipoPessoaEnum.CI


def test_build_returns_fornecedor_with_tipo_pessoa_os_when_atividade_economica_description_does_not_contain_comercio_or_industria():
    adapter = make_adapter(atividade_economica_description="SERVICO DE SAUDE")
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.tipo_pessoa == TipoPessoaEnum.OS


# ---------------------------------------------------------------------------
# Cooperativa tests
# ---------------------------------------------------------------------------

def test_build_returns_fornecedor_with_cooperativa_true_when_razao_social_contains_cooperativa_or_coop():
    adapter = make_adapter(api_response=make_api_response(NOME_EMPRESARIAL="COOPERATIVA DE SAUDE LTDA"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.cooperativa is True


def test_build_returns_fornecedor_with_cooperativa_false_when_razao_social_does_not_contain_cooperativa_or_coop():
    adapter = make_adapter(api_response=make_api_response(NOME_EMPRESARIAL="CLINICA CARDIOVIDA LTDA"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.cooperativa is False


# ---------------------------------------------------------------------------
# Codigo retencao tests
# ---------------------------------------------------------------------------

def test_build_returns_fornecedor_with_codigo_retencao_3280_when_cooperativa_is_true():
    adapter = make_adapter(api_response=make_api_response(NOME_EMPRESARIAL="COOPERATIVA DE SAUDE LTDA"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.codigo_retencao == "3280"


def test_build_returns_fornecedor_with_codigo_retencao_1708_when_cooperativa_is_false():
    adapter = make_adapter(api_response=make_api_response(NOME_EMPRESARIAL="CLINICA CARDIOVIDA LTDA"))
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.codigo_retencao == "1708"

# ---------------------------------------------------------------------------
# Tipo contrato social tests
# ---------------------------------------------------------------------------

def test_build_always_returns_fornecedor_with_tipo_contrato_social_juridico():
    adapter = make_adapter()
    result = adapter.build(_CNPJ)
    assert result.dados_cadastrais.tipo_contrato_social == TipoContratoSocialEnum.J

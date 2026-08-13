import pytest
pytestmark = pytest.mark.unit

from app.application.ports import MunicipioLookupPort
from app.domain.entities import Fornecedor
from app.domain.enums import FederacaoEnum, SituacaoCadastralEnum, TipoPessoaEnum, VinculoSebraeEnum
from app.domain.value_objects import CNPJ, Municipio, CodigoMunicipioIBGE
from app.infra.adapters.get_fornecedores_to_update import GetFornecedoresToUpdateViaFornecedoresAPI
from app.infra.api_requester.fornecedores_api_requester import (
    FornecedoresAPIRequester,
    FornecedorToUpdate,
)


def make_fornecedor_to_update(**overrides) -> FornecedorToUpdate:
    data = {
        "LOJA": "01",
        "CODIGO": "000003",
        "NOME": "EQUATORIAL ALAGOAS DISTRIBUIDORA DE ENERGIA S.A.",
        "NOME_FANTASIA": "EQUATORIAL ENERGIA",
        "CPF_CNPJ": "12272084000100",
        "TIPO_FORNEC": "JURIDICA",
        "ENDERECO": "AV FERNANDES LIMA",
        "NUMERO_END": "3349",
        "COMPLEM_END": "",
        "BAIRRO": "FAROL",
        "ESTADO": "ALAGOAS",
        "COD_MUNICIP": "04302",
        "MUNICIPIO": "MACEIO",
        "CEP_FORNEC": "57055000",
        "DDD_FONE": "82",
        "TELEFONE": "33364463",
        "E_MAIL": "",
        "INSCR_ESTAD": "24007177-8",
        "INSCR_MUNIC": "",
        "BLOQUEADO": "NÃO",
        "RELACAO_FOR": "Sem Vínculo",
        "MOTIVO_BLOQ": "",
        "INI_BLOQUEIO": "01/01/1900",
        "FIM_BLOQUEIO": "01/01/1900",
        "ATIVIDA_FOR": "Demais",
        "FOR_SIMPLES": "NÃO",
        "FEDERACAO": "NÃO",
        "COOPERATIVA": "NÃO",
        "TIPO_PESSOA": "Prestação de Serviço",
        "COD_RETENCAO": "1708",
    }
    data.update(overrides)
    return FornecedorToUpdate(**data)


class FakeFornecedoresAPIRequester(FornecedoresAPIRequester):
    def __init__(self, mock_get_fornecedores_to_update: list[FornecedorToUpdate] | None = None):
        self._mock_get_fornecedores_to_update = mock_get_fornecedores_to_update

    def get_fornecedores_to_update(self) -> list[FornecedorToUpdate] | None:
        return self._mock_get_fornecedores_to_update


class FakeMunicipioLookupPort(MunicipioLookupPort):
    def __init__(self, municipio: Municipio | None = None):
        self._municipio = municipio or Municipio(
            nome="MACEIO",
            codigo_ibge=CodigoMunicipioIBGE(value="2704302"),
        )
        self.calls: list[str] = []

    def get(self, municipio_name: str) -> Municipio:
        self.calls.append(municipio_name)
        return self._municipio


def make_adapter(
    fornecedores_to_update: list[FornecedorToUpdate] | None = None,
    municipio_lookup_port: MunicipioLookupPort | None = None,
) -> GetFornecedoresToUpdateViaFornecedoresAPI:
    return GetFornecedoresToUpdateViaFornecedoresAPI(
        fornecedores_api_requester=FakeFornecedoresAPIRequester(fornecedores_to_update),
        municipio_lookup_port=municipio_lookup_port or FakeMunicipioLookupPort(),
    )


def test_should_return_just_fornecedores_with_cnpj_when_some_have_cpf():
    fornecedor_with_cpf = make_fornecedor_to_update(CPF_CNPJ="52998224725")
    fornecedor_with_cnpj = make_fornecedor_to_update(CPF_CNPJ="12272084000100")

    adapter = make_adapter([fornecedor_with_cpf, fornecedor_with_cnpj])

    result = adapter.get()

    assert len(result) == 1
    assert isinstance(result[0], Fornecedor)
    assert result[0].identificacao.cnpj == CNPJ.create(cnpj="12272084000100")


def test_should_return_empty_list_when_all_fornecedores_have_cpfs():
    fornecedor_with_cpf = make_fornecedor_to_update(CPF_CNPJ="52998224725")

    adapter = make_adapter([fornecedor_with_cpf, fornecedor_with_cpf])

    result = adapter.get()

    assert result == []


@pytest.mark.parametrize("mock_value", [None, []])
def test_should_return_empty_list_when_there_are_no_fornecedores_to_update(mock_value):
    adapter = make_adapter(mock_value)

    result = adapter.get()

    assert result == []


def test_should_map_all_fornecedor_fields_correctly():
    fornecedor_to_update = make_fornecedor_to_update()
    municipio_lookup_port = FakeMunicipioLookupPort()

    adapter = make_adapter([fornecedor_to_update], municipio_lookup_port=municipio_lookup_port)

    result = adapter.get()

    assert len(result) == 1
    fornecedor = result[0]

    assert fornecedor.identificacao.cnpj == CNPJ.create(cnpj="12272084000100")
    assert fornecedor.identificacao.razao_social == "EQUATORIAL ALAGOAS DISTRIBUIDORA DE ENERGIA S.A."
    assert fornecedor.identificacao.nome_fantasia == "EQUATORIAL ENERGIA"

    assert fornecedor.endereco.endereco == "AV FERNANDES LIMA"
    assert fornecedor.endereco.numero == "3349"
    assert fornecedor.endereco.bairro == "FAROL"
    assert fornecedor.endereco.uf == "ALAGOAS"
    assert fornecedor.endereco.cep.value == "57055000"
    assert fornecedor.endereco.municipio.nome == "MACEIO"

    assert fornecedor.dados_cadastrais.porte is None
    assert fornecedor.dados_cadastrais.opt_simples_nacional is False
    assert fornecedor.dados_cadastrais.situacao_cadastral == SituacaoCadastralEnum.ATIVA
    assert fornecedor.dados_cadastrais.tipo_pessoa == TipoPessoaEnum.OS
    assert fornecedor.dados_cadastrais.vinculo_sebrae == VinculoSebraeEnum.Z
    assert fornecedor.dados_cadastrais.federacao == FederacaoEnum.NAO
    assert fornecedor.dados_cadastrais.cooperativa is False
    assert fornecedor.dados_cadastrais.codigo_retencao == "1708"

    assert fornecedor.dados_contato.ddd.value == "82"


@pytest.mark.parametrize(
    "motivo_bloq,expected_situacao",
    [
        ("", SituacaoCadastralEnum.ATIVA),
        (" ", SituacaoCadastralEnum.ATIVA),
        ("000009", SituacaoCadastralEnum.INAPTA),
        ("000011", SituacaoCadastralEnum.SUSPENSA),
        ("000010", SituacaoCadastralEnum.BAIXADA),
        ("999999", SituacaoCadastralEnum.SUSPENSA),
        (
            "PORTAL DA TRANSPARÊNCIA: IMPEDIDO DE LICITAR OU CONTRATAR COM O SISTEMA SEBRAE",
            SituacaoCadastralEnum.SUSPENSA,
        ),
    ],
)
def test_should_map_motivo_bloqueio_to_situacao_cadastral(motivo_bloq, expected_situacao):
    fornecedor_to_update = make_fornecedor_to_update(MOTIVO_BLOQ=motivo_bloq)

    adapter = make_adapter([fornecedor_to_update])

    result = adapter.get()

    assert len(result) == 1
    assert result[0].dados_cadastrais.situacao_cadastral == expected_situacao


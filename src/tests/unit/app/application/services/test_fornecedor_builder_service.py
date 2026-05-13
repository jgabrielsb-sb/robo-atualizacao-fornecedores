
import pytest

from app.application.ports import (
    GetOptSimplesNacionalPort,
    GetCartaoCNPJPort,
    GetEnderecoPort
)
\
from app.domain.value_objects import (
    CNPJ, 
    CartaoCNPJ, 
    Endereco, 
    Telefone, 
    CEP, 
    Municipio, 
    CodigoMunicipioIBGE
)

from app.application.services import FornecedorBuilderService
from app.domain.enums import PorteEnum, SituacaoCadastralEnum


def fake_get_opt_simples_nacional(is_opt: bool):
    class FakeGetOptSimplesNacional(GetOptSimplesNacionalPort):
        def __init__(self):
            self._mock_return_value = is_opt

        def get(self, cnpj: CNPJ):
            return self._mock_return_value
    
    return FakeGetOptSimplesNacional()

def fake_get_cartao_cnpj(cartao_cnpj: CartaoCNPJ):
    class FakeGetCartaoCNPJ(GetCartaoCNPJPort):
        def __init__(self):
            self._mock_return_value = cartao_cnpj
        
        def get(self, cnpj: CNPJ):
            return self._mock_return_value

    return FakeGetCartaoCNPJ()

def fake_get_endereco_port(endereco: Endereco):
    class FakeGetEndereco(GetEnderecoPort):
        def __init__(self):
            self._get_times_called = 0
            self._mock_return_value = endereco
        
        def get(self, cnpj: CNPJ):
            self._get_times_called += 1
            return self._mock_return_value

    return FakeGetEndereco()

@pytest.fixture
def endereco() -> Endereco:
    return Endereco.create(
        endereco="test endereco",
        numero="test numero",
        complemento="test complemento",
        cep=CEP.create(cep="31310240"),
        municipio=Municipio.create(nome="Belo Horizonte", codigo_ibge=CodigoMunicipioIBGE.create(ibge_code="3106200")),
    )

@pytest.fixture
def cartao_cnpj_without_endereco() -> CartaoCNPJ:
    return CartaoCNPJ(
        porte=PorteEnum.MEI,
        razao_social="test razao_social",
        situacao_cadastral=SituacaoCadastralEnum.ATIVA,
        atividade_economica_principal_str="test atividade_economica_principal_str",
        natureza_juridica="test natureza_juridica",
        telefone=Telefone.create(value="82988735379"),
        endereco=None
    )

@pytest.fixture
def cartao_cnpj_with_full_endereco(endereco: Endereco) -> CartaoCNPJ:
    return CartaoCNPJ(
        porte=PorteEnum.MEI,
        razao_social="test razao_social",
        situacao_cadastral=SituacaoCadastralEnum.ATIVA,
        atividade_economica_principal_str="test atividade_economica_principal_str",
        natureza_juridica="test natureza_juridica",
        telefone=Telefone.create(value="82988735379"),
        endereco=endereco,
    )

def test_should_return_endereco_from_alternative_souce_if_cartao_cnpj_doesnt_provide_any_endereco_field(
    cartao_cnpj_without_endereco: CartaoCNPJ,
    endereco: Endereco,
):
    service = FornecedorBuilderService(
        get_opt_simples_nacional_port=fake_get_opt_simples_nacional(True),
        get_cartao_cnpj_port=fake_get_cartao_cnpj(cartao_cnpj_without_endereco),
        get_endereco_port=fake_get_endereco_port(endereco),
    )

    result = service.build(CNPJ.create(cnpj="00000000000000"))
    assert result.endereco == endereco

def test_should_return_mixed_endereco_from_alternative_source_and_from_cartao_cnpj_if_cartao_cnpj_doesnt_provide_some_endereco_fields(
    cartao_cnpj_without_endereco: CartaoCNPJ,
    endereco: Endereco,
):
    cartao_cnpj_with_some_endereco_fields = cartao_cnpj_without_endereco.model_copy(
        update={
            "endereco": Endereco.create(
                endereco="test endereco from cartao cnpj",
                numero="test numero from cartao cnpj",
                complemento=None,
                cep=CEP.create(cep="31310240"),
                municipio=Municipio.create(nome="Belo Horizonte", codigo_ibge=CodigoMunicipioIBGE.create(ibge_code="3106200")),
            ),
        }
    )

    assert isinstance(cartao_cnpj_with_some_endereco_fields.endereco, Endereco)

    fake_get_endereco = fake_get_endereco_port(endereco)
    service = FornecedorBuilderService(
        get_opt_simples_nacional_port=fake_get_opt_simples_nacional(True),
        get_cartao_cnpj_port=fake_get_cartao_cnpj(cartao_cnpj_with_some_endereco_fields),
        get_endereco_port=fake_get_endereco,
    )

    result = service.build(CNPJ.create(cnpj="00000000000000"))

    # just the 'complemento' field must be obtained from the get_endereco_port
    assert result.endereco == Endereco(
        endereco="test endereco from cartao cnpj",
        numero="test numero from cartao cnpj",
        complemento="test complemento",
        cep=CEP.create(cep="31310240"),
        municipio=Municipio.create(nome="Belo Horizonte", codigo_ibge=CodigoMunicipioIBGE.create(ibge_code="3106200")),
    )
    assert fake_get_endereco._get_times_called == 1

def test_should_return_fornecedor_with_opt_simples_nacional_false(
    cartao_cnpj_without_endereco: CartaoCNPJ,
    endereco: Endereco,
):
    service = FornecedorBuilderService(
        get_opt_simples_nacional_port=fake_get_opt_simples_nacional(False),
        get_cartao_cnpj_port=fake_get_cartao_cnpj(cartao_cnpj_without_endereco),
        get_endereco_port=fake_get_endereco_port(endereco),
    )

    result = service.build(CNPJ.create(cnpj="00000000000000"))
    assert result.dados_cadastrais.opt_simples_nacional == False

def test_should_not_call_get_endereco_port_if_cartao_cnpj_provides_full_endereco(
    cartao_cnpj_with_full_endereco: CartaoCNPJ,
    endereco: Endereco,
):
    fake_get_endereco = fake_get_endereco_port(endereco)
    
    service = FornecedorBuilderService(
        get_opt_simples_nacional_port=fake_get_opt_simples_nacional(False),
        get_cartao_cnpj_port=fake_get_cartao_cnpj(cartao_cnpj_with_full_endereco),
        get_endereco_port=fake_get_endereco,
    )

    result = service.build(CNPJ.create(cnpj="00000000000000"))
    assert result.endereco == cartao_cnpj_with_full_endereco.endereco
    assert fake_get_endereco._get_times_called == 0

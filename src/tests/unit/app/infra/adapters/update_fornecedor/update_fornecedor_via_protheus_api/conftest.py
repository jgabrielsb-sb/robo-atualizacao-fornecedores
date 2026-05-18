import pytest

from app.domain.entities.fornecedor import (
    Fornecedor,
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
from app.domain.value_objects import (
    CEP,
    CNPJ,
    CodigoMunicipioIBGE,
    DDD,
    Endereco,
    Municipio,
)
from app.infra.adapters.update_fornecedor.update_fornecedor_via_protheus_api.fornecedor_to_protheus_builder import (
    FornecedorToProtheusBuilder,
)

_DEFAULT_ENDERECO = Endereco(
    endereco="RUA TESTE",
    numero="123",
    bairro="CENTRO",
    cep=CEP(value="57020000"),
    municipio=Municipio(
        nome="MACEIO",
        codigo_ibge=CodigoMunicipioIBGE(value="2704302"),
    ),
    uf="AL",
)

_DEFAULT_IDENTIFICACAO = FornecedorIdentificacao(
    cnpj=CNPJ.create("28738609000181"),
    razao_social="EMPRESA TESTE LTDA",
    nome_fantasia="EMPRESA TESTE",
)

_DEFAULT_DADOS_CONTATO = FornecedorDadosContato(ddd=DDD(value="82"))


def make_dados_cadastrais(
    situacao_cadastral: SituacaoCadastralEnum = SituacaoCadastralEnum.ATIVA,
    cooperativa: bool = False,
    codigo_retencao: str = "1708",
    tipo_pessoa: TipoPessoaEnum = TipoPessoaEnum.OS,
    porte: PorteEnum = PorteEnum.ME,
    opt_simples_nacional: bool = False,
) -> FornecedorDadosCadastrais:
    return FornecedorDadosCadastrais(
        porte=porte,
        opt_simples_nacional=opt_simples_nacional,
        situacao_cadastral=situacao_cadastral,
        tipo_pessoa=tipo_pessoa,
        vinculo_sebrae=VinculoSebraeEnum.Z,
        federacao=FederacaoEnum.NAO,
        cooperativa=cooperativa,
        codigo_retencao=codigo_retencao,
    )


def make_fornecedor(
    dados_cadastrais: FornecedorDadosCadastrais | None = None,
) -> Fornecedor:
    return Fornecedor.create(
        endereco=_DEFAULT_ENDERECO,
        identificacao=_DEFAULT_IDENTIFICACAO,
        dados_cadastrais=dados_cadastrais or make_dados_cadastrais(),
        dados_contato=_DEFAULT_DADOS_CONTATO,
    )


@pytest.fixture
def builder() -> FornecedorToProtheusBuilder:
    return FornecedorToProtheusBuilder()

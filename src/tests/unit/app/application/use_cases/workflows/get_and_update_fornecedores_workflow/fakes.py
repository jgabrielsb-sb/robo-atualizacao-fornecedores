from app.application.ports import (
    GetCNPJsToUpdatePort,
    BuildFornecedorPort,
    UpdateFornecedorPort,
)
from app.domain.entities.fornecedor import (
    Fornecedor,
    FornecedorIdentificacao,
    FornecedorDadosCadastrais,
    FornecedorDadosContato,
)
from app.domain.enums import (
    FederacaoEnum,
    PorteEnum,
    SituacaoCadastralEnum,
    TipoPessoaEnum,
    VinculoSebraeEnum,
)
from app.domain.value_objects import CNPJ, Endereco


def make_fake_cnpj(id: int) -> CNPJ:
    return CNPJ(value=f"{id:014d}")


def _make_fornecedor(cnpj: CNPJ) -> Fornecedor:
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


class FakeGetCNPJsToUpdatePort(GetCNPJsToUpdatePort):
    def __init__(
        self,
        cnpjs: list[CNPJ] | None = None,
        error: Exception | None = None,
    ):
        self.cnpjs = cnpjs or []
        self.error = error

    def get(self) -> list[CNPJ]:
        if self.error:
            raise self.error
        return self.cnpjs


class FakeBuildFornecedorPort(BuildFornecedorPort):
    def __init__(self, fail_fornecedores_ids: list[int] | None = None):
        self._fail_fornecedores_ids = fail_fornecedores_ids or []

    def build(self, cnpj: CNPJ) -> Fornecedor:
        id_ = int(cnpj.value)
        if id_ in self._fail_fornecedores_ids:
            raise RuntimeError("Error building fornecedor")
        return _make_fornecedor(cnpj)


class FakeUpdateFornecedorPort(UpdateFornecedorPort):
    def __init__(self, fail_fornecedores_ids: list[int] | None = None):
        self._fail_fornecedores_ids = fail_fornecedores_ids or []

    def update(self, fornecedor: Fornecedor):
        id_ = int(fornecedor.identificacao.cnpj.value)
        if id_ in self._fail_fornecedores_ids:
            raise RuntimeError("Error updating fornecedor")
        return fornecedor

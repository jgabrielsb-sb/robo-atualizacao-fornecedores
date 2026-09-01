from app.application.ports import (
    GetFornecedoresToUpdatePort,
    BuildFornecedorPort,
    UpdateFornecedorPort,
    UpdatedFornecedorRepositoryPort,
)
from app.application.ports.fornecedor.update_fornecedor_port import UpdateFornecedorResult
from app.application.ports.fornecedor.updated_fornecedor_repository_port import PersistUpdatedFornecedorResult
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
from datetime import datetime, timezone


def make_fake_cnpj(id: int) -> CNPJ:
    return CNPJ(value=f"{id:014d}")


def make_fake_fornecedor(id: int) -> Fornecedor:
    return _make_fornecedor(make_fake_cnpj(id))


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


class FakeGetFornecedoresToUpdatePort(GetFornecedoresToUpdatePort):
    def __init__(
        self,
        fornecedores: list[Fornecedor] | None = None,
        error: Exception | None = None,
    ):
        self.fornecedores = fornecedores or []
        self.error = error

    def get(self) -> list[Fornecedor]:
        if self.error:
            raise self.error
        return self.fornecedores


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

    def update(self, fornecedor: Fornecedor) -> UpdateFornecedorResult:
        id_ = int(fornecedor.identificacao.cnpj.value)
        if id_ in self._fail_fornecedores_ids:
            raise RuntimeError("Error updating fornecedor")
        return UpdateFornecedorResult(input={}, output={})


class FakeUpdatedFornecedorRepositoryPort(UpdatedFornecedorRepositoryPort):
    def __init__(self, fail_fornecedores_ids: list[int] | None = None):
        self._fail_fornecedores_ids = fail_fornecedores_ids or []

    def create(self, cnpj: CNPJ) -> PersistUpdatedFornecedorResult:
        id_ = int(cnpj.value)
        if id_ in self._fail_fornecedores_ids:
            raise RuntimeError("Error persisting updated fornecedor")
        now = datetime.now(timezone.utc)
        return PersistUpdatedFornecedorResult(
            id=id_,
            cnpj=cnpj.value,
            step_update_on_ppe_attempt_count=0,
            step_update_on_ppe_status_id=1,
            created_at=now,
            updated_at=now,
        )

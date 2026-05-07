from pydantic import BaseModel

from app.application.ports import (
    GetFornecedoresToUpdatePort,
    BuildFornecedorPort,
    FornecedorRepositoryPort
)


class FakeFornecedorToUpdate(BaseModel):
    id: int

    def __str__(self)-> str:
        return f"FornecedorToUpdate(id_fornecedor={self.id})"

class FakeBuildFornecedorInput(BaseModel):
    id: int

    def __str__(self) -> str:
        return f"FornecedorInput(id_fornecedor={self.id})"

class FakeFornecedor(BaseModel):
    id: int

    def __str__(self) -> str:
        return f"Fornecedor(id_fornecedor={self.id})"

class FakeGetFornecedoresToUpdatePort(GetFornecedoresToUpdatePort):
    def __init__(
        self,
        fornecedores: list[FakeFornecedorToUpdate] | None = None,
        error: Exception | None = None
    ):
        self.fornecedores = fornecedores or []
        self.error = error
        self.called = False

    def get(self):
        self.called = True

        if self.error:
            raise self.error

        return self.fornecedores

class FakeBuildFornecedorPort(BuildFornecedorPort):
    def __init__(self, fail_fornecedores_ids: list[int] = []):
        self._fail_fornecedores_ids = fail_fornecedores_ids
        self._built_fornecedores = []

    def build(self, fornecedor_input: FakeBuildFornecedorInput) -> FakeFornecedor:
        if fornecedor_input.id in self._fail_fornecedores_ids:
            raise RuntimeError('Error building Fornecedor')

        fornecedor = FakeFornecedor(id=fornecedor_input.id)
        self._built_fornecedores.append(fornecedor)
        return fornecedor

class FakeFornecedorRepositoryPort(FornecedorRepositoryPort):
    def __init__(self, fail_fornecedores_ids: list[int] = []):
        self._fail_fornecedores_ids = fail_fornecedores_ids
        self._updated_fornecedores = []

    def create(self):
        pass

    def update(self, fornecedor: FakeFornecedor):
        if fornecedor.id in self._fail_fornecedores_ids:
            raise RuntimeError('Error updating fornecedor')

        self._updated_fornecedores.append(fornecedor)
        return fornecedor

from pydantic import BaseModel

from app.domain.value_objects import CNPJ

class FornecedorToUpdate(BaseModel):
    cnpj: CNPJ

    def __str__(self) -> str:
        return f"FornecedorToUpdate(cnpj={self.cnpj})"

if __name__ == "__main__":
    fornecedor = FornecedorToUpdate(cnpj=CNPJ.create("12345678901234"))
    print(fornecedor)
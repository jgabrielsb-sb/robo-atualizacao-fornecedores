import requests
from http import HTTPStatus

from pydantic import BaseModel
from app.domain.value_objects import CodigoMunicipioIBGE, Municipio
from app.infra.api_requester.exceptions import NotFoundError, APIRequesterException

class FornecedorToUpdate(BaseModel):
    loja: str
    codigo: str
    nome: str
    nome_fantasia: str
    cpf_cnpj: str

class FornecedoresAPIRequester:
    def __init__(
        self,
        base_url: str,
    ):
        self._base_url = base_url

    def get_municipio_by_name(self, municipio_name: str) -> Municipio:
        url = f"{self._base_url}/api/v1/municipios/name/{municipio_name}"

        response = requests.get(url)
        data = response.json()
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            return Municipio(
                nome=municipio_name,
                codigo_ibge=CodigoMunicipioIBGE.create(
                    ibge_code=data["codigo_ibge"]
                ),
            )
        elif status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundError(f"Municipio not found by name: {municipio_name}")
        else:
            raise APIRequesterException(f"Failed to get municipio by name: {status_code}")

    def get_fornecedores_to_update(self) -> list[FornecedorToUpdate] | None:
        url = f"{self._base_url}/api/v1/fornecedores-to-update"
        response = requests.get(url)
        data = response.json()
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            return [FornecedorToUpdate(**fornecedor) for fornecedor in data]
        else:
            raise APIRequesterException(f"Failed to get fornecedores to update: {status_code}")

if __name__ == "__main__":
    fornecedores_api_requester = FornecedoresAPIRequester(
        base_url="http://localhost:8000"
    )
    municipio = fornecedores_api_requester.get_municipio_by_name("SãoPaulo")
    print(municipio)
        


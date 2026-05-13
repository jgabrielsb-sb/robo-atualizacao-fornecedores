import requests
from http import HTTPStatus

from pydantic import BaseModel
from app.domain.value_objects import CodigoMunicipioIBGE, Municipio
from app.infra.api_requester.exceptions import NotFoundError, APIRequesterException

class FornecedorToUpdate(BaseModel):
    LOJA: str
    CODIGO: str
    NOME: str
    NOME_FANTASIA: str
    CPF_CNPJ: str

class FornecedoresAPIRequester:
    def __init__(
        self,
        base_url: str,
    ):
        self._base_url = base_url

    def get_municipio_by_name(self, municipio_name: str) -> Municipio:
        """
        Method for getting a municipio by name.
        Returns a Municipio object or raises a NotFoundError 
        if the municipio is not found.
        :raises NotFoundError: if the municipio is not found.
        :raises APIRequesterException: if the request fails.
        :params return: Municipio
        """
        url = f"{self._base_url}/api/v1/municipios/name/{municipio_name}"
        response = requests.get(url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            data = response.json() # get json only after status_code == 200
            return Municipio(
                nome=municipio_name,
                codigo_ibge=CodigoMunicipioIBGE.create(
                    ibge_code=data["codigo_ibge"]
                ),
            )
        elif status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundError(f"Municipio not found by name: {municipio_name}")
        else:
            raise APIRequesterException(
                f"Failed to get municipio by_name: {municipio_name}"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text}"
            )

    def get_fornecedores_to_update(self) -> list[FornecedorToUpdate] | None:
        """
        Method for getting all the fornecedores that must be updated.
        Returns a list of FornecedorToUpdate objects or an empty list 
        if there are no fornecedores to update.

        :raises APIRequesterException: if the request fails.
        :params return: list[FornecedorToUpdate] | None
        """
        url = f"{self._base_url}/api/v1/fornecedores-to-update"
        response = requests.get(url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            data = response.json() # get json only after status_code == 200
            return [FornecedorToUpdate(**fornecedor) for fornecedor in data]
        else:
            raise APIRequesterException(
                f"Failed to get fornecedores to update \n"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text}"
            )


        


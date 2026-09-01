from datetime import datetime
from enum import Enum
from typing import Optional

import requests
from http import HTTPStatus

from pydantic import BaseModel
from app.domain.value_objects import CodigoMunicipioIBGE, Municipio
from app.infra.api_requester.exceptions import (
    NotFoundError,
    APIRequesterException,
    UnprocessableEntityError,
    ForbiddenError,
)

class FornecedorToUpdate(BaseModel):
    LOJA: str
    CODIGO: str
    NOME: str
    NOME_FANTASIA: str
    CPF_CNPJ: str
    TIPO_FORNEC: str
    ENDERECO: str
    NUMERO_END: str
    COMPLEM_END: str
    BAIRRO: str
    ESTADO: str
    COD_MUNICIP: str
    MUNICIPIO: str
    CEP_FORNEC: str
    DDD_FONE: str
    TELEFONE: str
    E_MAIL: str
    INSCR_ESTAD: str
    INSCR_MUNIC: str
    BLOQUEADO: str
    RELACAO_FOR: str
    MOTIVO_BLOQ: str
    INI_BLOQUEIO: str
    FIM_BLOQUEIO: str
    ATIVIDA_FOR: str
    FOR_SIMPLES: str
    FEDERACAO: str
    COOPERATIVA: str
    TIPO_PESSOA: str
    COD_RETENCAO: str

class Cnae(BaseModel):
    id: int
    code: str
    description: str

class AtualizacaoFornecedor(BaseModel):
    id: int
    cnpj: str
    step_update_on_ppe_last_attempted_at: Optional[datetime] = None
    step_update_on_ppe_last_error_message: Optional[str] = None
    step_update_on_ppe_attempt_count: int
    step_update_on_ppe_status_id: int
    created_at: datetime
    updated_at: datetime

class AttemptStatus(str, Enum):
    ERROR = "ERROR"
    SUCCESSFULL = "SUCCESSFULL"

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
        url = f"{self._base_url}/v1/municipios/name/{municipio_name}"
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
        url = f"{self._base_url}/v1/fornecedores-to-update/all"
        response = requests.get(url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            data = response.json() # get json only after status_code == 200
            return [FornecedorToUpdate(**fornecedor) for fornecedor in data]
        else:
            raise APIRequesterException(
                f"Failed to get fornecedores to update \n"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text} \n"
                f"URL: {url}"
            )

    def get_fornecedor_to_update_by_cpf_cnpj(self, cpf_cnpj: str) -> FornecedorToUpdate:
        """
        Method for getting a single fornecedor to update by its CPF/CNPJ.
        Returns a FornecedorToUpdate object.

        :raises NotFoundError: if the fornecedor is not found.
        :raises APIRequesterException: if the request fails.
        :params return: FornecedorToUpdate
        """
        url = f"{self._base_url}/v1/fornecedores-to-update/cpf-cnpj/{cpf_cnpj}"
        response = requests.get(url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            data = response.json() # get json only after status_code == 200
            return FornecedorToUpdate(**data)
        elif status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundError(f"Fornecedor to update not found by CPF/CNPJ: {cpf_cnpj}")
        else:
            raise APIRequesterException(
                f"Failed to get fornecedor to update by CPF/CNPJ: {cpf_cnpj} \n"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text} \n"
                f"URL: {url}"
            )

    def create_atualizacao_fornecedor(self, cnpj: str) -> AtualizacaoFornecedor:
        """
        Method for registering a fornecedor update occurrence.
        Returns the created AtualizacaoFornecedor record.

        :raises UnprocessableEntityError: if the payload is rejected by the API.
        :raises APIRequesterException: if the request fails.
        :params return: AtualizacaoFornecedor
        """
        url = f"{self._base_url}/v1/atualizacoes-fornecedores/"
        response = requests.post(url, json={"cnpj": cnpj})
        status_code = response.status_code

        if status_code == HTTPStatus.CREATED:
            data = response.json() # get json only after status_code == 201
            return AtualizacaoFornecedor(**data)
        elif status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            raise UnprocessableEntityError(
                f"Failed to create atualizacao fornecedor for CNPJ: {cnpj} \n"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text}"
            )
        else:
            raise APIRequesterException(
                f"Failed to create atualizacao fornecedor for CNPJ: {cnpj} \n"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text} \n"
                f"URL: {url}"
            )

    def get_atualizacoes_fornecedores_pending_update_on_ppe(self) -> list[AtualizacaoFornecedor]:
        """
        Method for getting the atualizacoes_fornecedores pending the update_on_ppe stage.
        Returns a list of AtualizacaoFornecedor objects or an empty list if there are none.

        :raises APIRequesterException: if the request fails.
        :params return: list[AtualizacaoFornecedor]
        """
        url = f"{self._base_url}/v1/atualizacoes-fornecedores/to-update-on-ppe"
        response = requests.get(url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            data = response.json() # get json only after status_code == 200
            return [AtualizacaoFornecedor(**item) for item in data]
        else:
            raise APIRequesterException(
                f"Failed to get atualizacoes fornecedores pending update_on_ppe \n"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text} \n"
                f"URL: {url}"
            )

    def register_update_on_ppe_attempt(
        self,
        id: int,
        status: AttemptStatus,
        why_error: Optional[str] = None,
    ) -> AtualizacaoFornecedor:
        """
        Method for registering an attempt of the update_on_ppe stage.
        Returns the updated AtualizacaoFornecedor record.

        :raises NotFoundError: if the atualizacao fornecedor is not found.
        :raises ForbiddenError: if the update_on_ppe stage is already finished.
        :raises UnprocessableEntityError: if the payload is rejected by the API.
        :raises APIRequesterException: if the request fails.
        :params return: AtualizacaoFornecedor
        """
        url = f"{self._base_url}/v1/atualizacoes-fornecedores/{id}/update-on-ppe-attempt"
        payload = {"status": status.value}
        if why_error is not None:
            payload["why_error"] = why_error

        response = requests.post(url, json=payload)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            data = response.json() # get json only after status_code == 200
            return AtualizacaoFornecedor(**data)
        elif status_code == HTTPStatus.FORBIDDEN:
            raise ForbiddenError(
                f"Cannot register update_on_ppe attempt for id {id}: stage already finished \n"
                f"Response text: {response.text}"
            )
        elif status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundError(f"Atualizacao fornecedor not found by id: {id}")
        elif status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            raise UnprocessableEntityError(
                f"Failed to register update_on_ppe attempt for id {id} \n"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text}"
            )
        else:
            raise APIRequesterException(
                f"Failed to register update_on_ppe attempt for id {id} \n"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text} \n"
                f"URL: {url}"
            )

    def get_cnae_by_code(self, code: str) -> Cnae:
        """
        :raises NotFoundError: if the CNAE is not found.
        :raises APIRequesterException: if the request fails.
        """
        url = f"{self._base_url}/v1/cnaes/code/{code}"
        response = requests.get(url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            data = response.json()
            return Cnae(**data)
        elif status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundError(f"CNAE not found by code: --{code}--")
        else:
            raise APIRequesterException(
                f"Failed to get CNAE by code: {code} \n"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text}"
            )




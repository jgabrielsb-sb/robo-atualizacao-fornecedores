import requests
from http import HTTPStatus
from pydantic import BaseModel
from typing import Optional

from app.domain.value_objects import CNPJ
from app.infra.api_requester.exceptions import APIRequesterException, NotFoundError

class ReceitaAPIGetCompanyResponse(BaseModel):
    CNPJ: str  
    NOME_EMPRESARIAL: str
    NOME_FANTASIA: Optional[str] = None
    SIT_CADASTRAL: str
    MOT_SIT_CADASTAL: Optional[str] = None
    DT_SIT_CADASTAL: Optional[int] = None
    DT_ABERTURA_ESTAB: Optional[int] = None
    CNAE_PRINCIPAL_COD: str
    END_UF: Optional[str] = None
    OPCAO_MEI: Optional[str] = None
    PORTE: str
    LISTA_QSA_SOCIO_NOME: Optional[str] = None
    END_TIPO_LOGRADOURO: Optional[str] = None
    END_LOGRADOURO: Optional[str] = None
    END_NUMERO: Optional[str] = None
    END_COMPLEMENTO: Optional[str] = None   
    END_BAIRRO: Optional[str] = None
    END_CEP: Optional[str] = None
    END_MUNICIPIO: Optional[str] = None
    DDD1: Optional[str] = None
    TELEFONE1: Optional[str] = None
    DDD2: Optional[str] = None
    TELEFONE2: Optional[str] = None
    EMAIL: Optional[str] = None
    RESPONSAVEL_CPF: Optional[str] = None
    RESPONSAVEL_NOME: Optional[str] = None
    HASH: Optional[str] = None

class ReceitaAPIRequester:
    def __init__(
        self,
        base_url: str,
    ):
        self._base_url = base_url

    def get_company(
        self,
        cnpj: CNPJ
    ) -> ReceitaAPIGetCompanyResponse:
        """
        Gets the company by cnpj using the Receita API.

        :param cnpj: The cnpj of the company.
        :type cnpj: CNPJ
        
        :return: The company.
        :rtype: ReceitaAPIGetCompanyResponse
        :raises RouteNotFoundError: If the route is not found.
        :raises NotFoundError: If the company is not found.
        :raises UnexpectedError: If an unexpected error occurs.
        """
        url = f"{self._base_url}/receita/api/v1/empresa-receita/get-by-cnpj/{cnpj.value}"
        response = requests.get(url)
        status_code = response.status_code

        if status_code == HTTPStatus.OK:
            data = response.json()
            return ReceitaAPIGetCompanyResponse.model_validate(data)
        elif status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundError(
                f"Company with CNPJ {cnpj.value} not found"
            )
        
        raise APIRequesterException(
                f"Failed to get company by CNPJ: {cnpj.value}"
                f"Status Code: {status_code} \n"
                f"Response text: {response.text}"
            )

from http import HTTPStatus

import requests

from app.infra.api_requester.exceptions import APIRequesterException
from app.infra.api_requester.protheus_api_requester.models import (
    FornecedorUpdateOnProtheus,
    ProtheusUpdateResult,
    TipoOperacaoProtheus,
)




class ProtheusUpdateError(APIRequesterException):
    pass


class ProtheusAPIRequester:
    _ENDPOINT = "/REST/APIPROTHEUSDB/INCLUIRFORNECEDOR"

    def __init__(
        self,
        base_url: str,
        c_auth: str,
        authorization_token: str,
    ):
        self._base_url = base_url
        self._c_auth = c_auth
        self._headers = {
            "Authorization": f"BASIC {authorization_token}",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }

    def update_fornecedor(
        self,
        fornecedor: FornecedorUpdateOnProtheus,
    ) -> ProtheusUpdateResult:
        url = f"{self._base_url}{self._ENDPOINT}"

        payload = fornecedor.model_dump()
        payload["cAuth"] = self._c_auth
        payload["Tipo_Ope"] = TipoOperacaoProtheus.ALTERACAO.value
        response = requests.post(
            url,
            headers=self._headers,
            json=payload,
            timeout=30,
            verify=False,
        )

        if response.status_code != HTTPStatus.CREATED:
            raise APIRequesterException(
                f"Protheus API returned unexpected HTTP {response.status_code}. "
                f"Response: {response.text}"
            )

        data = response.json()
        
        if not data.get("sucesso"):
            descr_erro = data.get("descr_erro", "")
            raise ProtheusUpdateError(
                f"Protheus refused update for CNPJ_For={fornecedor.CNPJ_For}: {descr_erro}"
            )

        return ProtheusUpdateResult(
            codigo_for=data["codigo_for"],
            loja_forne=data["loja_forne"],
        )

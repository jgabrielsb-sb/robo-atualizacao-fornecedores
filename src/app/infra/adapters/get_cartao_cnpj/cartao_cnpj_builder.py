from typing import Any, Dict, Optional

from app.domain.enums import PorteEnum, SituacaoCadastralEnum
from app.application.ports import MunicipioLookupPort
from app.infra.adapters.exceptions import ErrorWhileGettingExternalDataError

from app.domain.value_objects import (
    Endereco,
    Municipio,
    CEP,
    CartaoCNPJ,
    Telefone,
)


_MAP_PORTE = {
    "ME": PorteEnum.ME,
    "EPP": PorteEnum.EPP,
    "EIRELI": PorteEnum.EIRELI,
    "EP": PorteEnum.EP,
    "N": PorteEnum.N,
    "PF": PorteEnum.PF,
    "SFL": PorteEnum.SFL,
    "DEMAIS": PorteEnum.D,
    "MEI": PorteEnum.MEI,
}

# Maps English registration status values (format 2) to Portuguese (format 1 / domain).
_REGISTRATION_STATUS_EN_TO_PT = {
    "ACTIVE": "ATIVA",
    "INACTIVE": "BAIXADA",
    "SUSPENDED": "SUSPENSA",
    "UNFIT": "INAPTA",
}


def _map_porte(size: str) -> PorteEnum:
    porte_enum = _MAP_PORTE.get(size)
    if not porte_enum:
        raise ValueError(f"Could not map porte to a valid PorteEnum: {size}")
    return porte_enum


class CartaoCNPJBuilder:
    def __init__(
        self,
        municipio_lookup_port: MunicipioLookupPort,
    ):
        self._municipio_lookup_port = municipio_lookup_port

    def _get_municipio(self, municipio_name: str) -> Municipio:
        try:
            return self._municipio_lookup_port.get(municipio_name.upper())
        except Exception as e:
            raise ErrorWhileGettingExternalDataError(f"Failed to get municipio: {e}") from e

    def _get_endereco(self, address: Dict[str, Any]) -> Endereco:
        cep = CEP.create(cep=address["zip_code"]) if address["zip_code"] else None
        municipio = self._get_municipio(address["city"]) if address["city"] else None

        return Endereco.create(
            endereco=address["street"],
            numero=address["number"],
            complemento=address["complement"],
            bairro=address["neighborhood"],
            cep=cep,
            municipio=municipio,
        )

    def _get_telefone(self, phone: str) -> Telefone:
        if "/" in phone:
            phone = phone.split("/")[0]
        return Telefone.create(value=phone)

    def _get_situacao_cadastral(self, registration_status: Any) -> SituacaoCadastralEnum:
        if isinstance(registration_status, dict):
            status_str = registration_status["status"]
        else:
            status_str = _REGISTRATION_STATUS_EN_TO_PT.get(registration_status, registration_status)
        return SituacaoCadastralEnum.from_value(status_str)

    def _get_primary_activity_description(self, data: Dict[str, Any]) -> Optional[str]:
        if "primary_activity" in data:
            return data["primary_activity"]["description"]
        primary = next(
            (a for a in data.get("company_activities", []) if a.get("type") == "PRIMARY"),
            None,
        )
        return primary["description"] if primary else None

    def _get_phone(self, data: Dict[str, Any]) -> Optional[str]:
        if "contact" in data:
            return data["contact"]["phone"]
        phone_contact = next(
            (c for c in data.get("contacts", []) if c.get("type") == "PHONE"),
            None,
        )
        return phone_contact["value"] if phone_contact else None

    def build(self, response: Dict[str, Any]) -> CartaoCNPJ:
        data = response["data"]
        phone = self._get_phone(data)
        return CartaoCNPJ(
            porte=_map_porte(data["size"]),
            razao_social=data["legal_name"],
            nome_fantasia=data["trade_name"],
            atividade_economica_principal_str=self._get_primary_activity_description(data),
            endereco=self._get_endereco(data["address"]),
            telefone=self._get_telefone(phone) if phone else None,
            natureza_juridica=data["legal_nature"]["description"],
            situacao_cadastral=self._get_situacao_cadastral(data["registration_status"]),
        )

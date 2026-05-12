from pydantic import BaseModel
from typing import Optional
from app.domain.enums import PorteEnum
from app.domain.value_objects import Endereco

class CartaoCNPJ(BaseModel):
    porte: Optional[PorteEnum] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    atividade_economica_principal_str: Optional[str] = None
    endereco: Optional[Endereco] = None
    telefone: Optional[str] = None
    natureza_juridica: Optional[str] = None
    natureza_juridica_code: Optional[str] = None
    situacao_cadastral: Optional[str] = None

from pydantic import BaseModel
from typing import Optional
from app.domain.enums import PorteEnum, SituacaoCadastralEnum
from app.domain.value_objects.endereco_value_object import Endereco
from app.domain.value_objects.telefone_value_object import Telefone


class CartaoCNPJ(BaseModel):
    porte: PorteEnum
    razao_social: str
    situacao_cadastral: SituacaoCadastralEnum
    atividade_economica_principal_str: Optional[str]
    natureza_juridica: str
    telefone: Telefone
    nome_fantasia: Optional[str] = None
    endereco: Optional[Endereco] = None
    
    
    

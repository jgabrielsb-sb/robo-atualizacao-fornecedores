from enum import Enum

class SituacaoCadastralEnum(str, Enum):
    ATIVA = "ATIVA"
    INAPTA = "INAPTA"
    SUSPENSA = "SUSPENSA"
    BAIXADA = "BAIXADA"
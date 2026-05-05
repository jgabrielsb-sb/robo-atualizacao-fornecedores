from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SituacaoCadastral:
    ativo: bool
    bloqueado: bool
    motivo_bloqueio: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.ativo, bool):
            raise TypeError("ativo must be a boolean")
        if not isinstance(self.bloqueado, bool):
            raise TypeError("bloqueado must be a boolean")
        if self.motivo_bloqueio and not isinstance(self.motivo_bloqueio, str):
            raise TypeError("motivo_bloqueio must be a string")

    @classmethod
    def create(
        cls,
        *,
        ativo: bool,
        bloqueado: bool,
        motivo_bloqueio: Optional[str] = None,
    ) -> 'SituacaoCadastral':
        return cls(
            ativo=ativo, 
            bloqueado=bloqueado, 
            motivo_bloqueio=motivo_bloqueio
        )
        

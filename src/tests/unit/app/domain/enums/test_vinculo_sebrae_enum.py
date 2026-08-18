import pytest
pytestmark = pytest.mark.unit

from app.domain.enums import VinculoSebraeEnum, InvalidVinculoSebraeError


VALID_VINCULO_SEBRAE_VALUES = [
    # CONSELHEIRO
    "CONSELHEIRO",
    "  CONSELHEIRO",
    "CONSELHEIRO  ",
    # DIRETOR
    "DIRETOR",
    "  DIRETOR",
    "DIRETOR  ",
    # FUNCIONARIO — with and without accent on Á
    "FUNCIONARIO",
    "FUNCIONÁRIO",
    "  FUNCIONARIO",
    "FUNCIONARIO  ",
    # GERENTE
    "GERENTE",
    "  GERENTE",
    "GERENTE  ",
    # ESTAGIARIO — with and without accent on Á
    "ESTAGIARIO",
    "ESTAGIÁRIO",
    "  ESTAGIARIO",
    "ESTAGIARIO  ",
    # SEM VINCULO — with and without accent on Í
    "SEM VINCULO",
    "SEM VÍNCULO",
    "  SEM VINCULO",
    "SEM VINCULO  ",
    VinculoSebraeEnum.C,
    VinculoSebraeEnum.D,
    VinculoSebraeEnum.F,
    VinculoSebraeEnum.G,
    VinculoSebraeEnum.E,
    VinculoSebraeEnum.Z,
    VinculoSebraeEnum.C.value,
    VinculoSebraeEnum.D.value,
    VinculoSebraeEnum.F.value,
    VinculoSebraeEnum.G.value,
    VinculoSebraeEnum.E.value,
    VinculoSebraeEnum.Z.value,
]

INVALID_VINCULO_SEBRAE_VALUES = [
    "CONSULTOR",
    "FUNCIONARIO_GERENTE",
    "SEM_VINCULO",
    "ESTAGIARIO_FUNCIONARIO",
    "DIRETOR GERENTE",
    "CONSELHEIRO DIRETOR",
    "VINCULO",
    "SEM",
]


@pytest.mark.parametrize("value", VALID_VINCULO_SEBRAE_VALUES)
def test_vinculo_sebrae_enum_accepts_valid_values(value):
    vinculo = VinculoSebraeEnum.from_value(value)
    assert isinstance(vinculo, VinculoSebraeEnum)


@pytest.mark.parametrize("value", INVALID_VINCULO_SEBRAE_VALUES)
def test_vinculo_sebrae_enum_raises_error_for_invalid_values(value):
    with pytest.raises(InvalidVinculoSebraeError):
        VinculoSebraeEnum.from_value(value)

import pytest
pytestmark = pytest.mark.unit

from app.domain.enums import PorteEnum, InvalidPorteError


VALID_PORTE_VALUES = [
    # EIRELI
    "EMPRESA INDIVIDUAL DE RESPONSABILIDADE LIMITADA",
    "  EMPRESA INDIVIDUAL DE RESPONSABILIDADE LIMITADA",
    "EMPRESA INDIVIDUAL DE RESPONSABILIDADE LIMITADA  ",
    # EP — with and without accent on Ú
    "EMPRESA PUBLICA",
    "EMPRESA PÚBLICA",
    "  EMPRESA PUBLICA",
    "EMPRESA PUBLICA  ",
    # EPP
    "EMPRESA DE PEQUENO PORTE",
    "  EMPRESA DE PEQUENO PORTE  ",
    # ME
    "MICRO EMPRESA",
    "  MICRO EMPRESA",
    "MICRO EMPRESA  ",
    # MEI
    "MICROEMPREENDEDOR INDIVIDUAL",
    "MICROEMPREENDEDOR INDIVIDUAL  ",
    # N
    "NORMAL",
    "  NORMAL",
    "NORMAL  ",
    # PF — with and without accent on Í
    "PESSOA FISICA",
    "PESSOA FÍSICA",
    "  PESSOA FISICA",
    "PESSOA FISICA  ",
    # SFL
    "SEM FINS LUCRATIVOS",
    "  SEM FINS LUCRATIVOS",
    "SEM FINS LUCRATIVOS  ",
    # D
    "DEMAIS",
    "  DEMAIS",
    "DEMAIS  ",
    PorteEnum.EIRELI,
    PorteEnum.EP,
    PorteEnum.EPP,
    PorteEnum.ME,
    PorteEnum.MEI,
    PorteEnum.N,
    PorteEnum.PF,
    PorteEnum.SFL,
    PorteEnum.D,
    PorteEnum.EIRELI.value,
    PorteEnum.EP.value,
    PorteEnum.EPP.value,
    PorteEnum.ME.value,
    PorteEnum.MEI.value,
    PorteEnum.N.value,
    PorteEnum.PF.value,
    PorteEnum.SFL.value,
    PorteEnum.D.value,
]

INVALID_PORTE_VALUES = [
    "EMPRESA",
    "PUBLICA",
    "MICRO",
    "PESSOA",
    "EMPRESA_PUBLICA",
    "MICRO_EMPRESA",
    "PESSOA_FISICA",
    "GRANDE EMPRESA",
    "EMPRESA PUBLICA EMPRESA",
    "NORMAL DEMAIS",
]


@pytest.mark.parametrize("value", VALID_PORTE_VALUES)
def test_porte_enum_accepts_valid_values(value):
    porte = PorteEnum.from_value(value)
    assert isinstance(porte, PorteEnum)


@pytest.mark.parametrize("value", INVALID_PORTE_VALUES)
def test_porte_enum_raises_error_for_invalid_values(value):
    with pytest.raises(InvalidPorteError):
        PorteEnum.from_value(value)

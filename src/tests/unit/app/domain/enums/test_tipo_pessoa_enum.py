import pytest
pytestmark = pytest.mark.unit

from app.domain.enums import TipoPessoaEnum, InvalidTipoPessoaError


VALID_TIPO_PESSOA_VALUES = [
    # CI — with and without accents on É / Ú
    "COMERCIO/INDUSTRIA",
    "COMÉRCIO/INDÚSTRIA",
    "COMÉRCIO/INDUSTRIA",
    "  COMERCIO/INDUSTRIA",
    "COMERCIO/INDUSTRIA  ",
    # PF — with and without accent on Í
    "PESSOA FISICA",
    "PESSOA FÍSICA",
    "  PESSOA FISICA",
    "PESSOA FISICA  ",
    # OS — stored as "PRESTAÇAO DE SERVIÇO"; all accent combos should match
    "PRESTAÇAO DE SERVIÇO",
    "PRESTAÇÃO DE SERVIÇO",
    "PRESTACAO DE SERVICO",
    "PRESTAÇÃO DE SERVICO",
    "PRESTAÇAO DE SERVICO",
    "  PRESTACAO DE SERVICO",
    "PRESTACAO DE SERVICO  ",
    TipoPessoaEnum.CI,
    TipoPessoaEnum.PF,
    TipoPessoaEnum.OS,
    TipoPessoaEnum.CI.value,
    TipoPessoaEnum.PF.value,
    TipoPessoaEnum.OS.value,
]

INVALID_TIPO_PESSOA_VALUES = [
    "COMERCIO",
    "INDUSTRIA",
    "PESSOA",
    "FISICA",
    "PRESTACAO",
    "PESSOA_FISICA",
    "COMERCIO/INDUSTRIA/SERVICO",
    "PRESTACAO DE SERVICO EXTRA",
    "COMERCIO INDUSTRIA",
]


@pytest.mark.parametrize("value", VALID_TIPO_PESSOA_VALUES)
def test_tipo_pessoa_enum_accepts_valid_values(value):
    tipo = TipoPessoaEnum.from_value(value)
    assert isinstance(tipo, TipoPessoaEnum)


@pytest.mark.parametrize("value", INVALID_TIPO_PESSOA_VALUES)
def test_tipo_pessoa_enum_raises_error_for_invalid_values(value):
    with pytest.raises(InvalidTipoPessoaError):
        TipoPessoaEnum.from_value(value)

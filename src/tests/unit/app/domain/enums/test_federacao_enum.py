import pytest

from app.domain.enums import FederacaoEnum, InvalidFederacaoError

valid_values = [
        "NAO",
        "NÃO",
        "NAO   ",
        "    NAO",
        "FEDERACAO",
        "FEDERAÇÃO",
        "FEDERAÇAO",
        "CONFEDERACAO",
        "CONFEDERAÇÃO",
        "CONFEDERAÇAO",
        "CONFEDERACAO  ",
        FederacaoEnum.NAO,
        FederacaoEnum.FEDERACAO,
        FederacaoEnum.CONFEDERACAO,
        FederacaoEnum.NAO.value,
        FederacaoEnum.FEDERACAO.value,
        FederacaoEnum.CONFEDERACAO.value,
    ]

INVALID_FEDERACAO_VALUES = [
    "NAO_FEDERACAO",
    "FEDERACAO_NAO",
    "CONFEDERACAO_NAO",
    "FEDERACAO_CONFEDERACAO",
    "CONFEDERACAO_FEDERACAO",
    "FEDERACAO_CONFEDERACAO_NAO",
    "CONFEDERACAO_FEDERACAO_NAO",
]

@pytest.mark.parametrize("value", valid_values)
def test_federacao_enum_accepts_valid_values(value):
    federacao = FederacaoEnum.from_value(value)
    assert isinstance(federacao, FederacaoEnum)
    
@pytest.mark.parametrize("value", INVALID_FEDERACAO_VALUES)
def test_federacao_enum_raises_error_for_invalid_values(value):
    with pytest.raises(InvalidFederacaoError):
        FederacaoEnum.from_value(value)
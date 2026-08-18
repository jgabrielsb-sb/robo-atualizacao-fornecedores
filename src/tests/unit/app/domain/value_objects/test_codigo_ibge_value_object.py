import pytest
pytestmark = pytest.mark.unit

from app.domain.value_objects import CodigoMunicipioIBGE, InvalidCodigoMunicipioIBGECodeLengthError


VALID_IBGE_MUNICIPIO_CODE_VARIATIONS = [
    "1200013 ",
    "1200054",
    "1200104",
    "1200138 ",
    "1200179  ",
    "1200203",
    "1200252  ",
    " 1200302",
    "1200328",
    "  1200336",
    "1200344",
    "1200351",
    "    1200385",
    "1200807",
    "1200393",
    "1200401",
    "1200427",
    "1200435",
    "1200500",
    "1200450",
    "1200609",
    "1200708",
    "2701605",
    "2701704",
    "2701803",
]


INVALID_IBGE_MUNICIPIO_CODES_WITH_EXTRA_DIGIT = [
    "27043020",
    " 27043020 ",
    "270 43020",
    "270-43020",
    "270.43020",
    "270/43020",
    "270_43020",
    "27 043 020",
    "27-043-020",
    "27.043.020",
    "27/043/020",
]


INVALID_IBGE_MUNICIPIO_CODES_WITH_MISSING_DIGIT = [
    "270430",
    " 270430 ",
    "270 430",
    "270-430",
    "270.430",
    "270/430",
    "270_430",
    "27 043 0",
    "27-043-0",
    "27.043.0",
    "27/043/0",
]


@pytest.mark.parametrize("ibge_code_input", VALID_IBGE_MUNICIPIO_CODE_VARIATIONS)
def test_should_create_ibge_municipio_code_from_valid_codes(ibge_code_input):
    ibge_code = CodigoMunicipioIBGE.create(ibge_code_input)
    assert ibge_code.value == ibge_code_input

@pytest.mark.parametrize(
    "ibge_code_input",
    INVALID_IBGE_MUNICIPIO_CODES_WITH_EXTRA_DIGIT,
)
def test_should_raise_when_ibge_municipio_code_has_more_than_7_digits(
    ibge_code_input,
):
    with pytest.raises(InvalidCodigoMunicipioIBGECodeLengthError):
        CodigoMunicipioIBGE.create(ibge_code_input)

@pytest.mark.parametrize(
    "ibge_code_input",
    INVALID_IBGE_MUNICIPIO_CODES_WITH_MISSING_DIGIT,
)
def test_should_raise_when_ibge_municipio_code_has_less_than_7_digits(
    ibge_code_input,
):
    with pytest.raises(InvalidCodigoMunicipioIBGECodeLengthError):
        CodigoMunicipioIBGE.create(ibge_code_input)

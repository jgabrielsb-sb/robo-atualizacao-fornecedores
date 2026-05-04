import pytest

from app.domain.value_objects import CEP, InvalidCEPLengthError


VALID_CEP_VARIATIONS = [
    "57020-565",
    "57020565",
    "57020 565",
    "57020.565",
    "57020/565",
    "57020_565",
    "57020-565 ",
    " 57020-565",
    " 57020-565 ",
    "57020 - 565",
    "57020- 565",
    "57020 -565",
    "57.020-565",
    "57 020 565",
    "57-020-565",
    "57/020/565",
]

INVALID_CEP_VARIATIONS_WITH_EXTRA_DIGIT = [
    "57020-5650",
    "570205650",
    "57020 5650",
    "57020.5650",
    "57020/5650",
    "57020_5650",
    "57020-5650 ",
    " 57020-5650",
    " 57020-5650 ",
    "57020 - 5650",
    "57020- 5650",
    "57020 -5650",
    "57.020-5650",
    "57 020 5650",
    "57-020-5650",
    "57/020/5650",
]

INVALID_CEP_VARIATIONS_WITH_MISSING_DIGIT = [
    "57020-56",
    "5702056",
    "57020 56",
    "57020.56",
    "57020/56",
    "57020_56",
    "57020-56 ",
    " 57020-56",
    " 57020-56 ",
    "57020 - 56",
    "57020- 56",
    "57020 -56",
    "57.020-56",
    "57 020 56",
    "57-020-56",
    "57/020/56",
]

INVALID_LENGTH_CEPS = INVALID_CEP_VARIATIONS_WITH_EXTRA_DIGIT + INVALID_CEP_VARIATIONS_WITH_MISSING_DIGIT


@pytest.mark.parametrize("cep_input", VALID_CEP_VARIATIONS)
def test_should_create_cep_from_valid_variations(cep_input):
    cep = CEP.create(cep_input)

    assert cep.value == "57020565"


@pytest.mark.parametrize("cep_input", INVALID_CEP_VARIATIONS_WITH_EXTRA_DIGIT)
def test_should_raise_when_cep_has_more_than_8_digits(cep_input):
    with pytest.raises(InvalidCEPLengthError):
        CEP.create(cep_input)


@pytest.mark.parametrize("cep_input", INVALID_CEP_VARIATIONS_WITH_MISSING_DIGIT)
def test_should_raise_when_cep_has_less_than_8_digits(cep_input):
    with pytest.raises(InvalidCEPLengthError):
        CEP.create(cep_input)

def test_if_cep_is_formatting_properly():
    cep_value = "57020565"
    cep_object = CEP.create(cep_value)
    assert cep_object.formatted == "57020-565"
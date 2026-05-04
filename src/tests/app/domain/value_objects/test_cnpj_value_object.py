import pytest

from app.domain.value_objects import CNPJ, InvalidCNPJLengthError

VALID_CNPJ_VARIATIONS = [
    "62.173.620/0001-80",
    "62.173.620/000180",
    "62173620000180",
    "62 173 620 0001 80",
    "62-173-620-0001-80",
    "62.173.620.0001.80",
    "62/173/620/0001/80",
    "62_173_620_0001_80",
    " 62.173.620/0001-80 ",
    " 62173620000180 ",
    "62.173.620 / 0001-80",
    "62 . 173 . 620 / 0001 - 80",
    "62.173.620/0001 - 80",
    "62.173.620 /0001-80",
    "62.173.620/ 0001-80",
    "62.173.620/0001- 80",
]

INVALID_CNPJS_WITH_EXTRA_DIGIT = [
    "62.173.620/0001-800",
    "62.173.620/0001800",
    "621736200001800",
    "62 173 620 0001 800",
    "62-173-620-0001-800",
    "62.173.620.0001.800",
    "62/173/620/0001/800",
    "62_173_620_0001_800",
    " 62.173.620/0001-800 ",
    " 621736200001800 ",
    "62.173.620 / 0001-800",
    "62 . 173 . 620 / 0001 - 800",
    "62.173.620/0001 - 800",
    "62.173.620 /0001-800",
    "62.173.620/ 0001-800",
    "62.173.620/0001- 800",
]

INVALID_CNPJS_WITH_MISSING_DIGIT = [
        "62.173.620/0001-8",
        "62.173.620/00018",
        "6217362000018",
        "62 173 620 0001 8",
        "62-173-620-0001-8",
        "62.173.620.0001.8",
        "62/173/620/0001/8",
        "62_173_620_0001_8",
        " 62.173.620/0001-8 ",
        " 6217362000018 ",
        "62.173.620 / 0001-8",
        "62 . 173 . 620 / 0001 - 8",
        "62.173.620/0001 - 8",
        "62.173.620 /0001-8",
        "62.173.620/ 0001-8",
        "62.173.620/0001- 8",
]

INVALID_LENGTH_CNPJS = INVALID_CNPJS_WITH_EXTRA_DIGIT + INVALID_CNPJS_WITH_MISSING_DIGIT

@pytest.mark.parametrize("cnpj", VALID_CNPJ_VARIATIONS)
def test_if_cnpj_is_being_created_with_valid_cnpj(cnpj):
    cnpj_object = CNPJ(cnpj)
    assert cnpj_object.value == "62173620000180"

@pytest.mark.parametrize("cnpj", INVALID_LENGTH_CNPJS)
def test_if_invalid_length_cnpj_is_being_rejected(cnpj):
    with pytest.raises(InvalidCNPJLengthError):
        CNPJ.create(cnpj)

def test_if_cnpj_is_formatting_properly():
    cnpj_value = "62173620000180"
    cnpj_object = CNPJ.create(cnpj_value)
    assert cnpj_object.formatted == "62.173.620/0001-80"



    
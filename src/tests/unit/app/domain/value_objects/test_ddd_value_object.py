import pytest
pytestmark = pytest.mark.unit

from app.domain.value_objects import DDD, InvalidDDDLengthError

VALID_DDD_VALUES = [
    "11", "12", "13", "14", "15", "16", "17", "18", "19",
    "21", "22", "24",
    "27", "28",
    "31", "32", "33", "34", "35", "37", "38",
    "41", "42", "43", "44", "45", "46",
    "47", "48", "49",
    "51", "53", "54", "55",
    "61",
    "62", "64",
    "63",
    "65", "66",
    "67",
    "68",
    "69",
    "71", "73", "74", "75", "77",
    "79",
    "81", "87",
    "82",
    "83",
    "84",
    "85", "88",
    "86", "89",
    "91", "93", "94",
    "92", "97",
    "95",
    "96",
    "98", "99",
    "11   ", " 12    "
]

INVALID_LENGTH_DDDS = [
    "1", "01","111", "1234", "123456", "123456789", "12345678901", "123456789012", "1234567890123", "12345678901234", "123456789012345",
]


@pytest.mark.parametrize("ddd", VALID_DDD_VALUES)
def test_should_create_ddd_from_valid_values(ddd):
    ddd_object = DDD.from_value(ddd)
    assert ddd_object.value == ddd

@pytest.mark.parametrize("ddd", INVALID_LENGTH_DDDS)
def test_should_raise_when_ddd_has_invalid_length(ddd):
    with pytest.raises(InvalidDDDLengthError):
        DDD.from_value(ddd)

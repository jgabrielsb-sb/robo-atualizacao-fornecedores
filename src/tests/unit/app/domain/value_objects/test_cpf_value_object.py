import pytest
pytestmark = pytest.mark.unit

from app.domain.value_objects import CPF, InvalidCPFLengthError

VALID_CPFS = [
    ("529.982.247-25", "52998224725"),
    ("529 982 247 25", "52998224725"),
    ("529-982-247-25", "52998224725"),
    ("529/982/247/25", "52998224725"),
    ("529_982_247_25", "52998224725"),
    ("52998224725",    "52998224725"),
    ("111.444.777-35", "11144477735"),
    ("111 444 777 35", "11144477735"),
    ("111-444-777-35", "11144477735"),
    ("111/444/777/35", "11144477735"),
    ("111_444_777_35", "11144477735"),
    ("11144477735",    "11144477735"),
    ("123.456.789-09", "12345678909"),
    ("123 456 789 09", "12345678909"),
    ("123-456-789-09", "12345678909"),
    ("123/456/789/09", "12345678909"),
    ("123_456_789_09", "12345678909"),
    ("12345678909",    "12345678909"),
    ("286.255.878-87", "28625587887"),
    ("987.654.321-00", "98765432100"),
    ("987 654 321 00", "98765432100"),
    ("987-654-321-00", "98765432100"),
    ("987/654/321/00", "98765432100"),
    ("987_654_321_00", "98765432100"),
    ("98765432100",    "98765432100"),
    ("935.411.347-80", "93541134780"),
    ("93541134780",    "93541134780"),
]

INVALID_CPFS_WITH_EXTRA_DIGIT = [
    "529.982.247-250",
    "111.444.777-350",
    "123.456.789-090",
    "987.654.321-000",
    "935.411.347-800",
    "286.255.878-870",
    "451.055.620-060",
    "738.219.870-270",
    "045.958.271-300",
    "681.943.594-060",
]

INVALID_CPFS_WITH_MISSING_DIGIT = [
    "529.982.247-2",
    "111.444.777-3",
    "123.456.789-0",
    "987.654.321-0",
    "935.411.347-8",
    "286.255.878-8",
    "",
]

INVALID_LENGTH_CPFS = INVALID_CPFS_WITH_EXTRA_DIGIT + INVALID_CPFS_WITH_MISSING_DIGIT


@pytest.mark.parametrize("cpf, expected_value", VALID_CPFS)
def test_if_cpf_is_being_created_with_valid_cpf(cpf: str, expected_value: str):
    cpf_object = CPF.create(cpf)
    assert cpf_object.value == expected_value


@pytest.mark.parametrize("cpf", INVALID_LENGTH_CPFS)
def test_if_invalid_length_cpf_is_being_rejected(cpf: str):
    with pytest.raises(InvalidCPFLengthError):
        CPF.create(cpf)


def test_if_cpf_is_formatting_properly():
    cpf_object = CPF.create("52998224725")
    assert cpf_object.formatted == "529.982.247-25"

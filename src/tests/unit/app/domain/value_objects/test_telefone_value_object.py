import pytest

from app.domain.value_objects import Telefone
from app.domain.value_objects.ddd_value_object import DDD

VALID_TELEFONES_CASES = [
    (
        "11999999999",
        Telefone(ddd=DDD(value="11"), numero="999999999"),
    ),
    (
        "(11) 99999-9999",
        Telefone(ddd=DDD(value="11"), numero="999999999"),
    ),
    (
        "+55 11 99999-9999",
        Telefone(ddd=DDD(value="11"), numero="999999999"),
    ),
    (
        "55 11 99999-9999",
        Telefone(ddd=DDD(value="11"), numero="999999999"),
    ),
    (
        "82999999999",
        Telefone(ddd=DDD(value="82"), numero="999999999"),
    ),
    (
        "(82) 99999-9999",
        Telefone(ddd=DDD(value="82"), numero="999999999"),
    ),
    (
        "31987654321",
        Telefone(ddd=DDD(value="31"), numero="987654321"),
    ),
    (
        "(31) 98765-4321",
        Telefone(ddd=DDD(value="31"), numero="987654321"),
    ),
    (
        "1133333333",
        Telefone(ddd=DDD(value="11"), numero="33333333"),
    ),
    (
        "(11) 3333-3333",
        Telefone(ddd=DDD(value="11"), numero="33333333"),
    ),
    (
        "8233333333",
        Telefone(ddd=DDD(value="82"), numero="33333333"),
    ),
    (
        "(82) 3333-3333",
        Telefone(ddd=DDD(value="82"), numero="33333333"),
    ),
    (
        "+55 31 3333-3333",
        Telefone(ddd=DDD(value="31"), numero="33333333"),
    ),
    (
        "3133333333",
        Telefone(ddd=DDD(value="31"), numero="33333333"),
    ),
    (
        "41999999999",
        Telefone(ddd=DDD(value="41"), numero="999999999"),
    ),
    (
        "(41) 99999-9999",
        Telefone(ddd=DDD(value="41"), numero="999999999"),
    ),
    (
        "21988887777",
        Telefone(ddd=DDD(value="21"), numero="988887777"),
    ),
    (
        "(21) 98888-7777",
        Telefone(ddd=DDD(value="21"), numero="988887777"),
    ),
    (
        "85977776666",
        Telefone(ddd=DDD(value="85"), numero="977776666"),
    ),
    (
        "(85) 97777-6666",
        Telefone(ddd=DDD(value="85"), numero="977776666"),
    ),
    (
        "5132221111",
        Telefone(ddd=DDD(value="51"), numero="32221111"),
    ),
    (
        "(51) 3222-1111",
        Telefone(ddd=DDD(value="51"), numero="32221111"),
    ),
]

@pytest.mark.parametrize("telefone, expected", VALID_TELEFONES_CASES)
def test_should_create_telefone_from_valid_values(telefone, expected):
    telefone_object = Telefone.create(telefone)
    assert telefone_object == expected
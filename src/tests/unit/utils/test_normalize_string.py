import pytest

from app.utils.normalize_str import normalize_str

pytestmark = pytest.mark.unit

municipios = [
    ("Alta Floresta D'Oeste", "ALTA FLORESTA D OESTE"),
    ("Alto Alegre dos Parecis", "ALTO ALEGRE DOS PARECIS"),
    ("Alto Paraíso", "ALTO PARAISO"),
    ("Alvorada D'Oeste", "ALVORADA D OESTE"),
    ("Ariquemes", "ARIQUEMES"),
    ("Buritis", "BURITIS"),
    ("Cabixi", "CABIXI"),
    ("Cacaulândia", "CACAULANDIA"),
    ("Cacoal", "CACOAL"),
    ("Campo Novo de Rondônia", "CAMPO NOVO DE RONDONIA"),
    ("Candeias do Jamari", "CANDEIAS DO JAMARI"),
    ("Castanheiras", "CASTANHEIRAS"),
    ("Cerejeiras", "CEREJEIRAS"),
    ("Chupinguaia", "CHUPINGUAIA"),
    ("Colorado do Oeste", "COLORADO DO OESTE"),
    ("Corumbiara", "CORUMBIARA"),
    ("Costa Marques", "COSTA MARQUES"),
    ("Cujubim", "CUJUBIM"),
    ("Espigão D'Oeste", "ESPIGAO D OESTE"),
    ("Governador Jorge Teixeira", "GOVERNADOR JORGE TEIXEIRA"),
    ("Guajará-Mirim", "GUAJARA MIRIM"),
    ("Itapuã do Oeste", "ITAPUA DO OESTE"),
    ("Jaru", "JARU"),
    ("Ji-Paraná", "JI PARANA"),
    ("Machadinho D'Oeste", "MACHADINHO D OESTE"),
    ("Ministro Andreazza", "MINISTRO ANDREAZZA"),
    ("Mirante da Serra", "MIRANTE DA SERRA"),
    ("Monte Negro", "MONTE NEGRO"),
    ("Nova Brasilândia D'Oeste", "NOVA BRASILANDIA D OESTE"),
    ("Nova Mamoré", "NOVA MAMORE"),
    ("Nova União", "NOVA UNIAO"),
    ("Novo Horizonte do Oeste", "NOVO HORIZONTE DO OESTE"),
    ("Ouro Preto do Oeste", "OURO PRETO DO OESTE"),
    ("Parecis", "PARECIS"),
    ("Pimenta Bueno", "PIMENTA BUENO"),
    ("Pimenteiras do Oeste", "PIMENTEIRAS DO OESTE"),
    ("Porto Velho", "PORTO VELHO"),
    ("Presidente Médici", "PRESIDENTE MEDICI"),
    ("Primavera de Rondônia", "PRIMAVERA DE RONDONIA"),
    ("Rio Crespo", "RIO CRESPO"),
    ("Rolim de Moura", "ROLIM DE MOURA"),
    ("Ji-Paraná", "JI PARANA"),
]


@pytest.mark.parametrize("raw_str, expected_normalized_str", municipios)
def test_normalize_str(raw_str: str, expected_normalized_str: str):
    assert normalize_str(raw_str) == expected_normalized_str


def test_normalize_str_strips_leading_trailing_spaces():
    assert normalize_str("   Alta Floresta D'Oeste   ") == "ALTA FLORESTA D OESTE"


def test_normalize_str_raises_type_error_for_non_string():
    with pytest.raises(TypeError):
        normalize_str(123)  # type: ignore[arg-type]

import re
import unicodedata

def normalize_str(value: str) -> str:
    """
    Normalizes a string by:
    - stripping leading/trailing spaces
    - removing accents
    - replacing apostrophes and hyphens with spaces
    - converting to uppercase
    - collapsing multiple spaces into one

    Example:
        "      Alta floresta D'Oeste" -> "ALTA FLORESTA D OESTE"
        "Maceió" -> "MACEIO"
        "Guajará-Mirim" -> "GUAJARA MIRIM"
    """
    if not isinstance(value, str):
        raise TypeError("value must be a string")

    without_accents = unicodedata.normalize("NFD", value)
    without_accents = "".join(
        char for char in without_accents
        if unicodedata.category(char) != "Mn"
    )

    normalized = without_accents.strip()
    normalized = re.sub(r"['’-]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.upper()

    return normalized
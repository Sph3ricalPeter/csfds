from unidecode import unidecode


def normalize(s: str) -> str:
    return unidecode(s).strip().lower()

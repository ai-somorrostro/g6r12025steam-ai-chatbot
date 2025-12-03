# helpers.py
# Funciones generales de utilidad (limpieza, formateo, truncado, etc.)


def truncar_texto(texto: str, max_tokens: int = 1000) -> str:
    """
    Trunca el texto para que no exceda el límite de tokens permitido.
    (Sustituir por control real de tokens si se usa tokenizer avanzado)
    """
    palabras = texto.split()
    if len(palabras) > max_tokens:
        return " ".join(palabras[:max_tokens]) + "..."
    return texto

# utils/tokenizer.py
# Funciones relacionadas con tokenización y generación de embeddings

import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

# ====================================
# 🔠 Cargar modelo de embeddings
# ====================================

# Leer modelo desde .env o usar fallback oficial
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-mpnet-base-v2")

# Cargar el modelo al iniciar
model = SentenceTransformer(EMBEDDING_MODEL)


def generar_embedding(texto: str):
    """
    Genera un vector embedding para un texto dado.
    Devuelve un vector numérico listo para usar.
    """
    return model.encode([texto])[0]

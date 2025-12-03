import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# ==============================
# Carga del modelo de embeddings
# ==============================

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")

# Cargar modelo al iniciar
model = SentenceTransformer(EMBEDDING_MODEL)


def generar_embedding(texto: str):
    """
    Genera un vector embedding para un texto dado.
    """
    return model.encode([texto])[0]

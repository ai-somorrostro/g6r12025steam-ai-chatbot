import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL")
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX")

# Inicializar cliente de Elasticsearch
es = Elasticsearch(ELASTIC_URL)


def buscar_contexto_en_elasticsearch(pregunta: str, top_k: int = 5) -> str:
    """
    Realiza una búsqueda semántica simple en Elasticsearch
    y devuelve el contexto concatenado (título + descripción).
    """
    query = {
        "size": top_k,
        "query": {
            "match": {
                "detailed_description": pregunta
            }
        }
    }

    response = es.search(index=ELASTIC_INDEX, body=query)

    resultados = response.get("hits", {}).get("hits", [])

    contexto = "\n\n".join([
        f"{r['_source'].get('name', '')}: {r['_source'].get('detailed_description', '')}"
        for r in resultados
    ])

    return contexto

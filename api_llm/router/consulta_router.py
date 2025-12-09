# Codigo para dejar solo lo necesario del modelo 

from fastapi import APIRouter, Query
from api_llm.models.consulta_request import ConsultaRequest
from api_llm.llm_manager import obtener_respuesta_llm
from api_llm.utils.elasticsearch_connector import buscar_contexto_en_elasticsearch, es
from api_llm.utils.tokenizer import generar_embedding

router = APIRouter()

# ==========================================================
#  ENDPOINT PRINCIPAL: CONSULTA CON LLM + EMBEDDINGS
# ==========================================================

@router.post("/consulta")
async def consultar_llm(data: ConsultaRequest):
    """
    🔍 Endpoint principal: realiza una búsqueda semántica en Elasticsearch usando embeddings
    y genera una respuesta final usando un LLM (OpenRouter).
    """
    pregunta = data.pregunta

    # 1. Buscar contexto híbrido (embeddings + match textual)
    contexto, score = buscar_contexto_en_elasticsearch(pregunta)

    # 2. Generar respuesta del modelo LLM
    respuesta = obtener_respuesta_llm(pregunta, contexto, elastic_score=score)

    return {
        "pregunta_realizada": pregunta,
        "score_similitud_elasticsearch": score,
        "modelo_llm_respuesta": {
            "formato_texto_completo": respuesta
        }
    }


# ==========================================================
#  ENDPOINT 1: /juegos/gratis
# ==========================================================

@router.get("/juegos/gratis")
async def juegos_gratis():
    """
    🎁 Devuelve todos los juegos cuyo precio sea GRATIS (is_free = true o price_final = 0).
    Esta búsqueda NO usa LLM, consulta directamente Elasticsearch.
    """
    query = {
        "size": 50,
        "_source": ["name", "price_final", "genres", "short_description"],
        "query": {
            "bool": {
                "should": [
                    {"term": {"is_free": True}},
                    {"term": {"price_final": 0}}
                ]
            }
        }
    }

    resultados = es.search(index="steam_games-*", body=query)
    juegos = [
        {
            "titulo": doc["_source"].get("name"),
            "generos": doc["_source"].get("genres"),
            "descripcion": doc["_source"].get("short_description")
        }
        for doc in resultados["hits"]["hits"]
    ]

    return {"total": len(juegos), "juegos_gratis": juegos}


# ==========================================================
#  ENDPOINT 2: /juegos/parecidos-a
# ==========================================================

@router.post("/juegos/parecidos-a")
async def juegos_parecidos_a(titulo: str = Query(..., description="Nombre del juego base para buscar similares")):
    """
    🔎 Busca juegos similares semánticamente a un título dado, usando embeddings.
    """
    embedding = generar_embedding(titulo)

    query = {
        "size": 10,
        "_source": ["name", "genres", "price_final", "short_description"],
        "knn": {
            "field": "vector_embedding",
            "query_vector": embedding,
            "k": 10,
            "num_candidates": 50
        }
    }

    resultados = es.search(index="steam_games-*", body=query)

    juegos = [
        {
            "titulo": d["_source"]["name"],
            "generos": d["_source"].get("genres"),
            "precio": d["_source"].get("price_final"),
            "descripcion": d["_source"].get("short_description")
        }
        for d in resultados["hits"]["hits"]
    ]

    return {"titulo_consulta": titulo, "juegos_similares": juegos}


# ==========================================================
#  ENDPOINT 3: /juegos/por-fecha
# ==========================================================

@router.get("/juegos/por-fecha")
async def juegos_por_fecha(
    fecha: str = Query(..., description="Fecha exacta YYYY-MM-DD o año YYYY")
):
    """
    📅 Devuelve juegos publicados en una fecha concreta (YYYY-MM-DD) o año (YYYY).
    """
    if len(fecha) == 4:
        # Filtrar por AÑO completo
        query = {
            "size": 50,
            "_source": ["name", "release_date", "genres", "price_final"],
            "query": {
                "range": {
                    "release_date": {
                        "gte": f"{fecha}-01-01",
                        "lte": f"{fecha}-12-31"
                    }
                }
            }
        }
    else:
        # Filtrar por fecha exacta
        query = {
            "size": 50,
            "_source": ["name", "release_date", "genres", "price_final"],
            "query": {
                "term": {"release_date": fecha}
            }
        }

    resultados = es.search(index="steam_games-*", body=query)

    juegos = [
        {
            "titulo": d["_source"]["name"],
            "fecha": d["_source"]["release_date"],
            "generos": d["_source"]["genres"],
            "precio": d["_source"]["price_final"]
        }
        for d in resultados["hits"]["hits"]
    ]

    return {"fecha_consultada": fecha, "total": len(juegos), "juegos": juegos}


# ==========================================================
#  ENDPOINT 4: /juegos/por-genero
# ==========================================================

@router.get("/juegos/por-genero")
async def juegos_por_genero(
    genero: str = Query(..., description="Género de juegos a buscar (Acción, Disparos, RPG, Aventura...)")
):
    """
    🎮 Devuelve juegos que contienen el género solicitado. 
    Búsqueda textual + relevancia.
    """
    query = {
        "size": 50,
        "_source": ["name", "genres", "price_final", "short_description"],
        "query": {
            "match": {
                "genres": {
                    "query": genero,
                    "fuzziness": "AUTO"
                }
            }
        }
    }

    resultados = es.search(index="steam_games-*", body=query)

    juegos = [
        {
            "titulo": d["_source"]["name"],
            "generos": d["_source"]["genres"],
            "precio": d["_source"]["price_final"],
            "descripcion": d["_source"]["short_description"]
        }
        for d in resultados["hits"]["hits"]
    ]

    return {"genero_consultado": genero, "total": len(juegos), "juegos": juegos}

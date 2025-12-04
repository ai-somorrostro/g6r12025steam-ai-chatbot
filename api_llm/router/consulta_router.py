from fastapi import APIRouter
from api_llm.models.consulta_request import ConsultaRequest
from api_llm.llm_manager import obtener_respuesta_llm
from api_llm.utils.elasticsearch_connector import buscar_contexto_en_elasticsearch

router = APIRouter()

@router.post("/consulta")
async def consultar_llm(data: ConsultaRequest):
    """
    Endpoint principal: búsqueda semántica con embeddings y respuesta LLM.
    """
    pregunta = data.pregunta

    # 1. Buscar contexto por similitud semántica en Elasticsearch
    # CORRECCIÓN: Ahora recibimos dos valores (Texto y Score)
    contexto, score = buscar_contexto_en_elasticsearch(pregunta)

    # 2. Generar respuesta con modelo LLM
    # CORRECCIÓN: Pasamos el texto como contexto y el score por separado
    respuesta = obtener_respuesta_llm(pregunta, contexto, elastic_score=score)

    return {
        "pregunta": pregunta,
        "score_relevancia": score, # Agregamos esto para que lo veas en la respuesta JSON
        "contexto_usado": contexto,
        "respuesta": respuesta
    }
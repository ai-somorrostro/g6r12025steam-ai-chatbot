from fastapi import APIRouter
from api_llm.models.consulta_request import ConsultaRequest
from api_llm.llm_manager import obtener_respuesta_llm
from api_llm.utils.elasticsearch_connector import buscar_contexto_en_elasticsearch

router = APIRouter()

# ==================================
# Ruta principal para consultas LLM
# ==================================

@router.post("/consulta")
async def consultar_llm(data: ConsultaRequest):
    pregunta = data.pregunta

    # 1. Buscar contexto en Elasticsearch
    contexto = buscar_contexto_en_elasticsearch(pregunta)

    # 2. Enviar pregunta + contexto al LLM
    respuesta = obtener_respuesta_llm(pregunta, contexto)

    # 3. Devolver respuesta
    return {"pregunta": pregunta, "respuesta": respuesta}

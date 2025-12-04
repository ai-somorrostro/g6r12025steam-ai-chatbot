# import os
# from elasticsearch import Elasticsearch
# from dotenv import load_dotenv
# from api_llm.utils.tokenizer import generar_embedding

# load_dotenv()

# ELASTIC_URL = os.getenv("ELASTIC_URL")
# ELASTIC_INDEX_PREFIX = os.getenv("ELASTIC_INDEX_PREFIX")
# ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
# ELASTIC_CA_CERT_PATH = os.getenv("ELASTIC_CA_CERT_PATH")

# # Inicializa el cliente con API Key y certificados
# es = Elasticsearch(
#     ELASTIC_URL,
#     api_key=ELASTIC_API_KEY,
#     ca_certs=ELASTIC_CA_CERT_PATH,
#     verify_certs=True
# )


# def buscar_contexto_en_elasticsearch(pregunta: str, top_k: int = 5) -> str:
#     """
#     Realiza búsqueda semántica REAL usando kNN y embeddings.
#     """
#     embedding = generar_embedding(pregunta)

#     query = {
#         "size": top_k,
#         "query": {
#             "knn": {
#                 "vector_embedding": {
#                     "vector": embedding,
#                     "k": top_k
#                 }
#             }
#         }
#     }

#     # Usa índice dinámico más reciente
#     from datetime import datetime
#     indice_hoy = f"{ELASTIC_INDEX_PREFIX}{datetime.today().strftime('%Y.%m.%d')}"

#     try:
#         response = es.search(index=indice_hoy, body=query)

#         hits = response.get("hits", {}).get("hits", [])

#         contexto = "\n\n".join([
#             f"Título: {doc['_source'].get('name', '')}\nDescripción: {doc['_source'].get('detailed_description', '')}"
#             for doc in hits
#         ])

#         return contexto if contexto else "No se encontró contexto relevante."

#     except Exception as e:
#         return f"[Error Elasticsearch] {str(e)}"   

#  Archivo API-Reto-1/api_llm/utils/elasticsearch_connector.py, para flujo normal con API-KEY y embbedings.Arriba


# ** Este siguiente archivo hace  búsquedas desde la API aunque el nodo con API Key esté caído y Cliente de Elasticsearch con autenticación básica


# import os
# from elasticsearch import Elasticsearch
# from dotenv import load_dotenv
# import warnings
# from urllib3.exceptions import InsecureRequestWarning

# warnings.simplefilter("ignore", InsecureRequestWarning)

# load_dotenv()

# # ================================
# # Configuración conexión temporal
# # ================================

# ELASTIC_URLS = os.getenv("ELASTIC_URLS", "").split(",")
# ELASTIC_USER = os.getenv("ELASTIC_USER")
# ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
# ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "steam_games-*")

# # Crear cliente temporal sin verificación de certificado (solo para pruebas)
# es = Elasticsearch(
#     hosts=ELASTIC_URLS,
#     basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
#     verify_certs=False,
#     ssl_show_warn=False,
#     request_timeout=30,
#     max_retries=5,
#     retry_on_timeout=True,
# )

# def buscar_contexto_en_elasticsearch(pregunta: str, top_k: int = 5) -> str:
#     """
#     Realiza búsqueda por texto plano (match simple) en Elasticsearch.
#     Retorna contexto textual basado en el campo "name" o "detailed_description".
#     """

#     query = {
#         "size": top_k,
#         "query": {
#             "match": {
#                 "name": {
#                     "query": pregunta,
#                     "fuzziness": "AUTO"
#                 }
#             }
#         },
#         "_source": ["name", "detailed_description"]
#     }

#     try:
#         response = es.search(index=ELASTIC_INDEX, body=query)
#         hits = response.get("hits", {}).get("hits", [])

#         if not hits:
#             return "[INFO] No se encontró contexto para la pregunta."

#         contexto = "\n\n".join([
#             f"🎮 Título: {doc['_source'].get('name', '')}\n📝 Descripción: {doc['_source'].get('detailed_description', '')}"
#             for doc in hits
#         ])

#         return contexto

#     except Exception as e:
#         return f"[ERROR al consultar Elasticsearch]: {str(e)}"

# # =============================================
# # Código anterior con embeddings (comentado)
# # =============================================

# # from api_llm.utils.tokenizer import generar_embedding
# # ELASTIC_URL = os.getenv("ELASTIC_URL")
# # ELASTIC_INDEX = os.getenv("ELASTIC_INDEX")
# # ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
# # ELASTIC_CA_CERT_PATH = os.getenv("ELASTIC_CA_CERT_PATH")

# # es = Elasticsearch(
# #     ELASTIC_URL,
# #     api_key=ELASTIC_API_KEY,
# #     ca_certs=ELASTIC_CA_CERT_PATH
# # )

# # def buscar_contexto_en_elasticsearch(pregunta: str, top_k: int = 5) -> str:
# #     embedding = generar_embedding(pregunta)
# #     query = {
# #         "size": top_k,
# #         "query": {
# #             "knn": {
# #                 "vector_embedding": {
# #                     "vector": embedding,
# #                     "k": top_k
# #                 }
# #             }
# #         }
# #     }
# #     ...




import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter("ignore", InsecureRequestWarning)

load_dotenv()

# ================================
# Configuración conexión temporal
# ================================

ELASTIC_URLS = os.getenv("ELASTIC_URLS", "").split(",")
ELASTIC_USER = os.getenv("ELASTIC_USER")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "steam_games-*")

# Crear cliente temporal sin verificación de certificado (solo para pruebas)
es = Elasticsearch(
    hosts=ELASTIC_URLS,
    basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
    verify_certs=False,
    ssl_show_warn=False,
    request_timeout=30,
    max_retries=5,
    retry_on_timeout=True,
)

def buscar_contexto_en_elasticsearch(pregunta: str, top_k: int = 5) -> str:
    """
    Realiza búsqueda por texto plano (match simple) en Elasticsearch.
    Retorna contexto textual basado en el campo "name" o "detailed_description".
    """

    query = {
        "size": top_k,
        "query": {
            "match": {
                "name": {
                    "query": pregunta,
                    "fuzziness": "AUTO"
                }
            }
        },
        "_source": ["name", "detailed_description"]
    }

    try:
        response = es.search(index=ELASTIC_INDEX, body=query)
        hits = response.get("hits", {}).get("hits", [])

        if not hits:
            return "[INFO] No se encontró contexto para la pregunta."

        contexto = "\n\n".join([
            f"🎮 Título: {doc['_source'].get('name', '')}\n📝 Descripción: {doc['_source'].get('detailed_description', '')}"
            for doc in hits
        ])

        return contexto

    except Exception as e:
        return f"[ERROR al consultar Elasticsearch]: {str(e)}"

# =============================================
# Código anterior con embeddings (comentado)
# =============================================

# from api_llm.utils.tokenizer import generar_embedding
# ELASTIC_URL = os.getenv("ELASTIC_URL")
# ELASTIC_INDEX = os.getenv("ELASTIC_INDEX")
# ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
# ELASTIC_CA_CERT_PATH = os.getenv("ELASTIC_CA_CERT_PATH")

# es = Elasticsearch(
#     ELASTIC_URL,
#     api_key=ELASTIC_API_KEY,
#     ca_certs=ELASTIC_CA_CERT_PATH
# )

# def buscar_contexto_en_elasticsearch(pregunta: str, top_k: int = 5) -> str:
#     embedding = generar_embedding(pregunta)
#     query = {
#         "size": top_k,
#         "query": {
#             "knn": {
#                 "vector_embedding": {
#                     "vector": embedding,
#                     "k": top_k
#                 }
#             }
#         }
#     }
#     ...

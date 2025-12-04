import os
import logging
import re  # <--- IMPORTANTE: Necesario para detectar números
from typing import Tuple
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from api_llm.utils.tokenizer import generar_embedding

load_dotenv()
logger = logging.getLogger(__name__)

# ================================
# Configuración conexión segura con API KEY
# ================================

ELASTIC_URLS = os.getenv("ELASTIC_URLS", "").split(",")
ELASTIC_INDEX_PREFIX = os.getenv("ELASTIC_INDEX_PREFIX", "steam_games-*")

# Obtener la API Key del .env
ENV_API_KEY = os.getenv("ELASTIC_API_KEY")
api_key_tuple = None

if ENV_API_KEY and ":" in ENV_API_KEY:
    api_key_tuple = tuple(ENV_API_KEY.split(":"))
else:
    print("⚠️ ADVERTENCIA: No se encontró ELASTIC_API_KEY válida en el .env")

es = Elasticsearch(
    hosts=ELASTIC_URLS,
    api_key=api_key_tuple,
    verify_certs=False, 
    ssl_show_warn=False,
    request_timeout=30,
    max_retries=5,
    retry_on_timeout=True,
)

# ================================
# Función para seleccionar el índice más nuevo
# ================================
def obtener_ultimo_indice(prefix_pattern: str) -> str:
    """
    Obtiene la lista de índices que coinciden con el patrón (ej: steam_games-*)
    y devuelve el último alfabéticamente (que corresponde a la fecha más reciente).
    """
    try:
        indices = list(es.indices.get(index=prefix_pattern).keys())
        
        if not indices:
            return prefix_pattern

        indices_ordenados = sorted(indices)
        ultimo_indice = indices_ordenados[-1]
        
        return ultimo_indice

    except Exception as e:
        logger.error(f"Error buscando último índice: {e}")
        return prefix_pattern

# ================================
# Función principal de búsqueda
# ================================
def buscar_contexto_en_elasticsearch(pregunta: str, top_k: int = 10) -> Tuple[str, float]:
    """
    Realiza búsqueda HÍBRIDA en el índice MÁS RECIENTE.
    Si detecta un precio, filtra numéricamente. Si no, usa búsqueda híbrida estándar.
    Devuelve: (Contexto formateado, Score de relevancia máximo)
    """
    try:
        embedding = generar_embedding(pregunta)
        
        # Cálculo dinámico de candidatos
        candidates = max(50, top_k + 50)
        
        # Campos que queremos recuperar
        source_fields = [
            "name", "short_description", "detailed_description", 
            "genres", "price_category", "is_free", 
            "developers", "price_final", "metacritic_score"
        ]

        # 1. DETECCIÓN DE PRECIO (Regex)
        # Busca números como: 9.75, 9,75, 10, 4.5
        match_precio = re.search(r'(\d+[.,]\d{1,2}|\d+)', pregunta)
        
        query = {}

        # === ESTRATEGIA A: FILTRO DE PRECIO EXACTO ===
        # Se activa solo si encontramos un número en la pregunta y la palabra "precio", "cuesta" o "vale" (opcional, pero recomendado para no confundir con "Dead Rising 4")
        if match_precio and any(x in pregunta.lower() for x in ['precio', 'cuesta', 'vale', 'euros', 'eur', '$']):
            try:
                # Normalizar precio (cambiar coma por punto)
                precio_str = match_precio.group(1).replace(',', '.')
                precio_target = float(precio_str)
                logger.info(f"Filtro numérico activado: Buscando precio cercano a {precio_target}")

                query = {
                    "size": top_k,
                    "_source": source_fields,
                    "query": {
                        "bool": {
                            "must": [
                                # Usamos range para tolerar pequeñas diferencias de decimales
                                {
                                    "range": {
                                        "price_final": {
                                            "gte": precio_target - 0.05, 
                                            "lte": precio_target + 0.05
                                        }
                                    }
                                }
                            ],
                            # Añadimos el kNN como 'should' para ordenar los resultados que coinciden en precio
                            # por similitud semántica con el resto de la frase
                            "should": [
                                {
                                    "knn": {
                                        "field": "vector_embedding",
                                        "query_vector": embedding,
                                        "k": top_k,
                                        "num_candidates": candidates
                                    }
                                }
                            ]
                        }
                    }
                }
            except ValueError:
                # Si falla la conversión a float, seguimos con la estrategia normal
                pass

        # === ESTRATEGIA B: BÚSQUEDA HÍBRIDA ESTÁNDAR (Si no es búsqueda de precio) ===
        if not query:
            query = {
                "size": top_k, 
                "_source": source_fields,
                
                # Búsqueda Vectorial (Conceptos)
                "knn": {
                    "field": "vector_embedding", 
                    "query_vector": embedding,
                    "k": top_k,
                    "num_candidates": candidates,
                    "boost": 0.5 
                },

                # Búsqueda Texto Exacto (Palabras clave)
                "query": {
                    "bool": {
                        "should": [
                            {
                                "multi_match": {
                                    "query": pregunta,
                                    "fields": [
                                        "name^3",
                                        "price_category^5",
                                        "genres^2",
                                        "categories",
                                        "short_description",
                                        "detailed_description"
                                    ],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ]
                    }
                }
            }

        # Seleccionamos el índice más reciente
        indice_objetivo = obtener_ultimo_indice(ELASTIC_INDEX_PREFIX)
        
        # Ejecutamos la búsqueda
        response = es.search(index=indice_objetivo, body=query)
        hits = response.get("hits", {}).get("hits", [])

        if not hits:
            return "[INFO] No se encontró contexto relevante.", 0.0

        # === CAPTURAR MAX SCORE ===
        max_score = hits[0].get("_score", 0.0)

        contexto_list = []

        for doc in hits:
            source = doc['_source']
            nombre = source.get('name', 'Desconocido')
            
            # Formateo del precio para el texto
            if source.get('is_free') or source.get('price_category') == "Gratis":
                precio_texto = "GRATIS"
            else:
                precio_val = source.get('price_final', 'N/A')
                precio_texto = f"{precio_val} EUR"
            
            info = (
                f"🎮 Título: {nombre}\n"
                f"💰 Precio: {precio_texto}\n"
                f"🏷️ Géneros: {', '.join(source.get('genres', []))}\n"
                f"📝 Descripción: {source.get('short_description', '')[:300]}..."
            )
            contexto_list.append(info)

        texto_final = "\n\n---\n\n".join(contexto_list)
        
        return texto_final, max_score

    except Exception as e:
        print(f"[ERROR DETALLADO]: {e}")
        return f"[ERROR Elasticsearch]: {str(e)}", 0.0
import pandas as pd
from elasticsearch import Elasticsearch
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)

IP_ELASTIC = [
    "https://192.199.1.53:9200",  # Nodo caído, se ignorará automáticamente
    "https://192.199.1.65:9200",
    "https://192.199.1.66:9200"
]

es = Elasticsearch(
    hosts=IP_ELASTIC,
    basic_auth=("elastic", "9VrlcU4nXNYb9EJZ8uAs"),
    verify_certs=False,
    ssl_show_warn=False,
    max_retries=5,         # reintentos automáticos
    retry_on_timeout=True, # reintenta en timeout
    request_timeout=30     # timeout de cada request
)

# Función de búsqueda
def buscar_juego(texto_usuario, campo="name", fuzziness="AUTO"):
    print(f"\n🎮 Buscando: '{texto_usuario}' en campo '{campo}' (Fuzziness: {fuzziness})...")

    query_body = {
        "size": 5,
        "query": {
            "match": {
                campo: {
                    "query": texto_usuario,
                    "fuzziness": fuzziness
                }
            }
        },
        "_source": ["name", "price_final", "price_category", "genres", "release_date"]
    }

    try:
        response = es.search(index="steam_games-*", body=query_body)
        hits = response['hits']['hits']
        if not hits:
            print("⚠️ No se encontraron juegos.")
            return

        datos = []
        for hit in hits:
            juego = hit['_source']
            juego['score'] = hit['_score']
            datos.append(juego)

        df = pd.DataFrame(datos)
        cols = ['name', 'score', 'price_final', 'price_category']
        cols_existentes = [c for c in cols if c in df.columns]
        print(df[cols_existentes])

    except Exception as e:
        print(f"❌ Error: {e}")

# --- Pruebas ---
try:
    count = es.count(index="steam_games-*")
    print(f"Documentos totales en 'steam_games-*': {count['count']}")
except Exception as e:
    print(f"No se pudo conectar o encontrar el índice: {e}")

buscar_juego("Batlefield")
buscar_juego("Red Ded")
buscar_juego("zombis", campo="short_description")
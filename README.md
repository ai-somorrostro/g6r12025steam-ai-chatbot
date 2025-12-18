# Documentación Completa: API RAG Híbrida para Steam Games

## Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Cómo Funciona](#cómo-funciona)
4. [Componentes Principales](#componentes-principales)
5. [Endpoints Disponibles](#endpoints-disponibles)
6. [Flujo de Datos](#flujo-de-datos)
7. [Configuración](#configuración)
8. [Despliegue](#despliegue)

---

## Descripción General

**API RAG Híbrida Steam Games** es una API REST construida con `FastAPI` que permite hacer consultas sobre videojuegos de Steam de dos maneras:

1. **Búsquedas semánticas (RAG)**: usando embeddings vectoriales y LLM para preguntas complejas
2. **Búsquedas SQL-like directas**: filtros por género, fecha, etc.

La API combina:
- **Elasticsearch**: motor de búsqueda vectorial + texto
- **Sentence-Transformers**: generación de embeddings semánticos (768 dimensiones)
- **OpenRouter LLM**: generación de respuestas contextuales
- **FastAPI**: servidor HTTP de alta performance

**Casos de uso:**
- "Recomiéndame juegos de supervivencia cooperativos" → RAG (busca semántica + LLM)
- "Dame juegos gratis" → SQL-like (filtro directo)
- "Juegos similares a Minecraft" → kNN vectorial
- "Juegos de 2024" → rango temporal

---

## Estructura del Proyecto

```
API-Reto-1/
├── api_llm/
│   ├── __init__.py
│   ├── main.py                          # Entrypoint FastAPI
│   ├── llm_manager.py                   # Gestor de LLM (OpenRouter)
│   ├── models/
│   │   └── consulta_request.py          # Modelos Pydantic de entrada
│   ├── router/
│   │   └── consulta_router.py           # Definición de endpoints
│   └── utils/
│       ├── elasticsearch_connector.py   # Conexión y queries a ES
│       ├── tokenizer.py                 # Generación de embeddings
│       └── helpers.py                   # Funciones auxiliares
│
├── scripts-ingesta-datos/
│   └── json-a-elasticsearch.py          # Script para cargar datos en ES
│
├── tests/
│   ├── test_endpoints.py                # Tests de endpoints
│   └── test_llm_response.py             # Tests de respuestas LLM
│
├── logs/
│   └── tokens_usage.json                # Métricas de uso
│
├── Dockerfile                           # Configuración Docker
├── docker-compose.yml                   # Orquestación de servicios
├── requirements.txt                     # Dependencias Python
├── .env.example                         # Variables de entorno
└── README.md                            # Este documento
```

---

## Cómo Funciona

### Flujo General

```
┌─────────────────┐
│  Usuario        │
│  (Cliente HTTP) │
└────────┬────────┘
         │ POST /consulta {"pregunta": "..."}
         ▼
┌─────────────────────────────────────┐
│  FastAPI Main (api_llm/main.py)     │
│  - CORS habilitado                  │
│  - Incluye router de consultas      │
└────────┬────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Router (consulta_router.py)             │
│  - Determina tipo de consulta            │
│  - Rutea a función correspondiente       │
└────────┬─────────────────────────────────┘
         │
    ┌────┴──────────────────────────────────────┐
    │                                           │
    ▼                                           ▼
┌─────────────────────┐            ┌──────────────────────┐
│ RAG Search          │            │ Direct Query         │
│ (/consulta)         │            │ (/juegos/gratis,     │
│ 1. Embed query      │            │  /juegos/por-genero, │
│ 2. kNN search ES    │            │  etc.)               │
│ 3. LLM response     │            │ 1. Build ES query    │
└────────┬────────────┘            │ 2. Execute           │
         │                         │ 3. Return results    │
         └──────────┬──────────────┘└────────┬────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Elasticsearch       │
         │ (steam_games index)  │
         │ - Vectores (768d)    │
         │ - Metadata (txt)     │
         │ - Filtros (num)      │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ Construcción respuesta│
         │ + Format JSON        │
         └──────────┬───────────┘
                    │
                    ▼
              Cliente HTTP ◄────
```

---

## Componentes Principales

### 1. **main.py** - Inicialización FastAPI

```python
# Define la aplicación FastAPI
# Configura CORS para acceso desde cualquier origen
# Incluye el router de endpoints
```

**Responsabilidades:**
- Crear instancia de `FastAPI()`
- Agregar middleware CORS
- Registrar routers

---

### 2. **consulta_router.py** - Definición de Endpoints

Define 5 endpoints principales:

#### **A. POST /consulta** (RAG Completo)
- **Entrada**: `{"pregunta": "..."}` (texto libre)
- **Proceso**:
  1. Genera embedding de la pregunta
  2. Busca contexto en Elasticsearch (kNN + match textual)
  3. Envía contexto + pregunta al LLM
  4. Retorna respuesta generada
- **Salida**: Respuesta estructurada con score y modelo

#### **B. GET /juegos/gratis** (SQL-like)
- **Busca**: Juegos con `price_final = 0` o `is_free = true`
- **Retorna**: Lista de juegos gratis con metadata

#### **C. POST /juegos/parecidos-a** (Búsqueda Semántica)
- **Entrada**: Nombre de un juego
- **Proceso**: Busca similares usando kNN vectorial
- **Retorna**: Top 10 juegos similares

#### **D. GET /juegos/por-fecha** (Rango Temporal)
- **Entrada**: `fecha` (YYYY-MM-DD o YYYY)
- **Retorna**: Juegos de esa fecha/año

#### **E. GET /juegos/por-genero** (Búsqueda Textual)
- **Entrada**: Nombre del género (Acción, RPG, etc.)
- **Retorna**: Juegos del género especificado (con fuzzy matching)

---

### 3. **llm_manager.py** - Gestor de LLM

Encargado de comunicarse con OpenRouter.

**Funciones principales:**
- `obtener_respuesta_llm(pregunta, contexto, elastic_score)`:
  - Construye prompt con contexto
  - Realiza HTTP POST a OpenRouter API
  - Loguea tokens consumidos
  - Registra métricas en `logs/tokens_usage.json`

**Configuración:**
- Modelo: `google/gemini-2.0-flash-lite-001` (configurable)
- API Key: desde `.env` (`OPENROUTER_API_KEY`)
- Rate limiting: integrado

---

### 4. **elasticsearch_connector.py** - Conexión a ES

Gestiona todas las operaciones con Elasticsearch.

**Funciones principales:**
- `buscar_contexto_en_elasticsearch(pregunta)`:
  - Genera embedding de la pregunta
  - Ejecuta query híbrida (kNN + BM25)
  - Retorna: documentos + score similitud

**Configuración:**
- URLs: desde `.env` (`ELASTIC_URLS`)
- API Key: desde `.env` (`ELASTIC_API_KEY`)
- Índice: `steam_games-*`

---

### 5. **tokenizer.py** - Embeddings

Generación de vectores semánticos.

**Función principal:**
- `generar_embedding(texto)`:
  - Usa modelo `sentence-transformers`
  - Retorna vector de 768 dimensiones
  - Cacheado para optimizar

**Modelo**: `all-MiniLM-L6-v2` (configurable, ~40MB)

---

### 6. **helpers.py** - Utilidades

Funciones auxiliares:
- Truncamiento de textos
- Sanitización de inputs
- Formateo de respuestas

---

### 7. **consulta_request.py** - Modelos Pydantic

Define estructura de datos esperada:

```python
class ConsultaRequest(BaseModel):
    pregunta: str = Field(..., description="Pregunta del usuario")
```

Validación automática de tipos + documentación Swagger.

---

## Endpoints Disponibles

### Tabla Resumen

| Método | Endpoint | Tipo | Descripción |
|--------|----------|------|-------------|
| POST | `/consulta` | RAG | Búsqueda semántica + LLM |
| GET | `/juegos/gratis` | SQL-like | Juegos gratis |
| POST | `/juegos/parecidos-a` | kNN | Similares a un título |
| GET | `/juegos/por-fecha` | Rango | Por fecha de lanzamiento |
| GET | `/juegos/por-genero` | Texto | Por género (fuzzy match) |

### Ejemplos de Uso

#### 1. Búsqueda RAG (Semántica + LLM)
```bash
curl -X POST http://localhost:8000/consulta \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "Recomiéndame juegos de ciencia ficción cooperativos baratos"}'
```

**Respuesta:**
```json
{
  "pregunta_realizada": "Recomiéndame juegos de ciencia ficción cooperativos baratos",
  "score_similitud_elasticsearch": 0.92,
  "modelo_llm_respuesta": {
    "formato_texto_completo": "Te recomiendo... [respuesta generada por LLM]"
  }
}
```

#### 2. Juegos Gratis
```bash
curl http://localhost:8000/juegos/gratis
```

**Respuesta:**
```json
{
  "total": 15,
  "juegos_gratis": [
    {
      "titulo": "Team Fortress 2",
      "generos": ["Acción", "Disparos"],
      "descripcion": "..."
    }
  ]
}
```

#### 3. Juegos Parecidos
```bash
curl -X POST "http://localhost:8000/juegos/parecidos-a?titulo=Minecraft"
```

#### 4. Juegos por Año
```bash
curl "http://localhost:8000/juegos/por-fecha?fecha=2023"
```

#### 5. Juegos por Género
```bash
curl "http://localhost:8000/juegos/por-genero?genero=RPG"
```

---

## Flujo de Datos

### Paso 1: Ingesta de Datos

```
NDJSON vectorizado           Elasticsearch
(steam-games-data-vect.json) ◄────────────────► Index: steam_games-YYYY.MM.DD
┌──────────────────────┐     json-a-es.py     └────────────────────────┘
│ {"id": 730,          │                       Documentos:
│  "name": "CS2",      │                       ├── name (texto)
│  "vector": [0.1...], │                       ├── genres (array)
│  "price": 0,         │                       ├── price_final (número)
│  ...}                │                       ├── vector_embedding (768d)
│ ...                  │                       └── ...
└──────────────────────┘
```

### Paso 2: Consulta RAG

```
Usuario pregunta:
"Juegos de survival cooperativos"
        │
        ▼
┌─────────────────────────────────────┐
│ Tokenizer.generar_embedding()       │
│ sentence-transformers               │
│ Entrada: "Juegos de survival..."    │
│ Salida: [0.123, 0.456, ...]  (768)  │
└─────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────┐
│ ES Query (Híbrido):                                  │
│ 1. KNN: {"field": "vector_embedding",                │
│          "query_vector": [0.123, ...],               │
│          "k": 5}                                     │
│ 2. BM25: {"match": {"description": "survival"}}      │
│ Resultado: Top 5 documentos similares                │
└──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────┐
│ Construcción de Prompt:                              │
│ "Basado en estos juegos: [contexto]                  │
│  Responde: [pregunta]"                               │
└──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────┐
│ OpenRouter LLM API:                                  │
│ POST https://openrouter.ai/api/v1/chat/completions   │
│ Payload: {model, messages, max_tokens...}            │
│ Respuesta: "Te recomiendo... [texto generado]"       │
└──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────┐
│ JSON Response al Cliente:                            │
│ {                                                    │
│   "pregunta_realizada": "...",                       │
│   "score_similitud_elasticsearch": 0.92,             │
│   "modelo_llm_respuesta": {                          │
│     "formato_texto_completo": "Te recomiendo..."     │
│   }                                                  │
│ }                                                    │
└──────────────────────────────────────────────────────┘
```

---

## Configuración

### Variables de Entorno (.env)

```bash
# OpenRouter LLM
OPENROUTER_API_KEY=sk-...
OPENROUTER_MODEL=google/gemini-2.0-flash-lite-001

# Elasticsearch
ELASTIC_URLS=http://localhost:9200
ELASTIC_API_KEY=id:password    # O vacío si auth no requerida
ELASTIC_INDEX_PREFIX=steam_games-*

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Ruta de datos (si aplica)
DATASET_PATH=/app/data/steam-games-data-vect.ndjson
```

### Descripción de Variables

| Variable | Descripción | Obligatoria | Ejemplo |
|----------|-------------|-------------|---------|
| `OPENROUTER_API_KEY` | API Key de OpenRouter | Sí | `sk-or-...` |
| `OPENROUTER_MODEL` | Modelo LLM a usar | No | `google/gemini-2.0-flash-lite-001` |
| `ELASTIC_URLS` | URLs de Elasticsearch | Sí | `http://localhost:9200` |
| `ELASTIC_API_KEY` | Credenciales ES | No | `id:password` |
| `ELASTIC_INDEX_PREFIX` | Patrón de índices | No | `steam_games-*` |
| `EMBEDDING_MODEL` | Modelo sentence-transformers | No | `all-MiniLM-L6-v2` |

---

## Despliegue

### 1. Desarrollo Local

```bash
# 1. Clonar y preparar entorno
cd /home/g6/API-Reto-1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configurar .env
cp .env.example .env
# ← Editar .env con tus credenciales

# 3. Iniciar Elasticsearch (si no está corriendo)
docker run -d --name elasticsearch -p 9200:9200 \
  -e "discovery.type=single-node" \
  docker.elastic.co/elasticsearch/elasticsearch:9.2.1

# 4. Cargar datos (si es la primera vez)
python scripts-ingesta-datos/json-a-elasticsearch.py

# 5. Ejecutar API
uvicorn api_llm.main:app --reload --host 0.0.0.0 --port 8000
```

**API disponible en**: `http://localhost:8000`
**Documentación interactiva**: `http://localhost:8000/docs` (Swagger)

---

### 2. Docker Compose (Recomendado)

```bash
# Construir y levantar
docker-compose up --build -d

# Ver logs
docker-compose logs -f api-llm

# Detener
docker-compose down
```

**Notas:**
- El servicio en docker-compose solo levanta la API
- Elasticsearch debe estar corriendo por separado o agregarse al compose
- Volumen `.:/app` permite desarrollo hot-reload

---

### 3. Producción

Para desplegar en producción:

1. **Remover volumen de código** en docker-compose.yml
2. **Agregar healthcheck**:
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```
3. **Usar usuario no-root** en Dockerfile
4. **Usar base de datos** para logs (en lugar de archivos)
5. **Configurar rate limiting** en LLM manager
6. **Habilitar HTTPS** con reverse proxy (Nginx)

---

## Flujo Completo de Ejemplo

### Escenario: Usuario busca "Juegos de horror baratos"

```
1️⃣  ENTRADA
    POST /consulta
    {"pregunta": "Juegos de horror baratos"}

2️⃣  TOKENIZACIÓN
    sentence-transformers genera embedding 768D
    ▶ Vector: [0.234, -0.156, 0.892, ...]

3️⃣  BÚSQUEDA ELASTICSEARCH
    Query híbrida:
    - kNN sobre vector_embedding
    - BM25 sobre descripción (horror, barato)
    Resultado: 5 documentos relevantes
    ├─ Amnesia: The Dark Descent (similitud: 0.95)
    ├─ SOMA (similitud: 0.91)
    ├─ The Evil Within (similitud: 0.88)
    ├─ Resident Evil 4 Remake (similitud: 0.85)
    └─ Dead Space Remake (similitud: 0.83)

4️⃣  CONSTRUCCIÓN DE PROMPT
    "Basado en estos juegos recomendados:
    1. Amnesia: The Dark Descent - Horror psicológico puro...
    2. SOMA - Horror existencial...
    3. [más documentos]
    
    El usuario pregunta: 'Juegos de horror baratos'
    
    Proporciona una recomendación útil considerando presupuesto,
    género y experiencia de los juegos."

5️⃣  GENERACIÓN CON LLM
    OpenRouter (gemini-2.0-flash-lite-001)
    Respuesta: "Para juegos de horror baratos, te recomiendo:
    
    1. **Amnesia: The Dark Descent** - Clásico del terror psicológico,
       generalmente a menos de $10.
    
    2. **SOMA** - Narrativa profunda con horror existencial,
       frecuentemente en oferta.
    
    [más recomendaciones personalizadas]"

6️⃣  RESPUESTA AL CLIENTE
    {
      "pregunta_realizada": "Juegos de horror baratos",
      "score_similitud_elasticsearch": 0.91,
      "modelo_llm_respuesta": {
        "formato_texto_completo": "Para juegos de horror baratos..."
      }
    }

7️⃣  LOGGING
    tokens_usage.json registra:
    {
      "timestamp": "2025-12-09 14:32:15",
      "pregunta": "Juegos de horror baratos",
      "tokens_input": 245,
      "tokens_output": 512,
      "costo": 0.0034
    }
```

---

## Monitoreo y Mantenimiento

### Logs

- **API Principal**: `logs/llm_manager.log`
- **Tokens/Métricas**: `logs/tokens_usage.json`
- **Docker**: `docker-compose logs api-llm`

### Health Check

```bash
# Endpoint health (recomendado agregar)
curl http://localhost:8000/health

# Verificar Elasticsearch
curl http://localhost:9200/_cat/indices

# Contar documentos en índice
curl http://localhost:9200/steam_games-*/_count
```

### Optimizaciones

1. **Caché de embeddings**: Guardar embeddings frecuentes en Redis
2. **Batch indexing**: Procesar datos en lotes
3. **Query timeout**: Agregar timeouts a queries ES
4. **Rate limiting**: Limitar requests por IP
5. **Compresión**: Comprimir respuestas HTTP

---

##  Contribución

Este proyecto forma parte del **Reto 1 - Sistema RAG para Steam Games**, basado en búsqueda y recomendación de videojuegos.

**Repositorio**: `g6r12025steam-ai-chatbot`  
**Owner**: ai-somorrostro  
**Rama actual**: feature/revision-final-api  
**Autor**: Equipo G6  

---

## Estructura del proyecto completo (multirepositorio)

**Última actualización**: Diciembre 2025  
**Versión API**: 1.0  
**Rama**: `feature/revision-final-api`


# Para ¡¡¡ VALIDACION !!!

- Requirements para el cambion

```python

--extra-index-url https://download.pytorch.org/whl/cpu
torch
fastapi
uvicorn[standard]
python-dotenv

# Embeddings ONNX
onnxruntime
numpy==1.26.4

# Chroma (por si quieres vector DB local)
chromadb

# Data handling
ndjson
requests
tqdm

# Elasticsearch
elasticsearch

# Testing
pytest
sentence-transformers

```

**Modificar el .env a esto**

```python
# Elasticsearch Configuration (Externo - levantado manualmente)
ELASTIC_URLS=https://localhost:9200  <----- de http --> https
ELASTIC_INDEX_PREFIX=steam_games-*
ELASTIC_PASSWORD=C0HcF=wHWtmHAnScY46f  <----- Cambiar
ELASTIC_USER=elastic   

# OpenRouter LLM Configuration
OPENROUTER_API_KEY=sk-or-v1-apikey-aqui


# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO

```

**Modificar el elasticsearch_connector**

```python
import os
import logging
import re 
from typing import Tuple
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from api_llm.utils.tokenizer import generar_embedding

load_dotenv()
logger = logging.getLogger(__name__)

# ================================
# Configuración conexión segura con USUARIO Y CONTRASEÑA
# ================================

ELASTIC_URLS = os.getenv("ELASTIC_URLS", "").split(",")
ELASTIC_INDEX_PREFIX = os.getenv("ELASTIC_INDEX_PREFIX", "steam_games-*")

# Obtener credenciales del .env
ELASTIC_USER = os.getenv("ELASTIC_USER", "elastic")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "changeme") # Pon un valor por defecto o déjalo vacío

if not ELASTIC_PASSWORD or ELASTIC_PASSWORD == "changeme":
    print("⚠️ ADVERTENCIA: Usando contraseña por defecto o vacía para Elasticsearch.")

es = Elasticsearch(
    hosts=ELASTIC_URLS,
    basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD), # <--- AQUÍ ESTÁ EL CAMBIO
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
    Realiza búsqueda VECTORIAL PURA (texto comentado).
    Si detecta un precio, filtra numéricamente.
    Devuelve: (Contexto formateado, Score de relevancia 0.0 - 1.0)
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

        match_precio = re.search(r'(\d+[.,]\d{1,2}|\d+)', pregunta)
        
        query = {}

        if match_precio and any(x in pregunta.lower() for x in ['precio', 'cuesta', 'vale', 'euros', 'eur', '$']):
            try:
                precio_str = match_precio.group(1).replace(',', '.')
                precio_target = float(precio_str)
                logger.info(f"Filtro numérico activado: Buscando precio cercano a {precio_target}")

                # CORRECCIÓN: Usamos la estructura nativa 'knn' con 'filter'
                query = {
                    "size": top_k,
                    "_source": source_fields,
                    "knn": {
                        "field": "vector_embedding",
                        "query_vector": embedding,
                        "k": top_k,
                        "num_candidates": candidates,
                        "filter": {
                            "range": {
                                "price_final": {
                                    "gte": precio_target - 0.05, 
                                    "lte": precio_target + 0.05
                                }
                            }
                        }
                    }
                }
            except ValueError:
                pass

        if not query:
            query = {
                "size": top_k, 
                "_source": source_fields,
                "knn": {
                    "field": "vector_embedding", 
                    "query_vector": embedding,
                    "k": top_k,
                    "num_candidates": candidates,
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
```

**Ejecucion de fastapi (paso final)**

```bash
uvicorn api_llm.main:app
```

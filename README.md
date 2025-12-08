# API RETO 1 – RAG con Steam Games

## 📌 Descripción
API REST basada en **FastAPI** que implementa un sistema RAG (Retrieval-Augmented Generation) para consultas sobre videojuegos de Steam:

1. **Scraping + Extracción**: Pipeline automatizada de Steam API con filtrado inteligente
2. **Resumen IA**: Generación de descripciones concisas mediante OpenRouter GPT-4o-mini
3. **Búsqueda semántica vectorial**: Embeddings + búsqueda kNN en Elasticsearch
4. **Generación de respuestas**: LLM `google/gemini-2.0-flash-lite-001` (OpenRouter)
5. **Modelo multilingüe**: `paraphrase-multilingual-mpnet-base-v2` (768 dims)

---

## 🏗️ Arquitectura

```
Usuario → FastAPI /consulta
    ↓
1. Genera embedding de pregunta (768 dims)
    ↓
2. Búsqueda kNN en Elasticsearch (top 5)
    ↓
3. Contexto de juegos → LLM (OpenRouter Gemini)
    ↓
4. Respuesta al usuario
```

### **Estructura del Proyecto**
```
API-Reto-1/
├── api_llm/
│   ├── main.py                         # FastAPI + CORS
│   ├── llm_manager.py                  # OpenRouter client
│   ├── models/consulta_request.py      # Input Pydantic
│   ├── router/consulta_router.py       # Endpoint /consulta
│   ├── utils/
│   │   ├── elasticsearch_connector.py  # Búsqueda kNN
│   │   ├── tokenizer.py                # Embeddings
│   │   └── helpers.py                  # Utilidades
├── scripts-ingesta-datos/
│   └── json-a-elasticsearch.py         # Carga NDJSON → ES
├── logs/
│   └── tokens_usage.json               # Tracking de uso LLM
├── tests/
├── .env / .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## 🚀 Instalación

### **1. Entorno Virtual**
```bash
cd /home/g6/API-Reto-1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Variables de Entorno**
Crea `.env` basándote en `.env.example`:
```bash
# OpenRouter (para LLM)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=google/gemini-2.0-flash-lite-001

# Embeddings
EMBEDDING_MODEL=paraphrase-multilingual-mpnet-base-v2

# Elasticsearch
ELASTIC_URL=http://localhost:9200
ELASTIC_INDEX=steam_games

# Dataset
DATASET_PATH=/home/g6/reto/scraper/data/steam-games-data-vect.ndjson
```

### **3. Iniciar Elasticsearch**
```bash
cd /home/g6/reto/elasticsearch-9.2.1
./bin/elasticsearch

# O con Docker:
docker run -d -p 9200:9200 -e "discovery.type=single-node" \
  --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:9.2.1
```

### **4. Pipeline Completo de Datos**
```bash
# Ejecutar scraping + vectorización + resúmenes + sincronización
cd /home/g6/reto/scraper
bash setup.sh
```

**Flujo interno de `setup.sh`:**
1. `run_pipeline.py` - Scraping de Steam API (5,001 juegos)
2. `vectorizador.py` - Generación de embeddings (768 dims)
3. `/home/g6/reto/imp-futuras/flux.sh` - Pipeline de resúmenes IA
   - `extract-desc-nuevas.py` - Extrae descripciones de nuevos juegos
   - `openrouter-call.py` - Genera resúmenes con GPT-4o-mini
   - `clean-summary.sh` - Limpia formato JSON
4. `desc-changer.py` - Reemplaza descripciones con resúmenes IA
5. Sincronización remota via SCP

### **5. Cargar Datos en Elasticsearch**
```bash
cd /home/g6/API-Reto-1
python scripts-ingesta-datos/json-a-elasticsearch.py
```

### **6. Ejecutar API**
```bash
uvicorn api_llm.main:app --reload --port 8000
```

**API disponible en:** http://localhost:8000  
**Documentación interactiva:** http://localhost:8000/docs

---

## 📡 Endpoint Principal

### **POST /consulta**

**Request:**
```json
{
  "pregunta": "¿Cuáles son los mejores juegos de estrategia en tiempo real?"
}
```

**Response:**
```json
{
  "pregunta": "¿Cuáles son los mejores juegos de estrategia en tiempo real?",
  "contexto_usado": "Título: Stellaris\nDescripción: Juego de gran estrategia espacial...\n\nTítulo: Total War: WARHAMMER III\nDescripción: ...",
  "respuesta": "Basándome en los datos de Steam, algunos de los mejores juegos de estrategia en tiempo real son: Stellaris, que ofrece exploración galáctica profunda y diplomacia compleja; Total War: WARHAMMER III con batallas épicas..."
}
```

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:8000/consulta \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "Recomiéndame juegos de terror multijugador para jugar con amigos"}'
```

---

## 🔍 Funcionamiento Detallado

### **1. Pipeline de Datos (Previo a API)**

#### **A. Scraping Inicial** (`/home/g6/reto/scraper/`)
```bash
# scripts/run_pipeline.py
- Obtiene lista de top juegos de Steam
- Filtra por palabras clave (DLC, soundtracks, adult content)
- Extrae detalles completos de cada juego
- Output: steam-top-games.json (5,001 juegos únicos)
```

#### **B. Extracción de Descripciones** (`/home/g6/reto/imp-futuras/`)
```bash
# scripts/extract-desc-nuevas.py
- Lee steam-top-games.json
- Compara con raw-desc.ndjson para evitar duplicados
- Extrae steam_id, name, detailed_description desde Steam API
- Limpia HTML preservando UTF-8
- Output: raw-desc.ndjson (append mode)
```

#### **C. Generación de Resúmenes IA**
```bash
# scripts/openrouter-call.py
- Carga descripciones desde raw-desc.ndjson
- Llama a OpenRouter GPT-4o-mini con prompt especializado:
  * Género, Ambientación, Mecánicas, Tono
  * Detección de DLCs/expansiones
  * Detección de contenido adulto
- 7 hilos paralelos, deduplicación automática
- Output: summary.ndjson (4,717 resúmenes)
```

#### **D. Reemplazo de Descripciones**
```bash
# scripts/desc-changer.py
- Compara IDs entre summary.ndjson y steam-games-data.ndjson
- Reemplaza detailed_description con resúmenes IA
- Crea backup automático
- Output: steam-games-data.ndjson actualizado
```

#### **E. Vectorización**
```bash
# scripts/vectorizador.py
- Modelo: paraphrase-multilingual-mpnet-base-v2
- Vectoriza: Título + Desarrollador + Géneros + Tags + Summary + Details
- Output: steam-games-data-vect.ndjson (768 dims por juego)
```

### **2. Embeddings en API** (`tokenizer.py`)
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
embedding = model.encode(["¿Juegos de terror?"])[0]  # Array de 768 floats
```

### **3. Búsqueda kNN en Elasticsearch** (`elasticsearch_connector.py`)
```python
query = {
    "query": {
        "knn": {
            "vector_embedding": {
                "vector": embedding,
                "k": 5,  # Top 5 resultados
                "num_candidates": 100
            }
        }
    },
    "_source": ["name", "detailed_description", "genres", "price_eur"]
}
results = es.search(index="steam_games", body=query)
```

### **4. Generación de Respuesta con LLM** (`llm_manager.py`)
```python
payload = {
    "model": "google/gemini-2.0-flash-lite-001",
    "messages": [
        {
            "role": "system",
            "content": "Eres un experto en videojuegos que ayuda a usuarios a encontrar juegos basándose en datos de Steam..."
        },
        {
            "role": "user",
            "content": f"CONTEXTO:\n{contexto}\n\nPREGUNTA:\n{pregunta}"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 500
}
response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload)
```

---

## 📊 Formato de Datos

### **NDJSON Vectorizado** (`steam-games-data-vect.ndjson`)
```json
{
  "steam_id": 730,
  "name": "Counter-Strike 2",
  "detailed_description": "Counter-Strike 2 es un juego de disparos en primera persona (FPS) competitivo ambientado en escenarios urbanos y tácticos. Las mecánicas principales incluyen un enfoque en objetivos...",
  "short_description": "Durante las dos últimas décadas, Counter‑Strike ha proporcionado...",
  "genres": ["Acción", "Free to Play"],
  "categories": ["Multijugador", "JcJ", "Cromos de Steam"],
  "developers": ["Valve"],
  "publishers": ["Valve"],
  "price_eur": 0.0,
  "is_free": true,
  "release_date": "2012-08-21",
  "metacritic_score": 0,
  "recommendations_total": 4798323,
  "vector_embedding": [0.023, -0.12, 0.045, ..., 0.056]  // 768 dimensiones
}
```

### **Documento en Elasticsearch**
Mismo formato que NDJSON, indexado con mapping kNN:
```json
{
  "mappings": {
    "properties": {
      "vector_embedding": {
        "type": "dense_vector",
        "dims": 768,
        "index": true,
        "similarity": "cosine"
      },
      "name": {"type": "text"},
      "detailed_description": {"type": "text"},
      "genres": {"type": "keyword"}
    }
  }
}
```

---

## 🧪 Testing

```bash
# Tests unitarios
pytest tests/ -v

# Test específico de endpoints
pytest tests/test_endpoints.py

# Test de respuesta LLM
pytest tests/test_llm_response.py
```

---

## 🐳 Docker Compose

```bash
# Iniciar todo el stack (API + Elasticsearch)
docker-compose up -d

# API: http://localhost:8000
# Elasticsearch: http://localhost:9200
# Logs: docker-compose logs -f
```

**`docker-compose.yml`** incluye:
- Elasticsearch 9.2.1 con kNN habilitado
- API FastAPI con auto-reload
- Volúmenes persistentes para datos

---

## 📚 Flujo Completo End-to-End

```
1. Scraping (setup.sh)
   ├── Steam API → steam-top-games.json
   ├── Filtrado (DLC, soundtracks, adult)
   └── Detalles completos → steam-games-data.ndjson

2. Resúmenes IA (flux.sh)
   ├── extract-desc-nuevas.py → raw-desc.ndjson
   ├── openrouter-call.py → summary.ndjson
   └── clean-summary.sh → formato limpio

3. Integración
   └── desc-changer.py → reemplaza descripciones

4. Vectorización
   └── vectorizador.py → steam-games-data-vect.ndjson (768 dims)

5. Ingesta
   └── json-a-elasticsearch.py → Elasticsearch index

6. API RAG
   └── /consulta → Embedding + kNN + LLM → Respuesta
```

---

## 📦 Dependencias Principales

### **API**
- `fastapi==0.115.12` - Framework web async
- `uvicorn==0.34.0` - Servidor ASGI
- `elasticsearch==8.16.0` - Cliente ES Python
- `sentence-transformers==3.3.1` - Embeddings multilingües
- `requests==2.32.3` - HTTP client para OpenRouter
- `python-dotenv==1.0.1` - Gestión de variables entorno
- `pydantic==2.10.6` - Validación de datos

### **Pipeline de Datos**
- `openai>=1.0.0` - Cliente OpenRouter compatible
- `beautifulsoup4` - Parsing HTML (limpieza de descripciones)
- `torch` (CPU-only) - Backend para sentence-transformers

---

## 🔧 Troubleshooting

### **Error: Elasticsearch no conecta**
```bash
# Verificar que Elasticsearch está corriendo
curl http://localhost:9200

# Ver logs
docker logs elasticsearch
```

### **Error: Modelo de embeddings no se descarga**
```bash
# Descargar manualmente
cd /home/g6/reto/scraper
python scripts/instalar_modelo.py
```

### **Error: OpenRouter API Key inválida**
```bash
# Verificar .env
cat /home/g6/API-Reto-1/.env | grep OPENROUTER_API_KEY

# Verificar permisos de .env
chmod 600 .env
```

### **Error: Datos no aparecen en consultas**
```bash
# Verificar índice en Elasticsearch
curl http://localhost:9200/steam_games/_count

# Recargar datos
python scripts-ingesta-datos/json-a-elasticsearch.py
```

---

## 📈 Métricas y Monitoreo

- **Logs de uso de tokens**: `/logs/tokens_usage.json`
- **Métricas de scraping**: `/home/g6/reto/scraper/logs/scraper_metrics.log`
- **Resúmenes generados**: 4,717 juegos
- **Total de juegos únicos**: 5,001
- **Dimensionalidad de vectores**: 768

---

## 🤝 Contribución

Este proyecto forma parte del Reto 1 - Sistema RAG para Steam Games, basado en recomendación para videojuegos.

**Repositorio**: `g6r12025steam-ai-chatbot`  
**Autor**: Equipo G6  
**Contacto**: iker.ortiz02@somo.eus


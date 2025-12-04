# API RETO 1 – RAG con Steam Games

## 📌 Descripción
API REST basada en **FastAPI** que implementa un sistema RAG (Retrieval-Augmented Generation) para consultas sobre videojuegos de Steam:

1. **Búsqueda semántica vectorial**: Embeddings + búsqueda kNN en Elasticsearch
2. **Generación de respuestas**: LLM `google/gemini-2.0-flash-lite-001` (OpenRouter)
3. **Modelo multilingüe**: `paraphrase-multilingual-mpnet-base-v2` (768 dims)

---

## 🏗️ Arquitectura

```
Usuario → FastAPI /consulta
    ↓
1. Genera embedding de pregunta
    ↓
2. Búsqueda kNN en Elasticsearch (top 5)
    ↓
3. Contexto → LLM (OpenRouter Gemini)
    ↓
4. Respuesta al usuario
```

### **Estructura**
```
API-Reto-1/
├── api_llm/
│   ├── main.py                         # FastAPI + CORS
│   ├── llm_manager.py                  # OpenRouter
│   ├── models/consulta_request.py      # Input Pydantic
│   ├── router/consulta_router.py       # Endpoint /consulta
│   ├── utils/
│   │   ├── elasticsearch_connector.py  # Búsqueda kNN
│   │   ├── tokenizer.py                # Embeddings
│   │   └── helpers.py                  # Utilidades
├── scripts-ingesta-datos/
│   └── json-a-elasticsearch.py         # Carga NDJSON → ES
├── tests/
├── .env
├── requirements.txt
└── docker-compose.yml
```

---

## 🚀 Instalación

```bash
# 1. Entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Dependencias
pip install -r requirements.txt

# 3. Variables de entorno (.env)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=google/gemini-2.0-flash-lite-001
EMBEDDING_MODEL=paraphrase-multilingual-mpnet-base-v2
ELASTIC_URL=http://localhost:9200
ELASTIC_INDEX=steam_games
DATASET_PATH=data/steam_games_data_vect.ndjson

# 4. Iniciar Elasticsearch
docker run -d -p 9200:9200 -e "discovery.type=single-node" \
  --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:9.2.1

# 5. Cargar datos
python scripts-ingesta-datos/json-a-elasticsearch.py

# 6. Ejecutar API
uvicorn api_llm.main:app --reload --port 8000
```

---

## 📡 Endpoint Principal

### **POST /consulta**

**Request:**
```json
{
  "pregunta": "¿Cuáles son los mejores juegos de estrategia?"
}
```

**Response:**
```json
{
  "pregunta": "¿Cuáles son los mejores juegos de estrategia?",
  "contexto_usado": "Título: Civilization VI\nDescripción: ...",
  "respuesta": "Basándome en los datos, algunos juegos destacados son..."
}
```

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:8000/consulta \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "Recomiéndame juegos de terror multijugador"}'
```

---

## 🔍 Funcionamiento

### **1. Embeddings (`tokenizer.py`)**
```python
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
embedding = model.encode(["¿Juegos de terror?"])[0]  # 768 dims
```

### **2. Búsqueda kNN (`elasticsearch_connector.py`)**
```python
query = {
    "query": {
        "knn": {
            "vector_embedding": {"vector": embedding, "k": 5}
        }
    }
}
response = es.search(index="steam_games", body=query)
```

### **3. LLM (`llm_manager.py`)**
```python
payload = {
    "model": "google/gemini-2.0-flash-lite-001",
    "messages": [
        {"role": "system", "content": "Eres experto en videojuegos..."},
        {"role": "user", "content": f"CONTEXT:\n{contexto}\n\nQUESTION:\n{pregunta}"}
    ]
}
```

---

## 📊 Formato de Datos

**Documento en Elasticsearch:**
```json
{
  "steam_id": 730,
  "name": "Counter-Strike 2",
  "detailed_description": "Juego de disparos táctico...",
  "genres": ["Acción", "FPS"],
  "price_eur": 0.0,
  "is_free": true,
  "vector_embedding": [0.023, -0.12, ..., 0.056]  // 768 dims
}
```

---

## 🐳 Docker

```bash
# Construir y ejecutar
docker-compose up -d

# API: http://localhost:8000
# Elasticsearch: http://localhost:9200
```

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📚 Pipeline Completo

1. **Scraping**: `/home/g6/reto/scraper/setup.sh` → `steam-games-data-vect.ndjson`
2. **Ingesta**: `json-a-elasticsearch.py` → Elasticsearch
3. **API**: `uvicorn api_llm.main:app` → `/consulta`

---

## 📦 Dependencias Principales

- `fastapi` / `uvicorn` - Framework web
- `elasticsearch` - Cliente ES
- `sentence-transformers` - Embeddings
- `requests` - Llamadas HTTP
- `python-dotenv` - Variables entorno


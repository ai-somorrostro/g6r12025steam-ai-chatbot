# API RETO 1 – LLM + Elasticsearch

## 📌 Descripción
API REST desarrollada en FastAPI que:
- Recibe consultas del usuario.
- Busca información relevante en Elasticsearch (`steam_games`).
- Genera una respuesta enriquecida mediante un modelo LLM de OpenRouter.
- Utiliza embeddings ONNX para ranking semántico adicional.

---

## 🚀 Ejecutar la API

### 1. Crear entorno
```bash
python3 -m venv venv
source venv/bin/activate

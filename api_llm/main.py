from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_llm.router import consulta_router

# ==============================
# Inicialización de la API FastAPI
# ==============================

app = FastAPI(title="API Reto 1 - Steam LLM")

# CORS por si se accede desde frontend externo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(consulta_router.router, prefix="")

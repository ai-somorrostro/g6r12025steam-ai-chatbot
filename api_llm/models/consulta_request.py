from pydantic import BaseModel, Field

# =============================
# Modelo de entrada para /consulta
# =============================

class ConsultaRequest(BaseModel):
    pregunta: str = Field(..., description="Pregunta del usuario que será enviada al LLM")

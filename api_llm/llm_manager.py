import os
import requests
from dotenv import load_dotenv
from api_llm.utils.helpers import truncar_texto

load_dotenv()

# ============================
# Parámetros de entorno
# ============================

API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-lite-001")

# ============================
# Prompt base del sistema
# ============================

SYSTEM_PROMPT = (
    "Eres un asistente experto en videojuegos de Steam."
    " Responde a las preguntas del usuario usando exclusivamente el contexto proporcionado."
    " Si no sabes la respuesta con claridad, di que no tienes suficiente información."
)


# ============================
# Función principal
# ============================

def obtener_respuesta_llm(pregunta: str, contexto: str) -> str:
    prompt_usuario = f"""CONTEXT:
{truncar_texto(contexto)}

QUESTION:
{pregunta}
"""

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_usuario}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        respuesta_llm = response.json()["choices"][0]["message"]["content"]
        return respuesta_llm.strip()
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

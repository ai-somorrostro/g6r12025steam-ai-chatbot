import os
import logging
import json
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
import requests
from api_llm.utils.helpers import truncar_texto

load_dotenv()
os.makedirs("logs", exist_ok=True)

# ============================
# Logging
# ============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/llm_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================
# Entorno
# ============================
API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-lite-001")
LOCAL_MODEL_ENABLED = os.getenv("LOCAL_MODEL_ENABLED", "false").lower() == "true"
LOCAL_MODEL_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:5000")

# ============================
# Prompt con PERSONALIDAD (Mejorado para Opinión vs Venta)
# ============================
SYSTEM_PROMPT = (
    "Actúa como un experto en videojuegos de Steam, amigable, entusiasta y con criterio propio (como un amigo gamer veterano). "
    "Tienes acceso a una lista de juegos con sus precios (CONTEXTO). Tu comportamiento depende de lo que pida el usuario:\n\n"

    "🎯 **MODOS DE RESPUESTA:**\n"
    "1. **Si piden OPINIÓN (ej: '¿Qué opinas de Battlefield?', '¿Es bueno X juego?'):**\n"
    "   - ¡NO hagas una lista de precios inmediatamente!\n"
    "   - Usa tu conocimiento general para dar una crítica cualitativa sobre la jugabilidad, historia o mecánicas (ej: 'Es caótico y realista', 'La historia es increíble').\n"
    "   - Menciona si el juego está en el contexto disponible y su precio de forma narrativa (ej: 'Y lo mejor es que lo tengo por aquí a 49.99 EUR').\n"
    "   - No menciones otros juegos que no tengan nada que ver.\n\n"
    
    "2. **Si piden RECOMENDACIONES o BÚSQUEDA (ej: 'Busco juegos de tiros', 'Dame algo barato'):**\n"
    "   - Busca similitudes conceptuales si no hay coincidencia exacta.\n"
    "   - Usa el formato de lista estructurada.\n\n"

    "🧠 **Reglas de Razonamiento:**\n"
    "1. **Contexto estricto para disponibilidad:** Solo puedes vender/ofrecer lo que está en el CONTEXTO. Si te preguntan por un juego que NO está en la lista, di: 'Ese juegazo no lo tengo en mi lista ahora mismo, pero... [ofrece alternativa del contexto]'.\n"
    "2. **Conocimiento híbrido:** Usa el contexto para Precios y Títulos exactos, pero usa tu propio conocimiento (entrenamiento del LLM) para describir por qué el juego es divertido.\n\n"

    "🎨 **Estilo de Respuesta:**\n"
    "- Tono cercano: '¡Uff, ese juego es brutal!', 'Mira, sinceramente...'.\n"
    "- Si haces lista, usa Markdown: * **Título** (Precio) - Razón.\n"
    "- Si das opinión, usa párrafos naturales.\n"
)

# ============================
# Monitor de tokens
# ============================
class TokenMonitor:
    """Registra el uso de tokens y métricas de relevancia"""
    
    def __init__(self):
        self.log_file = "logs/tokens_usage.json"
        os.makedirs("logs", exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
    
    def registrar_uso(self, entrada_tokens: int, salida_tokens: int, modelo: str, pregunta: str, respuesta: str, elastic_score: float = 0.0):
        registro = {
            "timestamp": datetime.now().isoformat(),
            "modelo": modelo,
            "tokens_entrada": entrada_tokens,
            "tokens_salida": salida_tokens,
            "tokens_totales": entrada_tokens + salida_tokens,
            "elastic_score": elastic_score,
            "pregunta": pregunta[:100],
            "respuesta": respuesta[:500] 
        }
        try:
            with open(self.log_file, 'r') as f:
                datos = json.load(f)
            datos.append(registro)
            with open(self.log_file, 'w') as f:
                json.dump(datos, f, indent=2)
            logger.info(f"Tokens: In={entrada_tokens}/Out={salida_tokens} | Score Elastic: {elastic_score:.4f}")
        except Exception as e:
            logger.error(f"Error registrando tokens: {str(e)}")

# ============================
# Gestor LLM
# ============================
class LLMManager:
    """Gestor centralizado para LLM locales y remotos"""
    
    def __init__(self):
        self.token_monitor = TokenMonitor()
        self.use_local = LOCAL_MODEL_ENABLED
        logger.info(f"LLM Manager inicializado - Modo local: {self.use_local}")
    
    def obtener_respuesta(self, pregunta: str, contexto: str, elastic_score: float = 0.0) -> Dict[str, Any]:
        if self.use_local:
            return self._obtener_respuesta_local(pregunta, contexto, elastic_score)
        else:
            return self._obtener_respuesta_remota(pregunta, contexto, elastic_score)
    
    def _obtener_respuesta_local(self, pregunta: str, contexto: str, elastic_score: float) -> Dict[str, Any]:
        prompt_usuario = f"CONTEXTO DE JUEGOS DISPONIBLES:\n{truncar_texto(contexto)}\n\nPREGUNTA DEL USUARIO:\n{pregunta}"
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_usuario}
            ],
            "stream": False,
            "max_tokens": 3000
        }
        try:
            logger.info(f"Enviando consulta a modelo local: {LOCAL_MODEL_URL}")
            response = requests.post(f"{LOCAL_MODEL_URL}/v1/chat/completions", json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            respuesta = data["choices"][0]["message"]["content"]
            tokens_entrada = len(prompt_usuario.split())
            tokens_salida = len(respuesta.split())
            
            self.token_monitor.registrar_uso(tokens_entrada, tokens_salida, "local", pregunta, respuesta, elastic_score)
            
            return {
                "respuesta": respuesta.strip(),
                "tokens_entrada": tokens_entrada,
                "tokens_salida": tokens_salida,
                "elastic_score": elastic_score,
                "modelo": "local",
                "error": None
            }
        except Exception as e:
            logger.error(f"Error en modelo local: {str(e)}")
            logger.info("Fallback a modelo remoto...")
            return self._obtener_respuesta_remota(pregunta, contexto, elastic_score)
    
    def _obtener_respuesta_remota(self, pregunta: str, contexto: str, elastic_score: float) -> Dict[str, Any]:
        prompt_usuario = f"CONTEXTO DE JUEGOS DISPONIBLES:\n{truncar_texto(contexto)}\n\nPREGUNTA DEL USUARIO:\n{pregunta}"
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
            ],
            "temperature": 0.7, # Un poco de creatividad para que sea amable
            "max_tokens": 3000
        }
        try:
            logger.info(f"Enviando consulta a OpenRouter con modelo: {LLM_MODEL}")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            respuesta = data["choices"][0]["message"]["content"]
            tokens_entrada = data.get("usage", {}).get("prompt_tokens", 0)
            tokens_salida = data.get("usage", {}).get("completion_tokens", 0)
            
            self.token_monitor.registrar_uso(tokens_entrada, tokens_salida, LLM_MODEL, pregunta, respuesta, elastic_score)
            
            return {
                "respuesta": respuesta.strip(),
                "tokens_entrada": tokens_entrada,
                "tokens_salida": tokens_salida,
                "elastic_score": elastic_score,
                "modelo": LLM_MODEL,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error al generar respuesta: {str(e)}")
            return self._generar_respuesta_error(str(e))
    
    def _generar_respuesta_error(self, error_msg: str) -> Dict[str, Any]:
        return {
            "respuesta": f"Vaya, he tenido un problema técnico y no puedo responderte ahora mismo. (Error: {error_msg})",
            "tokens_entrada": 0,
            "tokens_salida": 0,
            "modelo": None,
            "error": error_msg
        }

def obtener_respuesta_llm(pregunta: str, contexto: str, elastic_score: float = 0.0) -> str:
    manager = LLMManager()
    resultado = manager.obtener_respuesta(pregunta, contexto, elastic_score)
    return resultado["respuesta"]
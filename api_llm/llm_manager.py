import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import requests
from api_llm.utils.helpers import truncar_texto

load_dotenv()
os.makedirs("logs", exist_ok=True)

# ============================
# DOCUMENTACIÓN TÉCNICA: ORIGEN DE DATOS Y ARQUITECTURA
# ============================
# 1. FUENTE DE DATOS: Indexación vectorial de catálogo Steam en Elasticsearch.
# 2. ARQUITECTURA: Conexión directa a API remota (OpenRouter) para inferencia.
# 3. ROL DEL LINGÜISTA / PROMPT ENGINEER:
#    - Diseño del "System Persona" para ajustar el registro comunicativo.
#    - Definición de reglas pragmáticas para diferenciar "Opinión" vs "Venta".
#    - Estrategias de mitigación de alucinaciones (Grounding).
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
# Configuración del Entorno (Solo Remoto)
# ============================
API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-lite-001")

# Hiperparámetros del modelo LLM
# Temperature: Controla la creatividad (0.7 = balanceado).
# Top_P: Filtra respuestas incoherentes.
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))

# ============================
# Prompt Engineering (Diseño Lingüístico)
# ============================
SYSTEM_PROMPT = (
    # --- CAPA 1: DEFINICIÓN DE PERSONA Y REGISTRO ---
    "Actúa como un experto en videojuegos de Steam. "
    "Tu registro lingüístico debe ser: Amigable, entusiasta, coloquial (jerga gamer) pero respetuoso. "
    "FUENTE DE VERDAD: Tienes acceso exclusivo a un fragmento de base de datos inyectado como 'CONTEXTO'.\n\n"

    # --- CAPA 2: REGLAS PRAGMÁTICAS (INTENCIÓN) ---
    "Tu comportamiento lingüístico se adapta a la intención del usuario:\n"
    "🎯 **INTENCIÓN: OPINIÓN (Evaluativa)**\n"
    "   - Estructura: Crítica cualitativa + Mención narrativa de precio.\n"
    "   - Foco: Jugabilidad, historia, mecánicas.\n"
    "   - Restricción: No listes precios sin contexto narrativo.\n\n"
    
    "🎯 **INTENCIÓN: BÚSQUEDA/RECOMENDACIÓN (Transaccional)**\n"
    "   - Estructura: Lista Markdown estructurada.\n"
    "   - Foco: Relación calidad/precio y similitud conceptual.\n\n"

    # --- CAPA 3: RESTRICCIONES SEMÁNTICAS Y GROUNDING ---
    "🧠 **Reglas de Procesamiento de Información:**\n"
    "1. **Principio de Veracidad (Grounding):** Solo puedes ofrecer productos presentes en el CONTEXTO recuperado. "
    "Si el juego no está en el contexto, explicita la falta de información.\n"
    "2. **Integración de Conocimiento:** Usa los DATOS del contexto para información objetiva (Precios) "
    "y tu ENTRENAMIENTO base para información subjetiva (Descripción de diversión).\n\n"

    "🚨 REGLA SUPREMA: El 'CONTEXTO' es tu única fuente de datos transaccionales. No inventes precios."
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
            "elastic_score": elastic_score, # Métrica de calidad de recuperación
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
# Gestor LLM (Solo OpenRouter)
# ============================
class LLMManager:
    """
    Gestor centralizado para la generación de lenguaje natural.
    Conexión simplificada únicamente a OpenRouter (Gemini).
    
    Limitaciones Técnicas (NLP):
    - Alucinaciones: Se mitigan restringiendo la respuesta al contexto inyectado.
    - Dependencia Externa: Se utiliza OpenRouter como proveedor de inferencia.
    """
    
    def __init__(self):
        self.token_monitor = TokenMonitor()
        self.generation_config = {
            "temperature": LLM_TEMPERATURE,
            "top_p": LLM_TOP_P,
            "max_tokens": LLM_MAX_TOKENS
        }
        logger.info(f"LLM Manager Remoto Inicializado | Config: {self.generation_config}")
    
    def obtener_respuesta(self, pregunta: str, contexto: str, elastic_score: float = 0.0) -> Dict[str, Any]:
        """Envía la consulta directamente a OpenRouter"""
        
        # Inyección de contexto RAG
        prompt_usuario = f"DATOS DE CONTEXTO (Corpus):\n{truncar_texto(contexto)}\n\nINPUT USUARIO:\n{pregunta}"
        
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
            # Hiperparámetros dinámicos
            "temperature": self.generation_config["temperature"],
            "top_p": self.generation_config["top_p"],
            "max_tokens": self.generation_config["max_tokens"]
        }
        
        try:
            logger.info(f"Enviando consulta a OpenRouter: {LLM_MODEL}")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Validación simple de respuesta vacía
            if not data.get("choices"):
                raise ValueError("La API remota devolvió una respuesta vacía.")

            respuesta = data["choices"][0]["message"]["content"]
            
            # Métricas
            usage = data.get("usage", {})
            tokens_entrada = usage.get("prompt_tokens", 0)
            tokens_salida = usage.get("completion_tokens", 0)
            
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
            logger.error(f"Error crítico en LLM: {str(e)}")
            return self._generar_respuesta_error(str(e))
    
    def _generar_respuesta_error(self, error_msg: str) -> Dict[str, Any]:
        return {
            "respuesta": f"Lo siento, tengo un problema técnico de conexión y no puedo responderte ahora mismo. (Error: {error_msg})",
            "tokens_entrada": 0,
            "tokens_salida": 0,
            "modelo": None,
            "error": error_msg
        }

def obtener_respuesta_llm(pregunta: str, contexto: str, elastic_score: float = 0.0) -> str:
    manager = LLMManager()
    resultado = manager.obtener_respuesta(pregunta, contexto, elastic_score)
    return resultado["respuesta"]
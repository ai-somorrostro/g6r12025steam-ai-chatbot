import logging
import os

# Crear carpeta logs si no existe
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logging")
os.makedirs(LOG_DIR, exist_ok=True)

# Archivo principal de logs
LOG_FILE = os.path.join(LOG_DIR, "api.log")

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("api_llm_logger")

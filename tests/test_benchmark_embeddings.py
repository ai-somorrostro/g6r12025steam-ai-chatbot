# # ✅ tests/test_benchmark_embeddings.py
# # Benchmark para evaluar modelos de embeddings

# import time
# import os
# import psutil
# import sys
# import importlib
# import logging
# from pathlib import Path
# from sentence_transformers import SentenceTransformer

# # 📁 Asegura ruta raíz del proyecto
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# # 📝 Logging
# log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
# os.makedirs(log_dir, exist_ok=True)
# log_file = os.path.join(log_dir, "benchmark_embeddings.log")

# logger = logging.getLogger("benchmark_logger_embeddings")
# logger.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(message)s')
# file_handler = logging.FileHandler(log_file, mode='w')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

# # 🧪 Modelos a comparar
# modelos = [
#     "sentence-transformers/all-MiniLM-L6-v2",
#     "intfloat/multilingual-e5-base",
#     "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# ]

# # 📋 Batch de textos para evaluar
# textos = [
#     "¿Qué juegos de simulación hay?",
#     "Quiero juegos con buena historia.",
#     "Busco algo de terror psicológico.",
#     "¿Tienes juegos con multijugador local?",
#     "¿Cuáles son los más baratos?",
# ] * 20  # ➕ Multiplicamos para simular batch de 100

# def medir_rendimiento_embedding(model_name: str):
#     logger.info(f"🔍 Evaluando modelo: {model_name}")

#     # ⏱️ Carga del modelo
#     start = time.time()
#     model = SentenceTransformer(model_name)
#     tiempo_carga = time.time() - start

#     # 🧠 Tamaño en disco
#     model_path = Path(model.cache_folder).joinpath(model_name.replace("/", "_"))
#     if model_path.exists():
#         peso_mb = sum(f.stat().st_size for f in model_path.glob("**/*") if f.is_file()) / (1024 * 1024)
#     else:
#         peso_mb = 0

#     # 💾 Memoria usada antes de la inferencia
#     mem_inicio = psutil.Process(os.getpid()).memory_info().rss

#     # ⏱️ Inferencia
#     start = time.time()
#     _ = model.encode(textos, batch_size=32, show_progress_bar=False)
#     tiempo_inferencia = time.time() - start

#     # 💾 Memoria después
#     mem_final = psutil.Process(os.getpid()).memory_info().rss
#     mem_usada_mb = (mem_final - mem_inicio) / (1024 * 1024)

#     # 📤 Log result
#     logger.info(f"🧠 Tiempo de carga: {tiempo_carga:.2f}s")
#     logger.info(f"⚡ Tiempo de inferencia (100 textos): {tiempo_inferencia:.2f}s")
#     logger.info(f"📦 Tamaño en disco: {peso_mb:.2f} MB")
#     logger.info(f"💾 RAM utilizada en inferencia: {mem_usada_mb:.2f} MB")
#     logger.info("=" * 70)

# def run_benchmark_embeddings():
#     for modelo in modelos:
#         medir_rendimiento_embedding(modelo)

# if __name__ == "__main__":
#     run_benchmark_embeddings()






# ✅ tests/test_benchmark_embeddings.py
# Benchmark para evaluar modelos de embeddings

import time
import os
import psutil
import sys
import logging
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# 📁 Asegura ruta raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 📝 Logging
log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "benchmark_embeddings.log")

logger = logging.getLogger("benchmark_logger_embeddings")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 🧪 Modelos a comparar
modelos = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "intfloat/multilingual-e5-base",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"  # ✅ Tu modelo real
]

# 📋 Textos para similitud semántica (pares)
pares_textos = [
    ("Juego de terror psicológico", "Juego con ambiente de miedo"),
    ("Simulador de granja", "Simulación de vida rural"),
    ("Disparos en primera persona", "FPS con armas de fuego"),
    ("Multijugador local", "Jugar en la misma pantalla"),
    ("Estrategia medieval", "Juego de castillos y reinos"),
]

# 📋 Textos para benchmark general
textos = [t[0] for t in pares_textos] * 20  # ➕ Simulamos 100 textos

def medir_rendimiento_embedding(model_name: str):
    logger.info(f"🔍 Evaluando modelo: {model_name}")

    # ⏱️ Carga del modelo
    start = time.time()
    model = SentenceTransformer(model_name)
    tiempo_carga = time.time() - start

    # 🧠 Tamaño en disco
    try:
        model_path = Path(model._first_module().model_dir)
        peso_mb = sum(f.stat().st_size for f in model_path.glob("**/*") if f.is_file()) / (1024 * 1024)
    except Exception:
        peso_mb = 0

    # 💾 Memoria usada antes de la inferencia
    mem_inicio = psutil.Process(os.getpid()).memory_info().rss

    # ⏱️ Inferencia
    start = time.time()
    _ = model.encode(textos, batch_size=32, show_progress_bar=False)
    tiempo_inferencia = time.time() - start

    # 💾 Memoria después
    mem_final = psutil.Process(os.getpid()).memory_info().rss
    mem_usada_mb = (mem_final - mem_inicio) / (1024 * 1024)

    # 🎯 Evaluación de precisión de similitud semántica
    precisiones = []
    for t1, t2 in pares_textos:
        emb1 = model.encode(t1)
        emb2 = model.encode(t2)
        sim = cosine_similarity([emb1], [emb2])[0][0]
        precisiones.append(sim)
    precision_media = np.mean(precisiones)

    # 📤 Log result
    logger.info(f"🧠 Tiempo de carga: {tiempo_carga:.2f}s")
    logger.info(f"⚡ Tiempo de inferencia (100 textos): {tiempo_inferencia:.2f}s")
    logger.info(f"📦 Tamaño en disco: {peso_mb:.2f} MB")
    logger.info(f"💾 RAM utilizada en inferencia: {mem_usada_mb:.2f} MB")
    logger.info(f"🎯 Precisión media (cosine): {precision_media:.4f}")
    logger.info("=" * 70)

def run_benchmark_embeddings():
    for modelo in modelos:
        medir_rendimiento_embedding(modelo)

if __name__ == "__main__":
    run_benchmark_embeddings()

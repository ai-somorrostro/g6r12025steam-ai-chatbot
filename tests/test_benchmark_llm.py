# tests/test_benchmark_llm.py  
# Evaluación de múltiples LLMs con métricas: latencia, tokens, coste y rendimiento


import time
import sys
import os
import logging
import numpy as np

# Asegura raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_llm.llm_manager import LLMManager
from api_llm.utils.elasticsearch_connector import buscar_contexto_en_elasticsearch

# Carpeta y archivo de logs
log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "benchmark_llm.log")

# Logger
logger = logging.getLogger("benchmark_logger_llm")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Consultas representativas
consultas = [
    "juegos cooperativos",
    "juegos de estrategia medieval",
    "juegos de disparos baratos",
    "terror psicológico",
    "multijugador local"
]

# Coste estimado por 1M tokens (en USD)
costes_por_millon = {
    "openai/gpt-4": 60.0,
    "openai/gpt-3.5-turbo": 1.5,
    "google/gemini-2.0-flash-lite-001": 0.35,
    "mistralai/mixtral-8x7b": 0.6,
    "meta-llama/llama-3-8b": 0.4,
    "claude-3-haiku": 0.25
}

# Modelos a evaluar (usa valores exactos definidos en tu .env OPENROUTER_MODEL)
modelos_a_testear = [
    "google/gemini-2.0-flash-lite-001",
    "mistralai/mixtral-8x7b",
    "meta-llama/llama-3-8b"
]

def run_benchmark_llms():
    for modelo in modelos_a_testear:
        print(f"\n🚀 Evaluando modelo: {modelo}")
        logger.info(f"=== Benchmark modelo: {modelo} ===")
        tiempos_llm = []
        tokens_salida_lista = []

        # Variable de entorno temporal para cambiar modelo
        os.environ["OPENROUTER_MODEL"] = modelo
        llm = LLMManager()  # Se reinicia con nuevo modelo

        for consulta in consultas:
            print(f"\n🧪 Consulta: {consulta}")

            # 🔍 Recuperación semántica
            t0 = time.time()
            contexto, score = buscar_contexto_en_elasticsearch(consulta)
            t_busqueda = time.time() - t0

            # 🤖 LLM
            t0 = time.time()
            resultado = llm.obtener_respuesta(consulta, contexto, score)
            t_llm = time.time() - t0

            # ⚡ Velocidad tokens/s
            tokens_salida = resultado['tokens_salida']
            velocidad = tokens_salida / t_llm if t_llm > 0 else 0

            # 💲 Coste estimado
            coste_modelo = costes_por_millon.get(modelo, 0)
            tokens_total = resultado['tokens_entrada'] + tokens_salida
            coste_estimado = (tokens_total / 1_000_000) * coste_modelo

            # 📊 Acumular datos
            tiempos_llm.append(t_llm)
            tokens_salida_lista.append(tokens_salida)

            # 📺 Terminal
            print("--------------------------------------------")
            print(f"🔍 Score Elastic: {score:.4f}")
            print(f"📚 Tokens: entrada={resultado['tokens_entrada']} | salida={tokens_salida}")
            print(f"⚡ Velocidad: {velocidad:.2f} tokens/seg")
            print(f"💲 Coste estimado: ${coste_estimado:.5f}")
            print(f"⏱️ Tiempo LLM: {t_llm:.2f}s")
            print("📤 Respuesta:")
            print(resultado["respuesta"])

            # 📥 Logging
            logger.info(f"Consulta: {consulta}")
            logger.info(f"Modelo: {modelo}")
            logger.info(f"Elastic score: {score:.4f}")
            logger.info(f"Tokens entrada: {resultado['tokens_entrada']} | salida: {tokens_salida}")
            logger.info(f"Tokens/seg: {velocidad:.2f}")
            logger.info(f"Tiempos -> LLM: {t_llm:.2f}s | Recuperación: {t_busqueda:.2f}s")
            logger.info(f"Coste estimado: ${coste_estimado:.5f}")
            logger.info(f"Respuesta completa:\n{resultado['respuesta']}")
            logger.info("-" * 70)

        # 📈 Estadísticas agregadas por modelo
        p95 = np.percentile(tiempos_llm, 95)
        p99 = np.percentile(tiempos_llm, 99)
        avg_speed = np.mean([t / s if s else 0 for t, s in zip(tiempos_llm, tokens_salida_lista)])

        print(f"\n📊 Estadísticas finales para {modelo}:")
        print(f"   🔸 Tiempo promedio LLM: {np.mean(tiempos_llm):.2f}s")
        print(f"   🔸 P95: {p95:.2f}s | P99: {p99:.2f}s")
        print(f"   🔸 Tokens/seg (media): {avg_speed:.2f}")
        logger.info(f"--- Estadísticas globales modelo {modelo} ---")
        logger.info(f"Tiempo medio LLM: {np.mean(tiempos_llm):.2f}s")
        logger.info(f"P95: {p95:.2f}s | P99: {p99:.2f}s")
        logger.info(f"Tokens/s media: {avg_speed:.2f}")
        logger.info("=" * 80)

if __name__ == "__main__":
    run_benchmark_llms()

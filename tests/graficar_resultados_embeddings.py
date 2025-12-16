# Archivo de para graficar resultados de embeddings

import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import seaborn as sns

# Crear carpeta plots si no existe
plots_dir = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(plots_dir, exist_ok=True)

# Ruta al log
log_file = os.path.join(os.path.dirname(__file__), "..", "logs", "benchmark_embeddings.log")

resultados = {}

# Parseo del log
with open(log_file, "r") as f:
    modelo_actual = None
    for linea in f:
        if "Evaluando modelo:" in linea:
            modelo_actual = linea.split(":")[-1].strip()
            resultados[modelo_actual] = {}
        elif "Tiempo de carga" in linea:
            resultados[modelo_actual]["tiempo_carga"] = float(linea.split(":")[-1].replace("s", ""))
        elif "Tiempo de inferencia" in linea:
            resultados[modelo_actual]["tiempo_inferencia"] = float(linea.split(":")[-1].replace("s", ""))
        elif "RAM utilizada" in linea:
            resultados[modelo_actual]["ram"] = float(linea.split(":")[-1].replace("MB", ""))
        elif "Tamaño en disco" in linea:
            resultados[modelo_actual]["tamano"] = float(linea.split(":")[-1].replace("MB", ""))
        elif "Precisión media" in linea:
            resultados[modelo_actual]["precision"] = float(linea.split(":")[-1])

# Crear PDF
pdf_path = os.path.join(plots_dir, "benchmark_embeddings.pdf")
pdf = PdfPages(pdf_path)

# Función para gráficas de barras
def grafica_barras(clave, ylabel, titulo, color):
    modelos = list(resultados.keys())
    valores = [resultados[m].get(clave, 0) for m in modelos]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(modelos, valores, color=color, alpha=0.75)
    ax.set_title(titulo)
    ax.set_ylabel(ylabel)
    ax.set_xticks(range(len(modelos)))
    ax.set_xticklabels(modelos, rotation=30, ha="right")
    ax.grid(axis="y")
    plt.tight_layout()
    pdf.savefig(fig)
    plt.close()

# Gráficas individuales
grafica_barras("tiempo_carga", "Segundos", "⏳ Tiempo de carga por modelo", "skyblue")
grafica_barras("tiempo_inferencia", "⚡ Segundos", "⚡ Tiempo de inferencia por modelo", "orange")
grafica_barras("ram", "MB", "🧠 Uso de memoria RAM", "lightgreen")
grafica_barras("tamano", "MB", "💾 Tamaño del modelo en disco", "violet")
grafica_barras("precision", "Similitud media", "🎯 Precisión semántica (cosine)", "salmon")

# ===============================
# 🔥 HEATMAP - Comparativa global
# ===============================
# Crear matriz normalizada
modelos = list(resultados.keys())
metricas = ["tiempo_carga", "tiempo_inferencia", "ram", "tamano", "precision"]
matriz = []

for modelo in modelos:
    valores = []
    for m in metricas:
        v = resultados[modelo].get(m, 0.0)
        # Invertimos las métricas donde menos es mejor
        if m != "precision":
            v = 1 / max(v, 1e-6)
        valores.append(v)
    matriz.append(valores)

matriz = np.array(matriz)
# Normalizar valores entre 0 y 1
norm_matriz = (matriz - matriz.min(axis=0)) / (matriz.ptp(axis=0) + 1e-8)

# Crear heatmap
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(norm_matriz, annot=True, cmap="YlGnBu", xticklabels=["Carga", "Inferencia", "RAM", "Tamaño", "Precisión"],
            yticklabels=modelos, cbar_kws={'label': 'Rendimiento relativo'})
ax.set_title("🔥 Comparativa global de modelos de embeddings (normalizada)")
plt.tight_layout()
pdf.savefig(fig)
plt.close()

# Guardar PDF
pdf.close()
print(f"✅ PDF generado correctamente en: {pdf_path}")


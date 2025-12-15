# # ✅ tests/graficar_resultados_embeddings.py
# # 📈 Visualización de resultados del benchmark de modelos de embeddings

# import os
# import re
# import matplotlib.pyplot as plt
# import numpy as np
# from matplotlib.backends.backend_pdf import PdfPages

# # 📁 Ruta al archivo de logs
# log_path = os.path.join("logs", "benchmark_embeddings.log")

# # 📊 Diccionario para guardar datos por modelo
# datos = {}

# # 🧾 Parsear el archivo línea por línea
# with open(log_path, "r", encoding="utf-8") as file:
#     modelo_actual = None
#     for linea in file:
#         if "Evaluando modelo" in linea:
#             modelo_actual = linea.strip().split(":")[-1].strip()
#             datos[modelo_actual] = {}
#         elif "Tiempo de carga" in linea:
#             datos[modelo_actual]["tiempo_carga"] = float(re.search(r"([\d.]+)", linea).group(1))
#         elif "Tiempo de inferencia" in linea:
#             datos[modelo_actual]["tiempo_inferencia"] = float(re.search(r"([\d.]+)", linea).group(1))
#         elif "Tamaño en disco" in linea:
#             datos[modelo_actual]["tamano"] = float(re.search(r"([\d.]+)", linea).group(1))
#         elif "RAM utilizada" in linea:
#             datos[modelo_actual]["ram"] = float(re.search(r"([\d.]+)", linea).group(1))
#         elif "Precisión media" in linea:
#             datos[modelo_actual]["precision"] = float(re.search(r"([\d.]+)", linea).group(1))

# # 📁 Asegura que la carpeta de plots existe
# output_dir = os.path.join("tests", "plots")
# os.makedirs(output_dir, exist_ok=True)

# # 📄 Ruta del PDF de salida
# pdf_path = os.path.join(output_dir, "graficas_embeddings.pdf")

# # 🖼️ Generar PDF con todas las gráficas
# with PdfPages(pdf_path) as pdf:

#     def crear_bar_plot(titulo, ylabel, clave, color):
#         modelos = list(datos.keys())
#         valores = [datos[m][clave] for m in modelos]

#         plt.figure(figsize=(10, 6))
#         plt.bar(modelos, valores, color=color)
#         plt.ylabel(ylabel)
#         plt.title(titulo)
#         plt.grid(True, axis='y')
#         plt.tight_layout()
#         pdf.savefig()
#         plt.close()

#     # 🧠 Generar cada gráfica
#     crear_bar_plot("⏱️ Tiempo de carga por modelo", "Segundos", "tiempo_carga", "skyblue")
#     crear_bar_plot("⚡ Tiempo de inferencia por modelo", "Segundos", "tiempo_inferencia", "orange")
#     crear_bar_plot("💾 RAM usada por modelo", "MB", "ram", "lightgreen")
#     crear_bar_plot("📦 Tamaño del modelo en disco", "MB", "tamano", "violet")
#     crear_bar_plot("🎯 Precisión semántica (cosine)", "Similitud media", "precision", "salmon")

# print(f"✅ PDF generado: {pdf_path}")






### # ✅ tests/graficar_resultados_embeddings.py
# # 📈 Visualización de resultados del benchmark de modelos de embeddings ver correctamente titulos.

# import os
# import re
# import matplotlib.pyplot as plt
# from collections import defaultdict
# from matplotlib.backends.backend_pdf import PdfPages

# # 📁 Ruta al log
# log_path = os.path.join("logs", "benchmark_embeddings.log")

# # 📊 Datos por modelo
# datos = defaultdict(lambda: {
#     "tiempo_carga": None,
#     "tiempo_inferencia": None,
#     "tamano": None,
#     "ram": None,
#     "precision": None
# })

# # 🧾 Parsear log
# with open(log_path, "r", encoding="utf-8") as file:
#     modelo_actual = None
#     for linea in file:
#         if "🔍 Evaluando modelo:" in linea:
#             modelo_actual = linea.strip().split(":")[-1].strip()
#         elif "🧠 Tiempo de carga:" in linea:
#             datos[modelo_actual]["tiempo_carga"] = float(re.search(r"([\d.]+)s", linea).group(1))
#         elif "⚡ Tiempo de inferencia" in linea:
#             datos[modelo_actual]["tiempo_inferencia"] = float(re.search(r"([\d.]+)s", linea).group(1))
#         elif "📦 Tamaño en disco:" in linea:
#             datos[modelo_actual]["tamano"] = float(re.search(r"([\d.]+)", linea).group(1))
#         elif "💾 RAM utilizada" in linea:
#             datos[modelo_actual]["ram"] = float(re.search(r"([\d.]+)", linea).group(1))
#         elif "🎯 Precisión media" in linea:
#             datos[modelo_actual]["precision"] = float(re.search(r"([\d.]+)", linea).group(1))

# # 🖼 Función de graficado genérica
# def crear_grafico(titulo, ylabel, valores, color):
#     modelos = list(valores.keys())
#     metricas = list(valores.values())

#     plt.figure(figsize=(10, 6))
#     plt.bar(modelos, metricas, color=color)
#     plt.ylabel(ylabel)
#     plt.title(titulo)
#     plt.xticks(rotation=25, ha='right')
#     plt.tight_layout()
#     return plt.gcf()

# # 📊 Generar gráficas
# graficas = []

# graficas.append(crear_grafico("🕒 Tiempo de carga por modelo", "Segundos", 
#     {m: datos[m]["tiempo_carga"] for m in datos}, "skyblue"))

# graficas.append(crear_grafico("⚡ Tiempo de inferencia por modelo", "Segundos", 
#     {m: datos[m]["tiempo_inferencia"] for m in datos}, "orange"))

# graficas.append(crear_grafico("💾 RAM usada por modelo", "MB", 
#     {m: datos[m]["ram"] for m in datos}, "lightgreen"))

# graficas.append(crear_grafico("📦 Tamaño del modelo en disco", "MB", 
#     {m: datos[m]["tamano"] for m in datos}, "violet"))

# graficas.append(crear_grafico("🎯 Precisión semántica (cosine)", "Similitud media", 
#     {m: datos[m]["precision"] for m in datos}, "salmon"))

# # 📁 Guardar en PDF
# plots_dir = os.path.join("tests", "plots")
# os.makedirs(plots_dir, exist_ok=True)
# pdf_path = os.path.join(plots_dir, "benchmark_embeddings_resultados.pdf")

# with PdfPages(pdf_path) as pdf:
#     for fig in graficas:
#         pdf.savefig(fig)
#         plt.close(fig)

# print(f"✅ Gráficas guardadas en: {pdf_path}")






# # Codigo final funcional corregido# ✅ tests/graficar_resultados_embeddings.py
# # 📈 Visualización de diferentes gráficas de resultados con grafico de radar corregido.


# import os
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_pdf import PdfPages
# import numpy as np

# # Crear carpeta plots si no existe
# plots_dir = os.path.join(os.path.dirname(__file__), "plots")
# os.makedirs(plots_dir, exist_ok=True)

# # Ruta al log
# log_file = os.path.join(os.path.dirname(__file__), "..", "logs", "benchmark_embeddings.log")

# resultados = {}

# # Parseo del log
# with open(log_file, "r") as f:
#     modelo_actual = None
#     for linea in f:
#         if "Evaluando modelo:" in linea:
#             modelo_actual = linea.split(":")[-1].strip()
#             resultados[modelo_actual] = {}
#         elif "Tiempo de carga" in linea:
#             resultados[modelo_actual]["tiempo_carga"] = float(linea.split(":")[-1].replace("s", ""))
#         elif "Tiempo de inferencia" in linea:
#             resultados[modelo_actual]["tiempo_inferencia"] = float(linea.split(":")[-1].replace("s", ""))
#         elif "RAM utilizada" in linea:
#             resultados[modelo_actual]["ram"] = float(linea.split(":")[-1].replace("MB", ""))
#         elif "Tamaño en disco" in linea:
#             resultados[modelo_actual]["tamano"] = float(linea.split(":")[-1].replace("MB", ""))
#         elif "Precisión media" in linea:
#             resultados[modelo_actual]["precision"] = float(linea.split(":")[-1])

# pdf_path = os.path.join(plots_dir, "benchmark_embeddings.pdf")
# pdf = PdfPages(pdf_path)

# def grafica_barras(clave, ylabel, titulo, color):
#     modelos = list(resultados.keys())
#     valores = [resultados[m][clave] for m in modelos]

#     fig, ax = plt.subplots(figsize=(10, 5))
#     ax.bar(modelos, valores, color=color, alpha=0.75)
#     ax.set_title(titulo)
#     ax.set_ylabel(ylabel)
#     ax.set_xticks(range(len(modelos)))
#     ax.set_xticklabels(modelos, rotation=30, ha="right")
#     ax.grid(axis="y")
#     plt.tight_layout()
#     pdf.savefig(fig)
#     plt.close()

# # Gráficas individuales
# grafica_barras("tiempo_carga", "Segundos", "Tiempo de carga por modelo", "skyblue")
# grafica_barras("tiempo_inferencia", "Segundos", "Tiempo de inferencia por modelo", "orange")
# grafica_barras("ram", "MB", "Uso de memoria RAM", "lightgreen")
# grafica_barras("tamano", "MB", "Tamaño del modelo en disco", "violet")
# grafica_barras("precision", "Similitud media", "Precisión semántica (cosine)", "salmon")

# # Radar chart (comparativa global)
# labels = ["Carga", "Inferencia", "RAM", "Tamaño", "Precisión"]
# angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
# angles += angles[:1]

# fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

# for modelo, d in resultados.items():
#     valores = [
#         1 / max(d["tiempo_carga"], 1e-6),
#         1 / max(d["tiempo_inferencia"], 1e-6),
#         1 / max(d["ram"], 1e-6),
#         1 / max(d["tamano"], 1e-6),
#         d["precision"],
#     ]
#     valores = np.array(valores)
#     valores = valores / valores.max()
#     valores = valores.tolist()
#     valores += valores[:1]  # ← SOLUCIÓN DEL ERROR

#     ax.plot(angles, valores, label=modelo)
#     ax.fill(angles, valores, alpha=0.1)

# ax.set_title("Comparativa global de modelos de embeddings")
# ax.set_xticks(angles[:-1])
# ax.set_xticklabels(labels)
# ax.set_yticklabels([])
# ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1))
# plt.tight_layout()
# pdf.savefig(fig)
# plt.close()

# pdf.close()
# print(f"✅ PDF generado correctamente en: {pdf_path}")







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


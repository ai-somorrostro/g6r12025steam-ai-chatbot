# # 📈 Visualización de resultados del benchmark de LLMs
# import os
# import re
# import matplotlib.pyplot as plt
# import numpy as np
# from collections import defaultdict

# # 📁 Ruta al log
# log_path = os.path.join("logs", "benchmark_llm.log")

# # 📊 Datos por modelo
# datos = defaultdict(lambda: {
#     "consultas": [],
#     "tiempos_llm": [],
#     "tokens_salida": [],
#     "tokens_por_seg": [],
#     "costes": []
# })

# # 🧾 Parsear archivo línea por línea
# with open(log_path, "r", encoding="utf-8") as file:
#     modelo_actual = None
#     consulta_actual = None

#     for linea in file:
#         if "=== Benchmark modelo:" in linea:
#             modelo_actual = linea.strip().split(":")[-1].strip()
#         elif "Consulta:" in linea:
#             consulta_actual = linea.strip().split(":")[-1].strip()
#             datos[modelo_actual]["consultas"].append(consulta_actual)
#         elif "Tokens salida:" in linea:
#             match = re.search(r"salida:\s*(\d+)", linea)
#             if match:
#                 datos[modelo_actual]["tokens_salida"].append(int(match.group(1)))
#         elif "Tokens/seg:" in linea:
#             match = re.search(r"Tokens/seg:\s*([\d.]+)", linea)
#             if match:
#                 datos[modelo_actual]["tokens_por_seg"].append(float(match.group(1)))
#         elif "Tiempos -> LLM:" in linea:
#             match = re.search(r"LLM:\s*([\d.]+)s", linea)
#             if match:
#                 datos[modelo_actual]["tiempos_llm"].append(float(match.group(1)))
#         elif "Coste estimado:" in linea:
#             match = re.search(r"\$(\d+\.\d+)", linea)
#             if match:
#                 datos[modelo_actual]["costes"].append(float(match.group(1)))

# # ✅ Generar gráficas

# def plot_boxplot_tiempos():
#     modelos = list(datos.keys())
#     valores = [datos[m]["tiempos_llm"] for m in modelos]

#     plt.figure(figsize=(10, 6))
#     plt.boxplot(valores, labels=modelos, patch_artist=True)
#     plt.ylabel("Tiempo LLM (s)")
#     plt.title("⏱️ Distribución del tiempo de respuesta por modelo")
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()

# def plot_tokens_por_seg():
#     modelos = list(datos.keys())
#     medias = [np.mean(datos[m]["tokens_por_seg"]) for m in modelos]

#     plt.figure(figsize=(10, 6))
#     plt.bar(modelos, medias, color='skyblue')
#     plt.ylabel("Tokens/s")
#     plt.title("🚀 Velocidad media (tokens por segundo)")
#     plt.grid(True, axis='y')
#     plt.tight_layout()
#     plt.show()

# def plot_coste_total():
#     modelos = list(datos.keys())
#     total_coste = [sum(datos[m]["costes"]) for m in modelos]

#     plt.figure(figsize=(10, 6))
#     plt.bar(modelos, total_coste, color='salmon')
#     plt.ylabel("Coste total ($)")
#     plt.title("💰 Coste total estimado por modelo")
#     plt.grid(True, axis='y')
#     plt.tight_layout()
#     plt.show()

# def plot_tokens_salida():
#     modelos = list(datos.keys())
#     medias = [np.mean(datos[m]["tokens_salida"]) for m in modelos]

#     plt.figure(figsize=(10, 6))
#     plt.bar(modelos, medias, color='lightgreen')
#     plt.ylabel("Tokens de salida promedio")
#     plt.title("📤 Media de tokens generados por modelo")
#     plt.grid(True, axis='y')
#     plt.tight_layout()
#     plt.show()

# # 📊 Ejecutar todas
# if __name__ == "__main__":
#     plot_boxplot_tiempos()
#     plot_tokens_por_seg()
#     plot_coste_total()
#     plot_tokens_salida()







# 📈 Visualización de resultados del benchmark de LLMs en un Pdf para mayor Órden.

import os
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from matplotlib.backends.backend_pdf import PdfPages

# 📁 Ruta al log
log_path = os.path.join("logs", "benchmark_llm.log")

# 📁 Crear carpeta para gráficas
plots_dir = os.path.join("tests", "plots")
os.makedirs(plots_dir, exist_ok=True)
pdf_path = os.path.join(plots_dir, "graficas_llm.pdf")

# 📊 Datos por modelo
datos = defaultdict(lambda: {
    "consultas": [],
    "tiempos_llm": [],
    "tokens_salida": [],
    "tokens_por_seg": [],
    "costes": []
})

# 🧾 Parsear archivo línea por línea
with open(log_path, "r", encoding="utf-8") as file:
    modelo_actual = None
    consulta_actual = None

    for linea in file:
        if "=== Benchmark modelo:" in linea:
            modelo_actual = linea.strip().split(":")[-1].strip()
        elif "Consulta:" in linea:
            consulta_actual = linea.strip().split(":")[-1].strip()
            datos[modelo_actual]["consultas"].append(consulta_actual)
        elif "Tokens salida:" in linea:
            match = re.search(r"salida:\s*(\d+)", linea)
            if match:
                datos[modelo_actual]["tokens_salida"].append(int(match.group(1)))
        elif "Tokens/seg:" in linea:
            match = re.search(r"Tokens/seg:\s*([\d.]+)", linea)
            if match:
                datos[modelo_actual]["tokens_por_seg"].append(float(match.group(1)))
        elif "Tiempos -> LLM:" in linea:
            match = re.search(r"LLM:\s*([\d.]+)s", linea)
            if match:
                datos[modelo_actual]["tiempos_llm"].append(float(match.group(1)))
        elif "Coste estimado:" in linea:
            match = re.search(r"\$(\d+\.\d+)", linea)
            if match:
                datos[modelo_actual]["costes"].append(float(match.group(1)))

# ✅ Generar gráficas
def plot_boxplot_tiempos():
    modelos = list(datos.keys())
    valores = [datos[m]["tiempos_llm"] for m in modelos]

    plt.figure(figsize=(10, 6))
    plt.boxplot(valores, labels=modelos, patch_artist=True)
    plt.ylabel("Tiempo LLM (s)")
    plt.title("⏱️ Distribución del tiempo de respuesta por modelo")
    plt.grid(True)
    plt.tight_layout()
    return plt.gcf()

def plot_tokens_por_seg():
    modelos = list(datos.keys())
    medias = [np.mean(datos[m]["tokens_por_seg"]) for m in modelos]

    plt.figure(figsize=(10, 6))
    plt.bar(modelos, medias, color='skyblue')
    plt.ylabel("Tokens/s")
    plt.title("🚀 Velocidad media (tokens por segundo)")
    plt.grid(True, axis='y')
    plt.tight_layout()
    return plt.gcf()

def plot_coste_total():
    modelos = list(datos.keys())
    total_coste = [sum(datos[m]["costes"]) for m in modelos]

    plt.figure(figsize=(10, 6))
    plt.bar(modelos, total_coste, color='salmon')
    plt.ylabel("Coste total ($)")
    plt.title("💰 Coste total estimado por modelo")
    plt.grid(True, axis='y')
    plt.tight_layout()
    return plt.gcf()

def plot_tokens_salida():
    modelos = list(datos.keys())
    medias = [np.mean(datos[m]["tokens_salida"]) for m in modelos]

    plt.figure(figsize=(10, 6))
    plt.bar(modelos, medias, color='lightgreen')
    plt.ylabel("Tokens de salida promedio")
    plt.title("📤 Media de tokens generados por modelo")
    plt.grid(True, axis='y')
    plt.tight_layout()
    return plt.gcf()

# 🧾 Guardar todas las gráficas en un único PDF
if __name__ == "__main__":
    with PdfPages(pdf_path) as pdf:
        pdf.savefig(plot_boxplot_tiempos())
        pdf.savefig(plot_tokens_por_seg())
        pdf.savefig(plot_coste_total())
        pdf.savefig(plot_tokens_salida())

    print(f"✅ Gráficas guardadas en {pdf_path}")

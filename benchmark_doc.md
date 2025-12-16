**📘 Documentación detallada - Sistema de Benchmarking de Modelos (LLM y Embeddings)**

---

### 🔍 Objetivo General del Benchmark

El objetivo principal ha sido implementar un sistema de **benchmarking automático** que permita evaluar y comparar:

* ✅ **Modelos LLM** usados para tareas de generación de texto en la API.
* ✅ **Modelos de embeddings** usados para tareas de recuperación semántica (RAG).

Este sistema permite tomar decisiones informadas sobre qué modelo utilizar según diferentes métricas de rendimiento, coste, precisión y consumo de recursos.

---

### 📂 Estructura y Ubicación de Archivos

```
API-Reto-1/
├── logs/
│   ├── benchmark_llm.log             # Log de resultados del benchmark de modelos LLM
│   └── benchmark_embeddings.log      # Log de resultados del benchmark de modelos de embeddings
│
├── tests/
│   ├── test_benchmark_llm.py         # Script para benchmark de modelos LLM (tiempos, tokens, coste)
│   ├── test_benchmark_embeddings.py  # Script para benchmark de embeddings (tiempos, RAM, similitud)
│   ├── graficar_resultados_embeddings.py  # Script para generar gráficas desde el log de embeddings
│   └── plots/
│       └── benchmark_embeddings.pdf  # Documento generado con gráficas visuales comparativas
```

---

### 📅 Proceso realizado paso a paso

#### 1. **Benchmark de LLMs** (`test_benchmark_llm.py`)

Se evaluaron modelos como `gemini`, `mistral`, `openrouter`, etc. Se registran:

* Tiempo de respuesta
* Tokens generados
* Coste estimado por petición
* Tokens por segundo (rendimiento)

**Resultado**: Un log detallado con todas las pruebas guardado en `benchmark_llm.log`

#### 2. **Benchmark de modelos de embeddings** (`test_benchmark_embeddings.py`)

Modelos evaluados:

* `sentence-transformers/all-MiniLM-L6-v2`
* `intfloat/multilingual-e5-base`
* `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
* `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`

**Métricas analizadas:**

* Tiempo de carga del modelo
* Tiempo de inferencia
* Uso de RAM
* Tamaño en disco
* Precisión semántica (cosine similarity)

**Resultado:** Log `benchmark_embeddings.log` con toda la información estructurada.

#### 3. **Generación de gráficas** (`graficar_resultados_embeddings.py`)

Se genera un PDF con las siguientes gráficas:

| Tipo de Gráfico             | Métrica Representada                         |
| --------------------------- | -------------------------------------------- |
| Barras horizontales         | Tiempo de carga                              |
| Barras horizontales         | Tiempo de inferencia                         |
| Barras horizontales         | RAM utilizada                                |
| Barras horizontales         | Tamaño en disco                              |
| Barras horizontales         | Precisión semántica (cosine)                 |
| **Mapa de calor (heatmap)** | Comparativa global normalizada entre modelos |

---

### 📊 Explicación del Heatmap Final (Sustituto del Radar Chart)

El último gráfico generado es un **heatmap** que resume todas las métricas en una sola visualización:

* Cada celda muestra el **rendimiento relativo normalizado** de un modelo en una métrica.
* Valores altos (cercanos a 1) implican **mejor rendimiento**.
* Colores oscuros → mejor resultado. Colores claros → peor.

✉️ Este reemplaza el radar chart, que resultaba poco legible o vacío si había datos faltantes.

---

### 📦 Ejecución paso a paso del sistema de benchmarking
Esta sección describe el orden de ejecución recomendado para evaluar y comparar los modelos LLM y de embeddings implementados en este proyecto. Asegúrate de haber instalado todas las dependencias necesarias (ver requirements.txt) antes de comenzar.

🔹 Paso 1: Activar el entorno virtual
```
cd API-Reto-1
source venv/bin/activate
```

🔹 Paso 2: Benchmark de modelos LLM

    ✅ Script: tests/test_benchmark_llm.py

Este script realiza pruebas de rendimiento sobre diferentes modelos LLM conectados vía OpenRouter o proveedores externos. Evalúa:

* Tiempo de respuesta.

* Tokens usados (prompt, completion y total).

* Tokens por segundo.

* Coste estimado por consulta.

* Calidad básica de respuesta (si se configura).


📦 Resultado:

Se genera el fichero de logs logs/benchmark_llm.log.

▶️ Ejecución:

```
python tests/test_benchmark_llm.py
```

🔹 Paso 3: Generación de gráficas del benchmark LLM

    ✅ Script: tests/graficar_resultados_llm.py

Este script procesa el log generado anteriormente (benchmark_llm.log) y crea un fichero PDF con varias visualizaciones:

* Tiempo de respuesta por modelo.

* Tokens usados (prompt/completion/total).

* Coste por cada consulta.

* Velocidad de respuesta (tokens/segundo).

* Calidad básica si está configurada.

📄 Resultado:

* Fichero PDF generado en tests/plots/benchmark_llm.pdf.

▶️ Ejecución:
```
python tests/graficar_resultados_llm.py
```


🔹 Paso 4: Benchmark de modelos de embeddings

    ✅ Script: tests/test_benchmark_embeddings.py

Evalúa varios modelos de embeddings locales (e.g., de sentence-transformers o intfloat). Calcula:

* Tiempo de carga.

* Tiempo de inferencia.

* Uso de RAM.

* Tamaño en disco.

* Precisión semántica basada en similitud coseno entre frases.

📦 Resultado:

* Se genera el fichero de logs logs/benchmark_embeddings.log.


▶️ Ejecución:
```
python tests/test_benchmark_embeddings.py
```


🔹 Paso 5: Generación de gráficas del benchmark de embeddings

    ✅ Script: tests/graficar_resultados_embeddings.py

Este script lee el log benchmark_embeddings.log y genera un PDF con los siguientes gráficos:

* Tiempo de carga.

* Tiempo de inferencia.

* Memoria RAM utilizada.

* Tamaño en disco.

* Precisión semántica.

* Comparativa global mediante heatmap normalizado (sustitución del gráfico radar por uno más legible y claro).

📄 Resultado:

Fichero PDF generado en tests/plots/benchmark_embeddings.pdf.


▶️ Ejecución:

```
python tests/graficar_resultados_embeddings.py
```

📌 Observaciones importantes

Si al ejecutar algún script falta una librería, instálala con pip install y añade el paquete al requirements.txt.

Todos los logs quedan en logs/, y todas las gráficas se guardan como PDF en tests/plots/.

Se recomienda mantener limpios los logs antes de una nueva ejecución para evitar mezclar resultados.

Con estos pasos, cualquier usuario podrá reproducir de forma controlada y completa el sistema de benchmarking del proyecto y visualizar los resultados sin complicaciones.


### 🚀 Conclusión

El sistema de benchmark ha sido **automatizado, visualizado y documentado** con:

* Ejecuciones reproducibles
* Logs estructurados
* Visualizaciones comparativas claras
* Documentación integrada y exportable

Con esto se garantiza la capacidad de auditar, escalar o sustituir modelos en base a datos objetivos y comparables.

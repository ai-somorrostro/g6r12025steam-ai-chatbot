# Justificación detallada de las mejoras implementadas: Benchmarking de modelos LLM y Embeddings

## Introducción

Como parte de las mejoras solicitadas en el reto del módulo PIA, se nos propuso implementar un sistema de **benchmarking** para evaluar y comparar distintos modelos LLM (Large Language Models) y modelos de embeddings. El objetivo principal era **tomar decisiones fundamentadas** sobre los modelos a utilizar en la API del proyecto, atendiendo a criterios como rendimiento, coste, velocidad y precisión.

A continuación se justifica detalladamente **qué se ha hecho**, **por qué se ha hecho**, y **cómo se ha implementado** cada una de las dos partes del benchmark: **LLMs** y **Embeddings**, apoyándose en los archivos desarrollados.

---

## Benchmarking de Modelos LLM (Large Language Models)

### 🔍 Qué se pedía:

* Evaluar distintos modelos LLM.
* Compararlos en términos de:

  * Tiempo de respuesta (latencia media, p95, p99)
  * Velocidad de generación (tokens/s)
  * Tokens usados (entrada/salida)
  * Coste estimado por solicitud (tokens * precio modelo)
  * Calidad de respuesta (opcional, se registra la respuesta)

### 📄 Archivos desarrollados:

#### 1. `tests/test_benchmark_llm.py`

* Ejecuta las consultas definidas contra cada modelo.
* Usa `LLMManager` para simular peticiones reales.
* Recupera contexto vía Elasticsearch (como se haría en la API real).
* Mide tiempos, tokens generados, coste y velocidad.
* Guarda todo en el fichero de log: `logs/benchmark_llm.log`.

#### 2. `tests/graficar_resultados_llm.py`

* Lee el log generado y extrae los datos por modelo.
* Genera un PDF (`graficas_llm.pdf`) con 4 gráficos:

  1. Boxplot de latencia por modelo.
  2. Tokens por segundo (velocidad).
  3. Coste total estimado.
  4. Tokens generados promedio.

### 🧵 Modelos evaluados:

* `google/gemini-2.0-flash-lite-001`
* `mistralai/mixtral-8x7b`
* `meta-llama/llama-3-8b`

### ✅ Justificación:

* **Modelos seleccionados**: los 3 modelos evaluados se eligieron por ser los más accesibles desde la API externa utilizada (`OpenRouter`) y representar distintas gamas (ligero, medio, potente).
* **Modelo usado finalmente en la API**: `google/gemini-2.0-flash-lite-001`.

  * Justificación: fue el modelo con mejor relación coste-velocidad-calidad para el tipo de consultas que hacemos (preguntas sobre videojuegos con contexto semántico).

### 📊 Resultados de las gráficas:

* `Gemini` tiene el menor tiempo de respuesta promedio.
* `LLaMA 3` genera más tokens por segundo que `Mixtral`.
* `Mixtral` presenta mayor coste total acumulado.

---

## Benchmarking de Modelos de Embeddings

### 🔍 Qué se pedía:

* Comparar distintos modelos de embeddings considerando:

  * Tiempo de carga
  * Tiempo de inferencia sobre 100 textos
  * Uso de RAM
  * Tamaño en disco del modelo
  * Precisión semántica (similitud cosine)

### 📄 Archivos desarrollados:

#### 1. `tests/test_benchmark_embeddings.py`

* Evalúa 4 modelos de embeddings descargables de Hugging Face.
* Mide:

  * Tiempo de carga del modelo.
  * Tiempo de inferencia sobre un batch de 100 textos.
  * RAM usada en inferencia.
  * Precisión media comparando pares de textos similares con `cosine_similarity`.
  * Tamaño del modelo en disco.
* Guarda todo en `logs/benchmark_embeddings.log`.

#### 2. `tests/graficar_resultados_embeddings.py`

* Lee el log anterior.
* Genera el PDF `benchmark_embeddings.pdf` con 6 gráficos:

  1. Barras de tiempo de carga.
  2. Barras de inferencia.
  3. Barras de RAM usada.
  4. Barras de tamaño.
  5. Barras de precisión.
  6. Heatmap comparativo global normalizado.

### 🧵 Modelos evaluados:

* `sentence-transformers/all-MiniLM-L6-v2`
* `intfloat/multilingual-e5-base`
* `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
* `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` ✅ (modelo usado en la API)

### ✅ Justificación:

* Se evaluaron modelos multilingües y ligeros con alto rendimiento en tareas semánticas.
* El modelo elegido para la API es `paraphrase-multilingual-mpnet-base-v2` porque:

  * Ofrece **alta precisión semántica** (cosine similarity > 0.7).
  * Aceptable tiempo de inferencia y carga.
  * Buen equilibrio entre **calidad y rendimiento**.

### 📊 Resultados de las gráficas:

* `MiniLM-L6` es el más rápido y ligero.
* `MPNET` (el que usamos) no es el más rápido, pero **es el más equilibrado**.
* `E5-base` destaca en precisión pero tarda más en inferencia.
* Heatmap permite comparar todos los factores en una sola visualización.

---

## Estructura del repositorio relevante

```
API-Reto-1/
├── logs/
│   ├── benchmark_llm.log
│   ├── benchmark_embeddings.log
├── tests/
│   ├── test_benchmark_llm.py
│   ├── graficar_resultados_llm.py
│   ├── test_benchmark_embeddings.py
│   ├── graficar_resultados_embeddings.py
│   └── plots/
│       ├── benchmark_embeddings.pdf
│       ├── graficas_llm.pdf
├── benchmark_doc.md ✅ Documento principal
```

---

## Librerías adicionales usadas

* `matplotlib` → gráficos de barras, boxplot y PDFs.
* `seaborn` → heatmap comparativo.
* `psutil` → medir uso de RAM.
* `sentence-transformers`, `sklearn` → embeddings y similitud cosine.
* `numpy` → estadísticas (medias, percentiles).

---

## Cómo se ejecuta cada parte y en qué orden

### Paso 1: Ejecutar benchmark LLM

```bash
python tests/test_benchmark_llm.py
```

* Genera `logs/benchmark_llm.log`

### Paso 2: Generar PDF de resultados del LLM

```bash
python tests/graficar_resultados_llm.py
```

* Genera `tests/plots/graficas_llm.pdf`

### Paso 3: Ejecutar benchmark de embeddings

```bash
python tests/test_benchmark_embeddings.py
```

* Genera `logs/benchmark_embeddings.log`

### Paso 4: Generar PDF de resultados de embeddings

```bash
python tests/graficar_resultados_embeddings.py
```

* Genera `tests/plots/benchmark_embeddings.pdf`

---

## Consideraciones finales

* Se han cumplido todos los objetivos planteados de evaluación de modelos.
* Se han seleccionado **modelos reales utilizados en la API** (no se ha hecho de forma aislada).
* Se han generado **logs trazables y visualizaciones exportables** para la presentación.
* La documentación final está centralizada en el archivo `benchmark_doc.md`.

---

## Posibles mejoras futuras

* Evaluación automática de la calidad de respuestas LLM ("LLM-as-a-judge").
* Benchmark de consumo real en GPUs.
* Comparación con embeddings propios entrenados.

---

## Conclusión

Este trabajo de benchmarking ha permitido tomar decisiones técnicas justificadas sobre qué modelos usar en producción, optimizando el equilibrio entre **calidad, coste y eficiencia**. Se han documentado, visualizado y versionado todos los pasos.

# Imagen base oficial
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer puerto por defecto de FastAPI
EXPOSE 8000

# Comando por defecto: levantar servidor Uvicorn
CMD ["uvicorn", "api_llm.main:app", "--host", "0.0.0.0", "--port", "8000"]

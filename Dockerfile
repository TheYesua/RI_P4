# Dockerfile para el sistema WikiSearch
# Construye el backend y permite indexar/servir

FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar recursos NLTK
RUN python -c "import nltk; nltk.download('stopwords', quiet=True)"

# Copiar código del backend
COPY backend/ ./backend/

WORKDIR /app/backend

# Puerto para la API
EXPOSE 8000

# Comando por defecto: ejecutar el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

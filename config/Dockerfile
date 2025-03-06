# Usar una imagen ligera con Python
FROM python:3.10-slim

# Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de dependencias
COPY config/requirements.txt /app/requirements.txt

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y datos
COPY src/ /app/src/
COPY data/ /app/data/

# Establecer el script de scraping como punto de entrada
CMD ["python", "/app/src/QuoteScraper.py"]


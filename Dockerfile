# Usa una imagen base de Python
FROM python:3.12-slim

# Variables de entorno para mejorar el rendimiento de Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias para Django y PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python directamente
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir tensorflow gunicorn pillow matplotlib django opencv-python

# Copia todos los archivos del proyecto al contenedor
COPY . /app/

# Expone el puerto de la aplicación
EXPOSE 8000

# Comando por defecto para ejecutar la aplicación
CMD ["gunicorn", "DRD.wsgi:application", "--bind", "0.0.0.0:8000"]
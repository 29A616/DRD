# Usa Python 3.12-slim como base
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para OpenCV y Python
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos del proyecto al contenedor
COPY . /app

# Crear un entorno virtual en /app/.venv
RUN python -m venv /app/.venv

# Actualiza herramientas esenciales de Python en el entorno virtual
RUN /app/.venv/bin/pip install --upgrade pip setuptools wheel

# Instala dependencias de Python en el entorno virtual
RUN /app/.venv/bin/pip install tensorflow gunicorn django opencv-python-headless matplotlib pillow

# Comando para verificar la estructura del entorno virtual
RUN echo "Verificando /app/.venv:" && ls -la /app/.venv && \
    echo "Verificando /app/.venv/bin:" && ls -la /app/.venv/bin

# Expone el puerto en el contenedor
EXPOSE 8000

# Comando de inicio del contenedor
CMD ["/app/.venv/bin/python", "-m", "gunicorn", "DRD.wsgi:application", "--bind", "0.0.0.0:8000"]

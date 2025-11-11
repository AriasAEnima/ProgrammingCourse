FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instalar dependencias del sistema (para MongoDB y debugging)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . /app/

# Variables de entorno por defecto para MongoDB
# IMPORTANTE: Sobrescribir según tu caso:
#   - MongoDB en tu PC: host.docker.internal (default)
#   - MongoDB en Docker: nombre del contenedor (ej: mongodb)
#   - MongoDB Atlas: usar MONGODB_URI en su lugar
ENV MONGODB_HOST=host.docker.internal \
    MONGODB_PORT=27017 \
    MONGODB_DB=desk_database \
    MONGODB_USERNAME= \
    MONGODB_PASSWORD=

# Puerto que expone la aplicación
EXPOSE 8000

# Script de inicio
CMD ["python", "desk_app/manage.py", "runserver", "0.0.0.0:8000"] 
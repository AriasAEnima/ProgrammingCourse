FROM python:3.15-rc-slim

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar toda la aplicación Django
COPY furniture_app /app/

# Exponer puerto
EXPOSE 8000

# Variables de entorno
ENV PYTHONPATH=/app
ENV MONGO_HOST=mongo

# Comando para ejecutar el servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

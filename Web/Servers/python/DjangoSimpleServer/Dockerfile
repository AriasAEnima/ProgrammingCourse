FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Configurar variables de entorno para MongoDB
ENV MONGODB_HOST=host.docker.internal
ENV MONGODB_PORT=27017
ENV MONGODB_DB=desk_database
ENV MONGODB_USERNAME=
ENV MONGODB_PASSWORD=

EXPOSE 8000

CMD ["python", "desk_app/manage.py", "runserver", "0.0.0.0:8000"] 
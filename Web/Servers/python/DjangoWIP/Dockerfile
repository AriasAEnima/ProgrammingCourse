FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

ENV PYTHONPATH=/app
ENV MONGO_HOST='host.docker.internal'

CMD ["python", "furniture_app/manage.py", "runserver", "0.0.0.0:8000"]
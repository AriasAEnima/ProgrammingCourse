FROM python:3.15-rc-slim

WORKDIR /app

COPY . /app/

EXPOSE 8000

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python","manage.py","runserver","0.0.0.0:8000"]
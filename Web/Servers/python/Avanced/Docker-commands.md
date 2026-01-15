# Docker commands

## Image (crear imagen apartir de un DockerFile)

* Listar imagenes:
    * docker images
* Crear imagen: -f (file) -t (tag) 
    * docker build -f .\Dockerfile.mongodb -t mongo-docker:latest .
    
    (ojo con el . final)
## Run (Crear contenedor e iniciarlo )
-d detached

-p puerto (host:contenedor)

* docker run -d -p 8001:8000 --name my_django_docker_app_local_db  my_first_django_docker_app:latest 

## Crear network (para conectividad entre servidores en docker)

* docker network create furniture-network

-e variable de entorno


* docker run -d -p 8000:8000 -e MONGO_HOST='mongo-docker' -e MONGO_DB='furniture_catalog_db_docker' --name my_django_docker_app --network furniture-network my_first_django_docker_app:latest


## Detener e inicializar

* docker stop ...
* docker start ..

# Docker Compose

* docker-compose up --build

## Ejecutar comandos sobre contenerdor (debe ser sobre la carpeta del archivo docker-compose)

* docker-compose exec django-api python manage.py init_users
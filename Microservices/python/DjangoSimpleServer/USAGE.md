# 🚀 Uso: Django + MongoDB con Docker

## 📦 Archivos Dockerfile

- **`Dockerfile`** - Para la aplicación Django
- **`Dockerfile.mongodb`** - Para MongoDB

## 🔨 Construir las Imágenes

```bash
# Construir imagen de Django
docker build -t desk-api -f Dockerfile .

# Construir imagen de MongoDB
docker build -t desk-mongodb -f Dockerfile.mongodb .
```

## 🌐 Opción 1: Usar Red Docker (Recomendado)

### Paso 1: Crear red
```bash
docker network create desk-network
```

### Paso 2: Iniciar MongoDB
```bash
docker run -d \
  --name mongodb \
  --network desk-network \
  -p 27017:27017 \
  desk-mongodb
```

### Paso 3: Iniciar Django
```bash
docker run -d \
  --name desk-api \
  --network desk-network \
  -p 8000:8000 \
  -e MONGODB_HOST=mongodb \
  desk-api
```

### Acceder
- API: http://localhost:8000/api/desk/
- MongoDB: localhost:27017

---

## 🖥️ Opción 2: MongoDB Local en tu PC

### Paso 1: Asegúrate que MongoDB esté corriendo en tu PC

### Paso 2: Iniciar solo Django
```bash
docker run -d \
  --name desk-api \
  -p 8000:8000 \
  -e MONGODB_HOST=host.docker.internal \
  desk-api
```

---

## 🛑 Detener y Limpiar

```bash
# Detener contenedores
docker stop desk-api mongodb

# Eliminar contenedores
docker rm desk-api mongodb

# Eliminar red
docker network rm desk-network

# Opcional: Eliminar imágenes
docker rmi desk-api desk-mongodb
```

---

## 📝 Comandos Útiles

### Ver logs
```bash
docker logs desk-api
docker logs mongodb
```

### Poblar base de datos
```bash
docker exec desk-api python desk_app/seed_db.py
```

### Shell de MongoDB
```bash
docker exec -it mongodb mongosh
```

En mongosh:
```javascript
use desk_database
db.desks.find()
```

### Shell de Django
```bash
docker exec -it desk-api python desk_app/manage.py shell
```

---

## 🐛 Troubleshooting

### Ver si MongoDB está corriendo
```bash
docker ps | grep mongodb
```

### Ver si están en la misma red
```bash
docker network inspect desk-network
```

### Probar conexión desde Django a MongoDB
```bash
docker exec -it desk-api bash
apt-get update && apt-get install -y curl
curl mongodb:27017
```

Debería responder: "It looks like you are trying to access MongoDB over HTTP..."

---

## 🎯 Resumen Rápido

```bash
# Construir
docker build -t desk-api .
docker build -t desk-mongodb -f Dockerfile.mongodb .

# Red
docker network create desk-network

# Iniciar
docker run -d --name mongodb --network desk-network -p 27017:27017 desk-mongodb
docker run -d --name desk-api --network desk-network -p 8000:8000 -e MONGODB_HOST=mongodb desk-api

# Usar
curl http://localhost:8000/api/desk/

# Limpiar
docker stop desk-api mongodb
docker rm desk-api mongodb
docker network rm desk-network
```


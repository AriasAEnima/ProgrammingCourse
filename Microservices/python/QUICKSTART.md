# ⚡ Inicio Rápido - Sistema de Notificaciones de Mesas

## 🐳 Opción 1: Docker Compose (Recomendado)

### Un solo comando para levantar todo el sistema

```bash
cd Microservices/python
docker-compose up --build
```

Esto levantará automáticamente:
- 🐘 MongoDB (puerto 27017)
- 📡 WebSocket Server (puerto 8765)
- 🐍 Django API (puerto 8000)
- 👂 Consumer (logs en consola)

### 🧪 Probar el sistema

En otra terminal:

```bash
# Crear mesa
curl -X POST http://localhost:8000/api/v1/desk/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Mesa Test", "width": 100, "height": 200}'

# Ver todas las mesas
curl http://localhost:8000/api/v1/desk/
```

Deberías ver notificaciones en tiempo real en los logs del consumer! 🎉

### 🛑 Detener el sistema

```bash
# Detener servicios (mantiene datos)
docker-compose down

# Detener y limpiar TODO (elimina volúmenes)
docker-compose down -v
```

### 📊 Ver logs específicos

```bash
# Ver logs del consumer
docker-compose logs -f consumer

# Ver logs de Django API
docker-compose logs -f django-api

# Ver logs del WebSocket Server
docker-compose logs -f websocket-server

# Ver logs de MongoDB
docker-compose logs -f mongo
```

---

## 💻 Opción 2: Ejecución Manual (sin Docker)

### Terminal 1: MongoDB
```bash
# Asegúrate de tener MongoDB instalado y ejecutándose
mongod
```

### Terminal 2: WebSocket Server
```bash
cd websocket_server
pip install -r requirements.txt
python websocket_server.py
```

### Terminal 3: Django API
```bash
cd DjangoSimpleServer
pip install -r requirements.txt

# Crear archivo .env en desk_app/
echo "MONGODB_HOST=localhost" > desk_app/.env
echo "MONGODB_PORT=27017" >> desk_app/.env
echo "MONGODB_DB=desk_database" >> desk_app/.env

python desk_app/manage.py runserver
```

### Terminal 4: Consumer (Ver notificaciones)
```bash
cd websocket_consumer
pip install -r requirements.txt
python websocket_consumer.py
```

### 🧪 Probar

En otra terminal:

```bash
# Crear mesa
curl -X POST http://localhost:8000/api/v1/desk/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Mesa Test", "width": 100, "height": 200}'

# Ver todas las mesas
curl http://localhost:8000/api/v1/desk/
```

---

## 📋 Requisitos

### Con Docker (Opción 1):
- Docker Desktop instalado
- Docker Compose instalado

### Sin Docker (Opción 2):
- Python 3.8+
- MongoDB ejecutándose localmente
- 4 terminales abiertas

---

## 🔧 Troubleshooting

### Puerto ocupado
Si ves errores de puerto ocupado:

```bash
# Ver qué usa los puertos
lsof -i :8000  # Django
lsof -i :8765  # WebSocket
lsof -i :27017 # MongoDB

# En Windows usar:
netstat -ano | findstr :8000
```

### Problemas con MongoDB en Docker
```bash
# Ver logs de MongoDB
docker-compose logs mongo

# Reiniciar solo MongoDB
docker-compose restart mongo
```

### Consumer no muestra notificaciones
```bash
# Verificar que el WebSocket server esté corriendo
curl -i http://localhost:8765

# Ver logs del WebSocket server
docker-compose logs -f websocket-server
```

---

¿Problemas? Lee `README_WEBSOCKET_SYSTEM.md` para más detalles.


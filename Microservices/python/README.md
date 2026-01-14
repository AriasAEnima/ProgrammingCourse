# 🐳 Sistema de Microservicios - Notificaciones de Muebles

Sistema de microservicios con Django, WebSocket, MongoDB y Consumer en tiempo real para gestión de catálogo de muebles.

## 🚀 Iniciar Sistema

```bash
# 1. Construir imágenes e iniciar servicios
docker-compose up --build

# O en segundo plano:
docker-compose up --build -d
```

## 🧪 Probar Sistema

```bash
# Crear mueble
curl -X POST http://localhost:8000/api/furniture/create/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Mesa de Roble", "descripcion": "Mesa elegante de comedor", "altura": 75, "ancho": 120, "material": "roble", "autor_username": "Juan"}'

# Listar muebles
curl http://localhost:8000/api/furniture/

# Obtener un mueble específico
curl http://localhost:8000/api/furniture/FURNITURE_ID/

# Actualizar mueble
curl -X PUT http://localhost:8000/api/furniture/FURNITURE_ID/update/ \
  -H "Content-Type: application/json" \
  -d '{"altura": 80, "material": "pino"}'

# Eliminar mueble
curl -X DELETE http://localhost:8000/api/furniture/FURNITURE_ID/
```

**Resultado esperado:** Verás las notificaciones en tiempo real en los logs del consumer 🎉

## 📊 Ver Logs

```bash
# Logs en tiempo real
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f consumer
docker-compose logs -f django-api
docker-compose logs -f websocket-server
docker-compose logs -f mongo

docker-compose exec django-api python manage.py init_users

```

## 🛑 Detener Sistema

```bash
# Detener servicios (mantiene datos)
docker-compose down

# Detener y eliminar todo (incluye volúmenes)
docker-compose down -v
```

## 📦 Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **Django API** | 8000 | REST API para CRUD de muebles |
| **WebSocket Server** | 8765 | Distribuye notificaciones en tiempo real |
| **Consumer** | - | Cliente que muestra notificaciones |
| **MongoDB** | 27017 | Base de datos de muebles |

## 🔧 Comandos Útiles

```bash
# Ver estado de contenedores
docker-compose ps

# Reiniciar un servicio
docker-compose restart websocket-server

# Reconstruir una imagen específica
docker-compose build django-api

# Ver uso de recursos
docker stats

# Acceder a un contenedor
docker-compose exec django-api bash
docker-compose exec mongo mongosh
```

## 📖 Documentación Completa

- **[QUICKSTART.md](./QUICKSTART.md)** - Guía de inicio rápido con opciones manuales
- **[README_WEBSOCKET_SYSTEM.md](./README_WEBSOCKET_SYSTEM.md)** - Documentación completa del sistema

---

**Arquitectura:** Django API → WebSocket Server → Consumer + MongoDB


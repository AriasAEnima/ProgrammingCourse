# 🐳 Sistema de Microservicios - Notificaciones de Mesas

Sistema de microservicios con Django, WebSocket, MongoDB y Consumer en tiempo real.

## 🚀 Iniciar Sistema

```bash
# 1. Construir imágenes e iniciar servicios
docker-compose up --build

# O en segundo plano:
docker-compose up --build -d
```

## 🧪 Probar Sistema

```bash
# Crear mesa
curl -X POST http://localhost:8000/api/v1/desk/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Mesa Test", "width": 100, "height": 200}'

# Listar mesas
curl http://localhost:8000/api/v1/desk/
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
| **Django API** | 8000 | REST API para CRUD de mesas |
| **WebSocket Server** | 8765 | Distribuye notificaciones en tiempo real |
| **Consumer** | - | Cliente que muestra notificaciones |
| **MongoDB** | 27017 | Base de datos |

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


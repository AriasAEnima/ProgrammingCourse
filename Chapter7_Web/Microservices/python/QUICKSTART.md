# ⚡ Inicio Rápido - Sistema de Notificaciones de Mesas

## 🎯 Para empezar ahora mismo

### Terminal 1: WebSocket Server (Producer)
```bash
cd websocket_producer
pip install websockets
python websocket_server.py
```

### Terminal 2: Django API
```bash
cd DjangoSimpleServer
pip install -r requirements.txt

# Crear archivo .env en desk_app/
echo "MONGODB_HOST=localhost" > desk_app/.env
echo "MONGODB_PORT=27017" >> desk_app/.env
echo "MONGODB_DB=desk_database" >> desk_app/.env

python desk_app/manage.py runserver
```

### Terminal 3: Consumer (Ver notificaciones)
```bash
cd websocket_consumer
pip install websockets
python websocket_consumer.py
```

## 🧪 Probar

En otra terminal:

```bash
# Crear mesa
curl -X POST http://localhost:8000/api/desk/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Mesa Test", "width": 100, "height": 200}'

# Ver todas las mesas
curl http://localhost:8000/api/desk/
```

Deberías ver notificaciones en tiempo real en el Terminal 3! 🎉

## 📋 Requisitos

- Python 3.8+
- MongoDB ejecutándose localmente
- 3 terminales abiertas

¿Problemas? Lee `README_WEBSOCKET_SYSTEM.md` para más detalles.


# 📡 WebSocket Producer - Servidor de Notificaciones de Mesas

Servidor WebSocket que recibe y distribuye notificaciones en tiempo real sobre operaciones con mesas.

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

## ▶️ Ejecutar

```bash
python websocket_server.py
```

El servidor se iniciará en `ws://localhost:8765`

## 📨 Mensajes Soportados

### desk_created
```json
{
  "type": "desk_created",
  "desk": {
    "desk_id": "123",
    "name": "Mesa Ejecutiva",
    "width": 180,
    "height": 90
  }
}
```

### desk_updated
```json
{
  "type": "desk_updated",
  "desk": {
    "desk_id": "123",
    "name": "Mesa Ejecutiva XL",
    "width": 200,
    "height": 100
  }
}
```

### desk_deleted
```json
{
  "type": "desk_deleted",
  "desk": {
    "desk_id": "123",
    "name": "Mesa Ejecutiva"
  }
}
```

## 🧪 Probar con wscat

```bash
# Instalar wscat
npm install -g wscat

# Conectar
wscat -c ws://localhost:8765

# Enviar mensaje de prueba
{"type": "desk_created", "desk": {"name": "Mesa Test", "width": 100, "height": 200}}
```


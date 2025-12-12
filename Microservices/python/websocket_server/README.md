# 📡 WebSocket Server - Servidor de Notificaciones de Muebles

Servidor WebSocket que recibe y distribuye notificaciones en tiempo real sobre operaciones con muebles.

**Nota:** Este servidor actúa como **broker/intermediario**, no como producer. El verdadero "producer" de mensajes es Django.

## 🎯 Rol en el Sistema

```
Django (Producer)  →  WebSocket Server (Broker)  →  Consumers (Clientes)
    Genera mensajes      Distribuye mensajes          Reciben mensajes
```

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

### furniture_created
Notifica cuando se crea un nuevo mueble en el catálogo

```json
{
  "type": "furniture_created",
  "furniture": {
    "furniture_id": "673a2f1b8e4d2a1c3b5e6f7a",
    "nombre": "Mesa de Roble",
    "descripcion": "Mesa elegante de comedor",
    "altura": 75,
    "ancho": 120,
    "material": "roble",
    "autor_username": "Juan"
  }
}
```

### furniture_updated
Notifica cuando se actualiza un mueble existente

```json
{
  "type": "furniture_updated",
  "furniture": {
    "furniture_id": "673a2f1b8e4d2a1c3b5e6f7a",
    "nombre": "Mesa de Roble XL",
    "descripcion": "Mesa elegante de comedor - tamaño grande",
    "altura": 80,
    "ancho": 150,
    "material": "pino",
    "autor_username": "Juan"
  }
}
```

### furniture_deleted
Notifica cuando se elimina un mueble del catálogo

```json
{
  "type": "furniture_deleted",
  "furniture": {
    "furniture_id": "673a2f1b8e4d2a1c3b5e6f7a",
    "nombre": "Mesa de Roble XL",
    "descripcion": "Mesa elegante de comedor - tamaño grande",
    "altura": 80,
    "ancho": 150,
    "material": "pino",
    "autor_username": "Juan"
  }
}
```

### ping/pong
Para mantener la conexión viva

```json
{
  "type": "ping"
}
```

Respuesta:
```json
{
  "type": "pong",
  "timestamp": "2024-01-15T14:30:00.000Z"
}
```

## 🧪 Probar con wscat

```bash
# Instalar wscat
npm install -g wscat

# Conectar
wscat -c ws://localhost:8765

# Enviar mensaje de prueba - crear mueble
{"type": "furniture_created", "furniture": {"furniture_id": "test123", "nombre": "Silla Test", "descripcion": "Silla de prueba", "altura": 90, "ancho": 45, "material": "plastico", "autor_username": "TestUser"}}

# Enviar mensaje de prueba - actualizar mueble
{"type": "furniture_updated", "furniture": {"furniture_id": "test123", "nombre": "Silla Test Modificada", "descripcion": "Silla modificada", "altura": 95, "ancho": 50, "material": "madera", "autor_username": "TestUser"}}

# Enviar mensaje de prueba - eliminar mueble
{"type": "furniture_deleted", "furniture": {"furniture_id": "test123", "nombre": "Silla Test", "descripcion": "Silla de prueba", "altura": 90, "ancho": 45, "material": "plastico", "autor_username": "TestUser"}}
```

## 🏗️ Arquitectura

El servidor WebSocket mantiene una lista de clientes conectados y:

1. **Registra** nuevos clientes cuando se conectan
2. **Recibe** mensajes de Django (vía websocket_client.py)
3. **Distribuye** (broadcast) esos mensajes a todos los clientes conectados
4. **Desregistra** clientes cuando se desconectan

## 🔧 Configuración

- **Host:** `0.0.0.0` (acepta conexiones desde cualquier IP)
- **Puerto:** `8765`
- **Timeout:** Configurable por cliente

## 📊 Logs

El servidor genera logs informativos sobre:
- ✅ Conexiones nuevas
- ❌ Desconexiones
- 📥 Mensajes recibidos
- 📨 Mensajes enviados a clientes
- 🧹 Limpieza de conexiones muertas


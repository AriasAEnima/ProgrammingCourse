# 🚀 Flask API + WebSocket Integration

Sistema completo de API REST con notificaciones en tiempo real usando WebSockets.

## 🎯 Inicio Rápido

**¿Primera vez?** Solo necesitas:

1. `pip install -r requirements.txt`
2. `python start_websocket_system.py`

**¡Listo!** El sistema se inicia automáticamente y te mostrará todo funcionando.

## 📁 Archivos del Proyecto

```
Flask/
├── app.py                    # API REST Flask con integración WebSocket
├── websocket_server.py       # Servidor WebSocket para notificaciones
├── websocket_consumer.py     # Consumidor que escucha notificaciones
├── start_websocket_system.py # 🎯 Script automático para iniciar todo
├── clean_logs.py            # 🛠️ Script utilidad para limpiar/organizar logs
├── requirements.txt          # Dependencias actualizadas
├── .gitignore               # Ignora logs y archivos temporales
├── logs/                    # 📁 Directorio para todos los logs del sistema
│   ├── websocket_server.log
│   ├── flask_api.log
│   └── websocket_consumer.log
└── README_WEBSOCKET.md       # Esta documentación
```

## 🔧 Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Cómo Ejecutar (3 Terminales)

### **Terminal 1: Servidor WebSocket**
```bash
python websocket_server.py
```
**✅ Listo cuando veas:**
```
🚀 Iniciando servidor WebSocket...
📍 Servidor ejecutándose en ws://localhost:8765
server listening on [::1]:8765
server listening on 127.0.0.1:8765
```

### **Terminal 2: API Flask**
```bash
python app.py
```
**✅ Listo cuando veas:**
```
🚀 Iniciando servidor Flask API...
📝 API de Tareas disponible en: http://localhost:8001
 * Running on http://127.0.0.1:8001
```

### **Terminal 3: Consumidor WebSocket (Para ver notificaciones)**
```bash
PYTHONUNBUFFERED=1 python websocket_consumer.py
```
**✅ Listo cuando veas:**
```
🎯 Consumidor de Notificaciones de Tareas
✅ Conectado al servidor WebSocket
🔗 Conectado al servidor de notificaciones
👥 Clientes conectados: 1
```

## ⚡ Método Recomendado (Automático)

**La forma más fácil es usar el script automático:**

```bash
python start_websocket_system.py
```

Este script:
- ✅ Inicia automáticamente los 3 servicios
- ✅ Verifica que todo funcione 
- ✅ Crea tarea de prueba
- ✅ Organiza logs en carpeta `logs/`
- ✅ Cierre limpio con Ctrl+C

## 📂 Inicio Manual (Background)

Si prefieres control manual:
```bash
# Crear carpeta logs si no existe
mkdir -p logs

# Levantar todos los servicios en background
python websocket_server.py > logs/websocket_server.log 2>&1 & 
python app.py > logs/flask_api.log 2>&1 & 
PYTHONUNBUFFERED=1 python websocket_consumer.py > logs/websocket_consumer.log 2>&1 &

# Ver notificaciones en tiempo real
tail -f logs/websocket_consumer.log
```

## 🛠️ Gestión de Logs

**Todos los logs se guardan en la carpeta `logs/` para mantener organizado:**

### Ver logs en tiempo real:
```bash
# Notificaciones WebSocket
tail -f logs/websocket_consumer.log

# API Flask
tail -f logs/flask_api.log

# Servidor WebSocket
tail -f logs/websocket_server.log
```

### Limpiar/organizar logs:
```bash
# Script interactivo para gestionar logs
python clean_logs.py
```

### Ubicación correcta de logs:
- ✅ **Correcto**: `logs/websocket_server.log`
- ❌ **Incorrecto**: `websocket_server.log` (directorio principal)

## 📊 Funcionamiento

### 🔄 Flujo de Notificaciones

1. **Cliente** hace request a Flask API (crear/actualizar/eliminar tarea)
2. **Flask API** procesa el request y guarda datos
3. **Flask API** envía mensaje al **Servidor WebSocket**
4. **Servidor WebSocket** distribuye mensaje a todos los **Consumidores** conectados
5. **Consumidores** reciben y procesan notificaciones en tiempo real

```
Cliente HTTP → Flask API → WebSocket Server → Consumidores
```

### 📝 Tipos de Notificaciones

#### Crear Tarea (POST /tasks)
```json
{
  "type": "task_created",
  "task": {
    "id": "uuid",
    "title": "Nueva tarea",
    "description": "Descripción",
    "completed": false,
    "created_at": "2024-01-15T10:00:00Z"
  },
  "timestamp": "2024-01-15T10:00:00Z"
}
```

#### Actualizar Tarea (PUT/PATCH /tasks/:id)
```json
{
  "type": "task_updated", 
  "task": { /* tarea actualizada */ },
  "timestamp": "2024-01-15T10:00:00Z"
}
```

#### Eliminar Tarea (DELETE /tasks/:id)
```json
{
  "type": "task_deleted",
  "task": { /* tarea eliminada */ },
  "timestamp": "2024-01-15T10:00:00Z"
}
```

## 🔗 Endpoints API

| Método | Endpoint | Descripción | WebSocket |
|--------|----------|-------------|-----------|
| GET | `/tasks` | Listar tareas | ❌ |
| GET | `/tasks/:id` | Obtener tarea | ❌ |
| POST | `/tasks` | **Crear tarea** | ✅ |
| PUT | `/tasks/:id` | **Actualizar tarea completa** | ✅ |
| PATCH | `/tasks/:id` | **Actualizar tarea parcial** | ✅ |
| DELETE | `/tasks/:id` | **Eliminar tarea** | ✅ |

## 🧪 Pruebas

### Crear Tarea
```bash
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prueba WebSocket",
    "description": "Tarea para probar notificaciones"
  }'
```

### Actualizar Tarea
```bash
curl -X PATCH http://localhost:8001/tasks/TASK_ID \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Eliminar Tarea  
```bash
curl -X DELETE http://localhost:8001/tasks/TASK_ID
```

## 🛠️ Tecnologías

- **Flask**: API REST
- **websockets**: Comunicación WebSocket
- **asyncio**: Programación asíncrona
- **threading**: Manejo de hilos para WebSocket en Flask

## 🔧 Configuración

### WebSocket Server (websocket_server.py)
```python
host = "localhost"
port = 8765
```

### Flask App (app.py)
```python
WEBSOCKET_URL = "ws://localhost:8765"
```

## 📋 Notas Importantes

1. **Orden de inicio**: Primero WebSocket Server, luego Flask API
2. **Reconexión**: El consumidor reintenta conexión automáticamente
3. **Threading**: Flask usa hilos separados para WebSocket (no bloqueante)
4. **Producción**: En producción usar Redis/RabbitMQ para mensajería

## 🐛 Troubleshooting

### ❌ Error: "Connection refused" 
**Problema:** Flask API no puede conectar con WebSocket
**Solución:** 
```bash
# 1. Verificar que WebSocket server esté ejecutándose
lsof -i :8765

# 2. Si no está, iniciarlo primero:
python websocket_server.py
```

### ❌ Error: "Module not found"
**Problema:** Dependencias faltantes
**Solución:**
```bash
pip install -r requirements.txt
```

### ❌ Consumer log vacío o sin notificaciones
**Problema:** Python buffering en background
**Solución:**
```bash
# ✅ Correcto (con PYTHONUNBUFFERED):
PYTHONUNBUFFERED=1 python websocket_consumer.py

# ❌ Incorrecto (logs vacíos):
python websocket_consumer.py
```

### ❌ "Port already in use"
**Problema:** Proceso anterior aún ejecutándose
**Solución:**
```bash
# Matar procesos WebSocket
pkill -f "websocket.*py"

# Verificar puertos libres
lsof -i :8765 -i :8001
```

### ✅ Verificar que todo funciona:

**Opción 1 (Recomendada): Usar script automático**
```bash
python start_websocket_system.py
# El script ya incluye verificaciones automáticas
```

**Opción 2: Prueba manual**
```bash
# Crear una tarea de prueba
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "description": "Prueba WebSocket"}'

# Deberías ver la notificación en Terminal 3 (consumidor) o logs/websocket_consumer.log
```

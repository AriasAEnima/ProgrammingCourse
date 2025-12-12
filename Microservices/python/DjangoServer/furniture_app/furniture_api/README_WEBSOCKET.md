# 🔌 Integración WebSocket - Notificaciones en Tiempo Real

Documentación de la integración WebSocket para notificaciones de muebles en tiempo real.

## 📁 Estructura de Archivos

```
furniture_api/
├── __init__.py
├── views.py                 # Vistas de la API REST
├── urls.py                  # Rutas de la API
├── websocket_client.py      # ⭐ Cliente WebSocket (NUEVO)
└── README_WEBSOCKET.md      # Esta documentación
```

## 🎯 ¿Qué hace `websocket_client.py`?

El módulo `websocket_client.py` se encarga de enviar notificaciones al servidor WebSocket cada vez que hay cambios en los muebles:

- ✅ **Separación de responsabilidades**: La lógica de WebSocket está aislada
- ✅ **Reutilizable**: Funciones específicas para cada tipo de notificación
- ✅ **Manejo de errores**: No afecta el flujo principal si WebSocket falla
- ✅ **Tipado**: Usa type hints para mejor mantenibilidad
- ✅ **Logging**: Registra todas las operaciones

## 📡 Funciones Disponibles

### 1. `notify_furniture_created()`
Notifica cuando se crea un nuevo mueble

```python
from .websocket_client import notify_furniture_created

notify_furniture_created(
    furniture_id="673a2f1b8e4d2a1c3b5e6f7a",
    nombre="Mesa de Roble",
    descripcion="Mesa elegante de comedor",
    altura=75,
    ancho=120,
    material="roble",
    autor_username="Juan"
)
```

### 2. `notify_furniture_updated()`
Notifica cuando se actualiza un mueble existente

```python
from .websocket_client import notify_furniture_updated

notify_furniture_updated(
    furniture_id="673a2f1b8e4d2a1c3b5e6f7a",
    nombre="Mesa de Roble XL",
    descripcion="Mesa elegante - tamaño grande",
    altura=80,
    ancho=150,
    material="pino",
    autor_username="Juan"
)
```

### 3. `notify_furniture_deleted()`
Notifica cuando se elimina un mueble

```python
from .websocket_client import notify_furniture_deleted

notify_furniture_deleted(
    furniture_id="673a2f1b8e4d2a1c3b5e6f7a",
    nombre="Mesa de Roble",
    descripcion="Mesa elegante de comedor",
    altura=75,
    ancho=120,
    material="roble",
    autor_username="Juan"
)
```

## 🔄 Flujo de Notificaciones

```
1. Usuario → POST /api/furniture/create/
2. Django → Crea mueble en MongoDB
3. Django → notify_furniture_created()
4. websocket_client.py → Envía mensaje al WebSocket Server
5. WebSocket Server → Distribuye a todos los consumers conectados
6. Consumers → Muestran notificación en tiempo real
```

## ⚙️ Configuración

### Variable de Entorno

El cliente WebSocket usa la variable de entorno `WEBSOCKET_URL`:

```bash
# Por defecto (para Docker):
WEBSOCKET_URL=ws://websocket-server:8765

# Para desarrollo local:
WEBSOCKET_URL=ws://localhost:8765
```

### En settings.py

Si quieres configurarlo en Django settings:

```python
# settings.py
import os

WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://websocket-server:8765")
```

## 🛡️ Manejo de Errores

El cliente WebSocket está diseñado para **no interrumpir** el flujo normal de la aplicación:

- Si el servidor WebSocket no está disponible → **Se registra un warning**
- Si hay timeout → **Se registra un warning**
- Si hay error de conexión → **Se registra un error**

**El CRUD de muebles funciona sin importar el estado del WebSocket** ✅

## 📊 Logging

El módulo genera logs útiles:

```python
✅ Notificación WebSocket enviada: furniture_created - Mesa de Roble
⚠️ Timeout al conectar con WebSocket: ws://websocket-server:8765
❌ Error inesperado enviando notificación WebSocket: ...
```

## 🧪 Testing Manual

### 1. Iniciar WebSocket Server
```bash
cd websocket_server
python websocket_server.py
```

### 2. Iniciar Consumer
```bash
cd websocket_consumer
python websocket_consumer.py
```

### 3. Crear un Mueble
```bash
curl -X POST http://localhost:8000/api/furniture/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Mesa de Roble",
    "descripcion": "Mesa elegante",
    "altura": 75,
    "ancho": 120,
    "material": "roble",
    "autor_username": "Juan"
  }'
```

### 4. Ver Notificación en Consumer
Deberías ver algo como:

```
[14:30:45] 🪑 Nuevo mueble creado: Mesa de Roble - roble (120x75cm)
   🆔 ID: 673a2f1b8e4d2a1c3b5e6f7a
   🏷️  Nombre: Mesa de Roble
   📏 Dimensiones: 120cm (ancho) x 75cm (alto)
   🪵 Material: roble
   👤 Autor: Juan
   🎉 ¡Nuevo mueble disponible en el catálogo!
```

## 🔧 Personalización

### Agregar nuevos tipos de notificaciones

Si necesitas agregar más tipos de notificaciones:

1. **Agrega la función en `websocket_client.py`:**

```python
def notify_furniture_reserved(furniture_id: str, nombre: str, 
                              reserved_by: str) -> bool:
    """Notifica cuando se reserva un mueble"""
    furniture_data = {
        "furniture_id": furniture_id,
        "nombre": nombre,
        "reserved_by": reserved_by
    }
    return notify_websocket("furniture_reserved", furniture_data)
```

2. **Actualiza el WebSocket Server** para manejar el nuevo tipo
3. **Actualiza el Consumer** para mostrar el nuevo tipo

## 📚 Referencias

- **WebSocket Server**: `/websocket_server/websocket_server.py`
- **WebSocket Consumer**: `/websocket_consumer/websocket_consumer.py`
- **API Views**: `/furniture_api/views.py`
- **Modelos**: `/dynamicpages/models.py`

---

**Beneficios de esta arquitectura:**
- 🎯 Código limpio y organizado
- 🔌 Desacoplado del código principal
- 🛡️ Tolerante a fallos
- 📊 Fácil de monitorear
- 🧪 Fácil de probar



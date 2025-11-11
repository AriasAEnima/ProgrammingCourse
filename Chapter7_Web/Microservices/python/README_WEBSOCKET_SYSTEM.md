# 🔔 Sistema de Notificaciones en Tiempo Real - Mesas

Sistema completo de microservicios con notificaciones WebSocket para operaciones CRUD de mesas.

## 📐 Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     SISTEMA DE MESAS                            │
└─────────────────────────────────────────────────────────────────┘

1️⃣ API REST (Django)          2️⃣ WebSocket Server           3️⃣ (N) Consumer(s)
┌──────────────────┐          ┌──────────────────┐          ┌──────────────┐
│  DjangoSimpleServer│  HTTP   │  websocket_producer│  WS    │  websocket_  │
│                  │─────────→│                  │─────────→│  consumer    │
│  POST /api/desk/ │          │   ws://8765      │          │              │
│  PUT  /api/desk/:id│         │                  │          │  📺 Display  │
│  DELETE /api/desk/:id│       │  📡 Broadcast    │          │              │
└──────────────────┘          └──────────────────┘          └──────────────┘
         │                             ↑
         │    Envía notificación       │
         └─────────────────────────────┘
              (sin bloquear)
```

## 🎯 Flujo de Operación

1. **Cliente hace POST** → Crea mesa en Django
2. **Django guarda en MongoDB** → Mesa almacenada
3. **Django envía notificación** → Al servidor WebSocket (sin bloquear)
4. **WebSocket Server broadcast** → A todos los clientes conectados
5. **Consumers reciben notificación** → Muestran en tiempo real

## 📁 Estructura del Proyecto

```
Microservices/python/
├── websocket_server/          # Servidor WebSocket
│   ├── websocket_server.py
│   ├── requirements.txt
│   └── README.md
│
├── websocket_consumer/          # Cliente WebSocket
│   ├── websocket_consumer.py
│   ├── requirements.txt
│   └── README.md
│
└── DjangoSimpleServer/          # API REST
    ├── desk_app/
    │   ├── desk/
    │   │   ├── views.py         # Vistas API (dispatchers)
    │   │   ├── models.py        # Modelo Desk (MongoDB)
    │   │   ├── serializers.py   # Validación
    │   │   └── services/
    │   │       └── websocket_notifier.py  # ⭐ Servicio de notificaciones
    │   └── manage.py
    └── requirements.txt
```

## 🚀 Instalación y Ejecución

### 1. Instalar MongoDB

```bash
# MongoDB debe estar ejecutándose
# Windows: Services → MongoDB
# Mac: brew services start mongodb-community
```

### 2. Terminal 1: Servidor WebSocket (Producer)

```bash
cd websocket_producer
pip install -r requirements.txt
python websocket_server.py
```

Salida esperada:
```
🚀 Iniciando servidor WebSocket para Mesas...
📍 Servidor ejecutándose en ws://localhost:8765
```

### 3. Terminal 2: API Django

```bash
cd DjangoSimpleServer
pip install -r requirements.txt

# Crear .env con configuración de MongoDB
# Ver desk_app/ENV_SETUP.md

python desk_app/manage.py runserver
```

Salida esperada:
```
Django version 5.2.7
Starting development server at http://127.0.0.1:8000/
```

### 4. Terminal 3: Consumer (Opcional - para visualizar notificaciones)

```bash
cd websocket_consumer
pip install -r requirements.txt
python websocket_consumer.py
```

Salida esperada:
```
🎯 Consumidor de Notificaciones de Mesas
✅ Conectado al servidor WebSocket
```

## 🧪 Probar el Sistema

### Crear una Mesa

```bash
curl -X POST http://localhost:8000/api/desk/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mesa Ejecutiva",
    "width": 180,
    "height": 90
  }'
```

**Lo que sucede:**
1. ✅ Django guarda la mesa en MongoDB
2. 📡 Envía notificación al WebSocket Server
3. 📢 WebSocket Server hace broadcast
4. 📺 Todos los consumers muestran:

```
[14:30:45] 🪑 Nueva mesa creada: Mesa Ejecutiva (180x90cm)
   🆔 ID: 673a2f1b8e4d2a1c3b5e6f7a
   🏷️  Nombre: Mesa Ejecutiva
   📏 Dimensiones: 180cm x 90cm
   🎉 ¡Nueva mesa disponible!
```

### Actualizar una Mesa

```bash
curl -X PATCH http://localhost:8000/api/desk/673a2f1b8e4d2a1c3b5e6f7a \
  -H "Content-Type: application/json" \
  -d '{"width": 200}'
```

### Eliminar una Mesa

```bash
curl -X DELETE http://localhost:8000/api/desk/673a2f1b8e4d2a1c3b5e6f7a
```

## 🔑 Componentes Clave

### 1. Servicio de Notificaciones (Separado de views.py)

**`desk/services/websocket_notifier.py`**:

```python
# ✅ SEPARACIÓN DE RESPONSABILIDADES
# Este servicio maneja SOLO las notificaciones WebSocket

def notify_desk_created(desk):
    """Notifica que se creó una mesa"""
    # Envía en thread separado (no bloquea Django)
    
def notify_desk_updated(desk):
    """Notifica que se actualizó una mesa"""
    
def notify_desk_deleted(desk_id, desk_name):
    """Notifica que se eliminó una mesa"""
```

### 2. Vistas (Solo lógica de negocio)

**`desk/views.py`**:

```python
def _handle_create_desk(request):
    # 1. Validar datos
    serializer = DeskSerializer(data=request.data)
    
    # 2. Guardar en BD
    desk = serializer.save()
    
    # 3. Notificar (llamando al servicio)
    websocket_notifier.notify_desk_created(desk)
    
    return Response(serializer.data, status=201)
```

✅ **Ventajas de esta arquitectura:**
- Views solo maneja HTTP/REST
- Servicio maneja notificaciones
- Fácil testear cada parte
- Fácil desactivar notificaciones si el WebSocket Server no está disponible

## 🐛 Troubleshooting

### Error: "No se pudo conectar al servidor WebSocket"

**Causa:** El servidor WebSocket no está ejecutándose.

**Solución:**
1. Abre una terminal
2. `cd websocket_producer`
3. `python websocket_server.py`

**Nota:** Django seguirá funcionando normalmente, solo no enviará notificaciones.

### Error: "Connection refused to MongoDB"

**Causa:** MongoDB no está ejecutándose.

**Solución:**
- Windows: Services → Iniciar MongoDB
- Mac: `brew services start mongodb-community`

### Las notificaciones no llegan

**Verificar:**

```bash
# 1. ¿Está corriendo el WebSocket Server?
# Terminal 1: python websocket_server.py

# 2. ¿Está corriendo Django?
# Terminal 2: python manage.py runserver

# 3. ¿Está conectado el consumer?
# Terminal 3: python websocket_consumer.py

# 4. Hacer una operación
curl -X POST http://localhost:8000/api/desk/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "width": 100, "height": 200}'

# Deberías ver logs en todas las terminales
```

## 📊 Logs del Sistema

### WebSocket Server:
```
📥 Mensaje recibido de 127.0.0.1:51234: desk_created
📨 Mensaje enviado exitosamente a 2/2 clientes
```

### Django:
```
Creando mesa: {'name': 'Mesa Test', 'width': 100, 'height': 200}
✅ Notificación WebSocket enviada: desk_created
```

### Consumer:
```
[14:30:45] 🪑 Nueva mesa creada: Mesa Test (100x200cm)
```

## 🎨 Ventajas de esta Arquitectura

| Aspecto | Beneficio |
|---------|-----------|
| **Separación de responsabilidades** | Views maneja HTTP, servicio maneja WebSocket |
| **No bloquea** | Notificaciones en thread separado |
| **Escalable** | Fácil agregar más consumers |
| **Testeable** | Cada componente se puede testear por separado |
| **Resiliente** | Si WebSocket falla, API sigue funcionando |
| **Microservicios** | Cada parte puede ejecutarse en servidor diferente |

## 🚢 Despliegue

### Desarrollo (Local):
- Todo en localhost
- 3 terminales

### Producción:
```
API Django → servidor-api.com:8000
WebSocket  → ws://servidor-ws.com:8765
MongoDB    → servidor-db.com:27017
Consumers  → Múltiples clientes conectados
```

## 📚 Recursos

- [Django REST Framework](https://www.django-rest-framework.org/)
- [WebSockets en Python](https://websockets.readthedocs.io/)
- [MongoDB con Django](http://docs.mongoengine.org/)

## 💡 Próximos Pasos

- ✅ Agregar autenticación JWT
- ✅ Dockerizar todo el sistema
- ✅ Agregar tests unitarios
- ✅ Implementar reconexión automática
- ✅ Agregar logging centralizado


# 🔐 Autenticación JWT + WebSocket - Microservices

Sistema completo de autenticación JWT y notificaciones WebSocket en tiempo real para la API de muebles.

## 🚀 Características

- ✅ Autenticación JWT con tokens de acceso y refresh
- ✅ Control de permisos por rol (admin, manager, user)
- ✅ Autor automático desde token JWT
- ✅ Notificaciones WebSocket en tiempo real
- ✅ Solo el autor o admin puede modificar/eliminar muebles

## 🎯 Usuarios Por Defecto

| Username | Password | Rol | Descripción |
|----------|----------|-----|-------------|
| `admin1` | `admin123` | admin | Acceso completo |
| `manager` | `manager123` | manager | Gestión de muebles |

## 🔧 Configuración Inicial

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Inicializar Usuarios

El sistema requiere usuarios para funcionar. Debes ejecutar este comando **UNA VEZ**:

```bash
cd furniture_app
python manage.py init_users
```

**O con Docker:**

```bash
docker-compose exec django-api python manage.py init_users
```

**Salida esperada:**
```
🔧 Inicializando usuarios...
✅ Usuarios iniciales creados en MongoDB
✅ Usuarios inicializados correctamente
```

**Usuarios creados:**
- `admin1` / `admin123` (role: admin)
- `manager` / `manager123` (role: manager)

**⚠️ Importante:** El comando solo crea usuarios si la colección está vacía (`User.objects.count() == 0`).

### 📚 **Más Formas de Agregar Usuarios:**

1. **Vía API Register** (cualquiera puede registrarse):
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "pedro", "password": "pedro123", "role": "user"}'
```

2. **Modificar usuarios iniciales** en `auth_api/models.py` → método `initialize_users()`

3. **Django Shell** (para testing):
```bash
python manage.py shell
>>> from auth_api.models import User
>>> user = User(user_id='user-3', username='ana', role='user')
>>> user.set_password('ana123')
>>> user.save()
```

### 3. Iniciar Sistema Completo con Docker

```bash
# Desde la raíz del proyecto Microservices/python
docker-compose down -v
docker-compose up --build
```

## 📡 Endpoints de Autenticación

### Login

```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin1",
  "password": "admin123"
}
```

**Respuesta:**
```json
{
  "message": "Login exitoso",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "user-1",
    "username": "admin1",
    "role": "admin"
  }
}
```

### Register

```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "nuevo_usuario",
  "password": "password123",
  "role": "user"
}
```

## 🪑 Endpoints de Muebles (Protegidos con JWT)

### Crear Mueble

El autor se obtiene **automáticamente del token JWT**:

```bash
POST /api/furniture/create/
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

{
  "nombre": "Mesa de Roble",
  "descripcion": "Mesa elegante de comedor",
  "altura": 75,
  "ancho": 120,
  "material": "roble"
}
```

**✅ Notificación WebSocket enviada automáticamente**

### Actualizar Mueble (Solo autor o admin)

```bash
PUT /api/furniture/{id}/update/
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

{
  "altura": 80,
  "material": "pino"
}
```

**✅ Notificación WebSocket enviada automáticamente**

### Eliminar Mueble (Solo autor o admin)

```bash
DELETE /api/furniture/{id}/
Authorization: Bearer YOUR_TOKEN_HERE
```

**✅ Notificación WebSocket enviada automáticamente**

### Listar Muebles

```bash
GET /api/furniture/
Authorization: Bearer YOUR_TOKEN_HERE
```

## 🧪 Ejemplo Completo de Uso

### 1. Login y obtener token

```bash
# Login como admin
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin1", "password": "admin123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. Crear mueble (se notifica vía WebSocket)

```bash
curl -X POST http://localhost:8000/api/furniture/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nombre": "Silla Moderna",
    "descripcion": "Silla ergonómica",
    "altura": 90,
    "ancho": 50,
    "material": "plastico"
  }'
```

### 3. Ver notificación en el consumer

Los logs del consumer mostrarán:

```
[14:30:45] 🪑 Nuevo mueble creado: Silla Moderna - plastico (50x90cm)
   🆔 ID: 693b265ec5c526f011ab3a8f
   🏷️  Nombre: Silla Moderna
   📏 Dimensiones: 50cm (ancho) x 90cm (alto)
   🪵 Material: plastico
   👤 Autor: admin1  ← Obtenido del JWT token
   🎉 ¡Nuevo mueble disponible en el catálogo!
```

## 🔑 Control de Acceso

| Operación | Usuario Normal | Manager | Admin |
|-----------|---------------|---------|-------|
| Listar muebles | ✅ | ✅ | ✅ |
| Crear mueble | ✅ | ✅ | ✅ |
| Ver mueble | ✅ | ✅ | ✅ |
| Actualizar propio mueble | ✅ | ✅ | ✅ |
| Actualizar mueble de otro | ❌ | ❌ | ✅ |
| Eliminar propio mueble | ✅ | ✅ | ✅ |
| Eliminar mueble de otro | ❌ | ❌ | ✅ |

## 🏗️ Arquitectura Completa

```
┌─────────────────┐
│  Usuario/API    │
│  con JWT Token  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Django API     │─────▶│     MongoDB      │
│  + JWT Auth     │      │   (Usuarios +    │
│  (Producer)     │      │    Muebles)      │
└────────┬────────┘      └──────────────────┘
         │
         │ websocket_client.py
         │ (Notifica: autor del token)
         ▼
┌─────────────────┐
│ WebSocket Server│
│    (Broker)     │
└────────┬────────┘
         │
         │ Broadcast
         ▼
┌─────────────────┐
│  Consumer(s)    │
│   (Clientes)    │
│ Muestran autor  │
└─────────────────┘
```

## 🔐 Seguridad

- ✅ Contraseñas hasheadas con werkzeug
- ✅ Tokens JWT con expiración (1 hora)
- ✅ El autor NO puede ser falsificado (viene del token)
- ✅ Verificación de permisos en cada operación
- ✅ Solo autor o admin pueden modificar/eliminar

## 📚 Archivos Clave

```
auth_api/
├── models.py          # Usuario con MongoDB
├── views.py           # Login/Register
├── urls.py            # Rutas auth
├── utils.py           # @jwt_required, @admin_required
└── management/
    └── commands/
        └── init_users.py

furniture_api/
├── views.py           # CRUD con JWT + WebSocket
├── urls.py            # Rutas API
└── websocket_client.py  # Notificaciones WebSocket
```

## 🚨 Diferencias Clave vs Sin JWT

### Antes (Sin JWT):
```json
{
  "nombre": "Mesa",
  "autor_username": "admin1"  ← Podía ser falsificado
}
```

### Ahora (Con JWT):
```bash
# El autor se obtiene del token automáticamente
Authorization: Bearer eyJ0eXAiOiJKV1...

# Body:
{
  "nombre": "Mesa"
  // autor_username ya NO se envía
}
```

**El autor es SIEMPRE el usuario del token. No puede ser falsificado.** ✅

---

**¡Sistema completo de JWT + WebSocket funcionando!** 🎉🔐🔌


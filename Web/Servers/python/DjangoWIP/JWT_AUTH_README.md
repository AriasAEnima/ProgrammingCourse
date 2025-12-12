# 🔐 Autenticación JWT con PyJWT - Django Furniture API

Sistema de autenticación JWT implementado usando **PyJWT directamente** (sin djangorestframework-simplejwt) para máxima compatibilidad con MongoDB y usuarios personalizados.

## 🎯 Usuarios Por Defecto

| Username | Password | Rol | Descripción |
|----------|----------|-----|-------------|
| `admin1` | `admin123` | admin | Puede crear, editar y eliminar cualquier mueble |
| `manager` | `manager123` | manager | Puede gestionar muebles |

## 🚀 Inicializar Usuarios

Antes de usar la API, debes inicializar los usuarios **UNA VEZ**:

```bash
# Desde la carpeta furniture_app
python manage.py init_users
```

**Salida esperada:**
```
🔧 Inicializando usuarios...
✅ Usuarios iniciales creados en MongoDB
✅ Usuarios inicializados correctamente
```

### 🔍 **¿Cómo Funciona?**

Django busca comandos personalizados en todas las apps de `INSTALLED_APPS`:

```
auth_api/
└── management/          ← Django busca aquí automáticamente
    └── commands/        ← En todas las apps instaladas
        └── init_users.py ← Tu comando: python manage.py init_users
```

El comando solo crea usuarios si **NO existen** (verifica con `User.objects.count() == 0`).

### ➕ **Agregar Más Usuarios Iniciales**

Si quieres agregar más usuarios por defecto, edita `auth_api/models.py`:

```python
@classmethod
def initialize_users(cls):
    """Inicializa usuarios por defecto si no existen"""
    if cls.objects.count() == 0:
        # Usuario admin
        admin = cls(user_id='user-1', username='admin1', role='admin')
        admin.set_password('admin123')
        admin.save()
        
        # Usuario manager
        manager = cls(user_id='user-2', username='manager', role='manager')
        manager.set_password('manager123')
        manager.save()
        
        # ⭐ AGREGA AQUÍ MÁS USUARIOS:
        user = cls(user_id='user-3', username='juan', role='user')
        user.set_password('juan123')
        user.save()
        
        print("✅ Usuarios iniciales creados en MongoDB")
```

Luego borra la base de datos y ejecuta de nuevo:

```bash
# Eliminar la colección de usuarios en MongoDB (opcional)
# Ejecutar de nuevo
python manage.py init_users
```

## 📡 Endpoints de Autenticación

### 1. **Login** - Obtener JWT Token

```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin1",
  "password": "admin123"
}
```

**Respuesta exitosa:**
```json
{
  "message": "Login exitoso",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-1",
    "username": "admin1",
    "role": "admin"
  }
}
```

### 2. **Register** - Registrar Nuevo Usuario

```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "nuevo_usuario",
  "password": "password123",
  "role": "user"  // opcional: admin, manager, user (default: user)
}
```

**Respuesta exitosa:**
```json
{
  "message": "Usuario creado exitosamente",
  "user": {
    "id": "user-3",
    "username": "nuevo_usuario",
    "role": "user"
  }
}
```

## 👥 **Formas de Agregar Usuarios**

### **Método 1: Vía API (Recomendado para usuarios normales)**

Cualquiera puede registrarse usando el endpoint `/api/auth/register/`:

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria",
    "password": "maria123",
    "role": "user"
  }'
```

**Ventajas:**
- ✅ No requiere acceso al servidor
- ✅ El usuario se crea con ID automático incremental
- ✅ Valida que el username no exista
- ✅ Funciona desde la aplicación cliente

### **Método 2: Comando Django (Para usuarios iniciales/admin)**

Modifica `auth_api/models.py` y ejecuta `python manage.py init_users`:

```python
# En auth_api/models.py - método initialize_users()

# Agregar más usuarios iniciales
nuevo_user = cls(
    user_id='user-3',
    username='pedro',
    role='manager'
)
nuevo_user.set_password('pedro123')
nuevo_user.save()
```

**Ventajas:**
- ✅ Útil para datos de prueba/desarrollo
- ✅ Se ejecuta una vez al inicio
- ✅ Ideal para usuarios administrativos

### **Método 3: Directamente en MongoDB (Avanzado)**

Conectarte directamente a MongoDB y crear el documento:

```javascript
// Conectar a MongoDB
mongosh

// Usar la base de datos
use furniture_catalog_db

// Insertar usuario manualmente
db.users.insertOne({
  "user_id": "user-4",
  "username": "carlos",
  "password_hash": "pbkdf2:sha256:...",  // Debes generar el hash
  "role": "user",
  "created_at": new Date()
})
```

**⚠️ NO recomendado:** Debes generar el hash de contraseña correctamente.

### **Método 4: Django Shell (Para testing rápido)**

```bash
python manage.py shell
```

Luego en el shell:

```python
from auth_api.models import User

# Crear usuario
user = User(
    user_id='user-5',
    username='ana',
    role='user'
)
user.set_password('ana123')
user.save()

print(f"✅ Usuario {user.username} creado")
```

**Ventajas:**
- ✅ Rápido para pruebas
- ✅ No requiere modificar código
- ✅ Ideal para desarrollo

## 🎯 **Recomendaciones por Caso de Uso:**

| Caso | Método Recomendado |
|------|-------------------|
| **Usuarios iniciales (admin)** | Comando Django (`init_users`) |
| **Nuevos usuarios normales** | API Register endpoint |
| **Testing rápido** | Django Shell |
| **Usuarios de prueba automáticos** | Modificar `initialize_users()` |

## 🔒 Endpoints Protegidos (Requieren JWT)

Todos los endpoints de la furniture API ahora requieren autenticación:

### Listar Muebles

```bash
GET /api/furniture/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Crear Mueble

El autor se obtiene automáticamente del token JWT:

```bash
POST /api/furniture/create/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "nombre": "Mesa de Roble",
  "descripcion": "Mesa elegante de comedor",
  "altura": 75,
  "ancho": 120,
  "material": "roble"
}
```

**✨ Nota:** Ya NO necesitas enviar `autor_username` en el body. Se obtiene automáticamente del token.

### Actualizar Mueble

Solo el autor o un administrador puede actualizar:

```bash
PUT /api/furniture/{id}/update/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "altura": 80,
  "material": "pino"
}
```

### Eliminar Mueble

Solo el autor o un administrador puede eliminar:

```bash
DELETE /api/furniture/{id}/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🧪 Ejemplo Completo con cURL

```bash
# 1. Login y obtener token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin1", "password": "admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token obtenido: $TOKEN"

# 2. Crear mueble con el token (autor = admin1 automáticamente)
curl -s -X POST http://localhost:8000/api/furniture/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nombre": "Silla Moderna",
    "descripcion": "Silla ergonómica",
    "altura": 90,
    "ancho": 50,
    "material": "plastico"
  }' | python3 -m json.tool

# 3. Listar muebles
curl -s -X GET http://localhost:8000/api/furniture/ \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
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

## 🛠️ Implementación Técnica

### PyJWT Directo (Sin DRF-SimpleJWT)

Este proyecto usa **PyJWT directamente** en lugar de djangorestframework-simplejwt para:
- ✅ Compatibilidad total con MongoDB
- ✅ Control total sobre el formato de tokens
- ✅ Usuarios personalizados (no depende del modelo User de Django)
- ✅ Más ligero y directo

### Estructura del Token

```python
{
  "username": "admin1",
  "role": "admin",
  "user_id": "user-1",
  "token_type": "access",
  "exp": 1765489350,  # Expira en 1 hora
  "iat": 1765485750   # Issued at
}
```

### Generación de Tokens

```python
# En auth_api/views.py
import jwt
from datetime import datetime, timedelta
from django.conf import settings

def create_tokens(user):
    access_payload = {
        'username': user.username,
        'role': user.role,
        'user_id': user.user_id,
        'token_type': 'access',
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
    return access_token, refresh_token
```

### Validación de Tokens

```python
# En auth_api/utils.py
import jwt
from django.conf import settings

def get_user_from_token(request):
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split(' ')[1]  # Extrae después de "Bearer "
    
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=['HS256']
    )
    
    return payload.get('username'), payload.get('role'), payload.get('user_id')
```

## 🔐 Seguridad

- ✅ Contraseñas hasheadas con Werkzeug
- ✅ Tokens JWT con expiración (1 hora access, 1 día refresh)
- ✅ Verificación de autorización en cada endpoint
- ✅ El autor se obtiene del token (no puede ser falsificado)
- ✅ Control de permisos por rol (admin, manager, user)
- ✅ Algoritmo HS256 para firma de tokens

## 📚 Archivos Clave

```
auth_api/
├── models.py          # Modelo User con MongoDB
├── views.py           # Login/Register con PyJWT
├── urls.py            # Rutas de autenticación
├── utils.py           # @jwt_required, @admin_required (validación PyJWT)
└── management/
    └── commands/
        └── init_users.py  # Inicializar usuarios

furniture_api/
├── views.py           # CRUD con JWT (autor automático)
└── urls.py            # Rutas API
```

## 🚨 Errores Comunes

### Error 401: Token inválido o expirado
- El token expira en 1 hora
- Verifica que incluyas "Bearer " antes del token
- Formato correcto: `Authorization: Bearer eyJhbGc...`

### Error 403: Acceso denegado
- Solo el autor o un administrador puede modificar/eliminar
- Verifica tu rol de usuario

### Error: "Token has no id" o problemas con djangorestframework-simplejwt
- Este proyecto NO usa djangorestframework-simplejwt
- Usamos PyJWT directamente, NO hay `DEFAULT_AUTHENTICATION_CLASSES` en settings.py

## 🆚 Comparación: PyJWT vs DRF-SimpleJWT

| Característica | PyJWT (Este proyecto) | DRF-SimpleJWT |
|----------------|----------------------|---------------|
| **Dependencias** | Menos, más ligero | Más dependencias |
| **Control** | Total sobre tokens | Configuración limitada |
| **MongoDB** | Compatible nativamente | Requiere workarounds |
| **Usuarios custom** | Totalmente compatible | Requiere configuración |
| **Complejidad** | Más simple y directo | Más abstraído |

---

**¡Sistema de autenticación JWT funcionando con PyJWT puro!** 🎉🔐


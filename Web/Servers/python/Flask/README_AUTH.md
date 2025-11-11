# 🔐 Sistema de Autenticación JWT - Flask API

## 📋 Índice
- [Introducción](#introducción)
- [Conceptos Clave](#conceptos-clave)
- [Configuración](#configuración)
- [Sistema de Roles](#sistema-de-roles)
- [Endpoints de Autenticación](#endpoints-de-autenticación)
- [Decorators de Verificación](#decorators-de-verificación)
- [Ejemplos Prácticos con cURL](#ejemplos-prácticos-con-curl)
- [Manejo de Errores](#manejo-de-errores)
- [Debugging y Troubleshooting](#debugging-y-troubleshooting)

---

## Introducción

Este proyecto implementa un sistema de **autenticación JWT (JSON Web Tokens)** completo con **verificación de roles** para una API REST de restaurantes en Flask.

### ✨ Características Principales:
- **Autenticación stateless** con JWT
- **3 niveles de roles**: user, manager, admin
- **Tokens con expiración** configurable (1 hora por defecto)
- **Protección de endpoints** por roles
- **Manejo de errores** personalizado
- **WebSocket notifications** integradas

---

## Conceptos Clave

### 🎯 ¿Qué es JWT?
**JWT (JSON Web Token)** es un estándar para transmitir información de forma segura entre partes como un objeto JSON compacto y autocontenido.

**Estructura JWT:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.signature
    ↓ Header              ↓ Payload                    ↓ Signature
```

### 🔄 ¿Cómo funciona?

```
🔐 FLUJO DE AUTENTICACIÓN JWT

1. 📱 Cliente                    2. 🖥️  Servidor
   |                               |
   | POST /auth/login              |
   | {username, password} -------> | ✅ Valida credenciales
   |                               | 🔑 Genera JWT con rol
   | <------ {access_token} ------ |
   |                               |
   | 💾 Almacena token             |
   |                               |
   | POST /api/restaurantes        |
   | Authorization: Bearer <token> | 🔍 Extrae rol del JWT
   | {...data...} ---------------> | ❓ ¿Rol permitido?
   |                               |
   | <------ ✅/❌ Respuesta ----- | ✅ 200 OK / ❌ 403 Forbidden

📋 VERIFICACIÓN POR PASOS:
   Step 1: Cliente envía credenciales → Servidor valida
   Step 2: Servidor genera JWT con rol → Cliente almacena token  
   Step 3: Cliente envía token en requests → Servidor verifica rol
   Step 4: Servidor permite/deniega → Cliente recibe respuesta
```

### 🚀 Ventajas vs Sesiones tradicionales:

| JWT (Stateless) | Sesiones (Stateful) |
|----------------|---------------------|
| ✅ No requiere almacenamiento server | ❌ Requiere storage de sesiones |
| ✅ Escalable horizontalmente | ❌ Difícil de escalar |
| ✅ Compatible con microservicios | ❌ Limitado a una app |
| ✅ Información en el token | ❌ Consultas adicionales a BD |

---

## Configuración

### 📦 Dependencias Requeridas:
```bash
pip install Flask-JWT-Extended==4.7.1
pip install Werkzeug  # Para hash de passwords
```

### ⚙️ Configuración en Flask:
```python
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Configuración JWT
app.config['JWT_SECRET_KEY'] = 'tu-clave-super-secreta-cambiar-en-produccion'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)
```

⚠️ **IMPORTANTE**: En producción, usa una clave secreta robusta y configúrala como variable de entorno.

---

## Sistema de Roles

### 👥 Jerarquía de Usuarios:

| Rol | Permisos | Descripción |
|-----|----------|-------------|
| **👤 user** | `read` | Solo lectura. Puede ver restaurantes |
| **👔 manager** | `read`, `create`, `update` | Puede gestionar restaurantes (no eliminar) |
| **👑 admin** | `read`, `create`, `update`, `delete` | Control total del sistema |

### 🔒 Matriz de Permisos:

| Endpoint | user | manager | admin |
|----------|------|---------|-------|
| `GET /api/restaurantes` | ✅ | ✅ | ✅ |
| `GET /api/restaurantes/<id>` | ✅ | ✅ | ✅ |
| `POST /api/restaurantes` | ❌ | ✅ | ✅ |
| `PUT /api/restaurantes/<id>` | ❌ | ✅ | ✅ |
| `PATCH /api/restaurantes/<id>` | ❌ | ✅ | ✅ |
| `DELETE /api/restaurantes/<id>` | ❌ | ❌ | ✅ |

### 🏗️ Usuarios Demo Preconfigurados:

```json
{
  "admin": {
    "username": "admin",
    "password": "admin123",
    "role": "admin"
  },
  "manager": {
    "username": "manager", 
    "password": "manager123",
    "role": "manager"
  },
  "user": {
    "username": "user",
    "password": "user123", 
    "role": "user"
  }
}
```

---

## Endpoints de Autenticación

### 🔑 Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Respuesta exitosa:**
```json
{
  "message": "Login exitoso",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-1",
    "username": "admin",
    "role": "admin"
  }
}
```

### 📝 Registro
```http
POST /auth/register
Content-Type: application/json

{
  "username": "nuevo_user",
  "password": "password123",
  "role": "user"
}
```

### 👤 Perfil del Usuario
```http
GET /auth/profile
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "user": {
    "id": "user-1",
    "username": "admin",
    "role": "admin", 
    "created_at": "2024-01-15T10:00:00Z",
    "permissions": ["read", "create", "update", "delete"]
  }
}
```

### 🔍 Verificación de Permisos
```http
GET /auth/whoami
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "current_user": {
    "username": "admin",
    "role": "admin",
    "user_id": "user-1"
  },
  "can_create": true,
  "can_update": true,
  "can_delete": true,
  "jwt_claims": {
    "role": "admin",
    "exp": 1757722810,
    "sub": "admin"
  }
}
```

---

## Decorators de Verificación

### 🎯 Decorators Implementados:

#### 1. **`@jwt_required()`**
Verifica que el usuario esté autenticado (cualquier rol).

```python
@app.route('/protected')
@jwt_required()
def protected():
    return {"message": "Acceso permitido"}
```

#### 2. **`@admin_required`** 
Solo administradores pueden acceder.

```python
@app.route('/admin-only')
@admin_required
def admin_only():
    return {"message": "Solo para admins"}
```

#### 3. **`@manager_or_admin_required`**
Managers y admins pueden acceder.

```python
@app.route('/create-something')
@manager_or_admin_required  
def create_something():
    return {"message": "Manager o admin requerido"}
```

#### 4. **`@role_required(['role1', 'role2'])`**
Decorator flexible para múltiples roles.

```python
@app.route('/flexible')
@role_required(['manager', 'admin'])
def flexible():
    return {"message": "Manager o admin"}
```

### 🛠️ Funciones Auxiliares:

```python
def get_current_user_role():
    """Obtiene el rol del usuario desde JWT"""
    claims = get_jwt()
    return claims.get('role', 'user')

def get_current_user_data():
    """Obtiene todos los datos del usuario"""
    return {
        'username': get_jwt_identity(),
        'role': get_jwt().get('role'),
        'user_id': get_jwt().get('user_id')
    }
```

---

## Ejemplos Prácticos con cURL

### 🚀 Flujo Completo de Autenticación:

#### 1. **Login y Obtener Token:**
```bash
# Login como admin
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Respuesta:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

#### 2. **Usar Token en Requests:**
```bash
# Guardar token en variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Crear restaurante (requiere manager/admin)
curl -X POST "http://localhost:8001/api/restaurantes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nombre": "Nuevo Restaurante",
    "tipo_cocina": "Italiana",
    "direccion": "Calle Nueva 123",
    "telefono": "+1-555-9999",
    "calificacion": 4.5,
    "precio_promedio": 30.0,
    "delivery": true
  }'
```

### 🧪 Ejemplos por Rol:

#### **Usuario básico (user):**
```bash
# 1. Login como user
USER_TOKEN=$(curl -s -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user123"}' | \
  jq -r '.access_token')

# 2. Ver restaurantes (permitido)
curl -H "Authorization: Bearer $USER_TOKEN" \
  "http://localhost:8001/api/restaurantes"

# 3. Intentar crear restaurante (denegado)
curl -X POST "http://localhost:8001/api/restaurantes" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Test", "tipo_cocina": "Test"}'

# Respuesta: 403 Forbidden
{
  "error": "Acceso denegado",
  "message": "Se requiere rol de manager o admin"
}
```

#### **Manager:**
```bash
# 1. Login como manager
MANAGER_TOKEN=$(curl -s -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "manager", "password": "manager123"}' | \
  jq -r '.access_token')

# 2. Crear restaurante (permitido)
curl -X POST "http://localhost:8001/api/restaurantes" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Manager Restaurant",
    "tipo_cocina": "Fusion",
    "direccion": "Manager St 456",
    "telefono": "+1-555-7777",
    "calificacion": 4.2,
    "precio_promedio": 28.0,
    "delivery": false
  }'

# 3. Intentar eliminar restaurante (denegado)
curl -X DELETE "http://localhost:8001/api/restaurantes/1" \
  -H "Authorization: Bearer $MANAGER_TOKEN"

# Respuesta: 403 Forbidden
{
  "error": "Acceso denegado",
  "message": "Solo los administradores pueden acceder a este endpoint"
}
```

#### **Administrador:**
```bash
# 1. Login como admin
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  jq -r '.access_token')

# 2. Crear restaurante (permitido)
curl -X POST "http://localhost:8001/api/restaurantes" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Admin Restaurant",
    "tipo_cocina": "Gourmet",
    "direccion": "Admin Ave 789", 
    "telefono": "+1-555-0001",
    "calificacion": 4.8,
    "precio_promedio": 50.0,
    "delivery": true
  }'

# 3. Eliminar restaurante (permitido)
curl -X DELETE "http://localhost:8001/api/restaurantes/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Respuesta: 200 OK
{
  "message": "Restaurante eliminado exitosamente",
  "deleted_restaurant": { ... }
}
```

### 🔍 Debugging y Verificación:

#### **Verificar permisos del usuario actual:**
```bash
curl -X GET "http://localhost:8001/auth/whoami" \
  -H "Authorization: Bearer $TOKEN"

# Respuesta:
{
  "current_user": {
    "username": "admin",
    "role": "admin"
  },
  "can_create": true,
  "can_update": true, 
  "can_delete": true,
  "jwt_claims": {
    "role": "admin",
    "exp": 1757722810,
    "sub": "admin"
  }
}
```

#### **Ver perfil completo:**
```bash
curl -X GET "http://localhost:8001/auth/profile" \
  -H "Authorization: Bearer $TOKEN"
```

### 🔄 Casos de Prueba Completos:

#### **Script de Prueba Automática:**
```bash
#!/bin/bash

echo "🔐 Probando Sistema de Autenticación"
echo "===================================="

BASE_URL="http://localhost:8001"

# 1. Test sin token (debe fallar)
echo "📋 1. Intentar crear sin token:"
curl -s -X POST "$BASE_URL/api/restaurantes" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Test"}' | jq .

# 2. Login y test con user
echo -e "\n📋 2. Login como user:"
USER_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user123"}' | jq -r '.access_token')

echo "📋 3. User intenta crear (debe fallar):"
curl -s -X POST "$BASE_URL/api/restaurantes" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Test"}' | jq .

# 3. Login y test con admin
echo -e "\n📋 4. Login como admin:"
ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.access_token')

echo "📋 5. Admin crea restaurante (debe funcionar):"
curl -s -X POST "$BASE_URL/api/restaurantes" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Restaurant",
    "tipo_cocina": "Test",
    "direccion": "Test St 123",
    "telefono": "+1-555-0000",
    "calificacion": 4.0,
    "precio_promedio": 25.0,
    "delivery": true
  }' | jq .

echo -e "\n✅ Tests completados!"
```

---

## Manejo de Errores

### 🚨 Códigos de Error Comunes:

| Código | Error | Descripción |
|--------|-------|-------------|
| **400** | Bad Request | Datos faltantes o inválidos |
| **401** | Unauthorized | Token inválido, expirado o faltante |
| **403** | Forbidden | Token válido pero permisos insuficientes |
| **404** | Not Found | Usuario o recurso no encontrado |

### 📝 Ejemplos de Respuestas de Error:

#### **Token Faltante:**
```json
{
  "error": "Token requerido",
  "message": "Se requiere un token JWT válido para acceder a este endpoint."
}
```

#### **Token Expirado:**
```json
{
  "error": "Token expirado", 
  "message": "El token JWT ha expirado. Por favor inicia sesión nuevamente."
}
```

#### **Permisos Insuficientes:**
```json
{
  "error": "Acceso denegado",
  "message": "Se requiere rol de manager o admin"
}
```

#### **Credenciales Inválidas:**
```json
{
  "error": "Credenciales inválidas",
  "message": "Username o password incorrectos"
}
```

---

## Debugging y Troubleshooting

### 🔧 Herramientas de Debug:

#### **1. Verificar estructura del token:**
```bash
# Decodificar JWT (solo para debug - NO hacer en producción)
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." | cut -d'.' -f2 | base64 -d | jq .
```

#### **2. Endpoint de diagnóstico:**
```bash
# Ver todos los claims del JWT actual
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/auth/whoami"
```

#### **3. Logs del servidor:**
```bash
# Ver logs en tiempo real
tail -f logs/flask_api.log
```

### 🐛 Problemas Comunes:

#### **"Token requerido"**
- ✅ **Solución**: Incluir header `Authorization: Bearer <token>`
- ❌ **Error común**: Olvidar el prefijo "Bearer "

#### **"Token expirado"**  
- ✅ **Solución**: Hacer login nuevamente para obtener token fresco
- ⚙️ **Configurar**: Ajustar `JWT_ACCESS_TOKEN_EXPIRES` para mayor duración

#### **"Acceso denegado"**
- ✅ **Solución**: Verificar rol del usuario con `/auth/whoami`
- 🔍 **Debug**: ¿El usuario tiene el rol correcto para este endpoint?

#### **"Credenciales inválidas"**
- ✅ **Solución**: Verificar username/password
- 👥 **Users demo**: admin:admin123, manager:manager123, user:user123

### 📊 Monitoreo y Logs:

#### **Logs importantes a revistar:**
```bash
# Errores de autenticación
grep "401\|403" logs/flask_api.log

# Logins exitosos
grep "Login exitoso" logs/flask_api.log

# Creaciones/eliminaciones (con WebSocket)
tail -f logs/websocket_consumer.log
```

---

## 🎯 Resumen Ejecutivo

### ✅ **Lo que tienes funcionando:**

1. **🔐 Autenticación JWT completa** con 3 roles (user/manager/admin)
2. **🛡️ Protección por endpoints** según permisos
3. **🎪 Decorators flexibles** para verificación de roles
4. **📡 WebSocket integration** con notificaciones en tiempo real
5. **🔍 Debugging endpoints** (`/auth/whoami`, `/auth/profile`)
6. **⚠️ Manejo de errores** detallado y user-friendly

### 🚀 **Cómo usar:**

```bash
# 1. Obtener token
TOKEN=$(curl -s -X POST "localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  jq -r '.access_token')

# 2. Usar en requests
curl -H "Authorization: Bearer $TOKEN" \
  "localhost:8001/api/restaurantes"

# 3. Verificar permisos
curl -H "Authorization: Bearer $TOKEN" \
  "localhost:8001/auth/whoami"
```

### 🎖️ **Características destacadas:**

- **Stateless**: No sesiones server-side
- **Escalable**: Compatible con microservicios  
- **Seguro**: Tokens con expiración automática
- **Flexible**: Sistema de roles extensible
- **Production-ready**: Manejo completo de errores

---

## 📚 Referencias Adicionales

- [Flask-JWT-Extended Docs](https://flask-jwt-extended.readthedocs.io/)
- [JWT.io](https://jwt.io/) - Decodificador de tokens
- [RFC 7519](https://tools.ietf.org/html/rfc7519) - Especificación JWT oficial
- [OWASP JWT Security](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

---

**🎉 ¡Tu API REST con autenticación JWT está completa y lista para producción!**

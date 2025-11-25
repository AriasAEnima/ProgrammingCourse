# Configuración de MongoDB para Flask App

## 1. Instalar MongoDB Community Server

### Para Windows:

1. Descarga MongoDB Community Server desde: https://www.mongodb.com/try/download/community
2. Ejecuta el instalador como administrador
3. Durante la instalación:
   - Selecciona "Complete" setup
   - Marca "Install MongoDB as a Service"
   - Marca "Install MongoDB Compass" (GUI opcional)
4. MongoDB se iniciará automáticamente como servicio de Windows

### Verificar instalación:

```powershell
# Verificar que MongoDB está corriendo
Get-Service MongoDB

# O conectar con mongosh
mongosh
```

## 2. Configuración por defecto

- **Puerto**: 27017
- **Host**: localhost
- **URI de conexión**: `mongodb://localhost:27017/`

## 3. Configurar variables de entorno (opcional)

Puedes configurar estas variables en tu sistema:

```powershell
# En PowerShell (temporal)
$env:MONGO_URI = "mongodb://localhost:27017/"
$env:DATABASE_NAME = "flask_app"

# Para hacerlo permanente, usar setx:
setx MONGO_URI "mongodb://localhost:27017/"
setx DATABASE_NAME "flask_app"
```

## 4. Estructura de la base de datos

La aplicación creará automáticamente:

### Base de datos: `flask_app`

#### Colección: `users`
```json
{
  "user_id": "user-1",
  "username": "admin1",
  "password_hash": "hash_de_la_contraseña",
  "role": "admin",
  "created_at": "2024-01-15T11:00:00Z"
}
```

#### Colección: `desks`
```json
{
  "desk_id": 1,
  "name": "Mesa Venture",
  "width": 125,
  "height": 225
}
```

## 5. Uso de MongoDB Compass (GUI)

1. Abre MongoDB Compass
2. Conecta a: `mongodb://localhost:27017`
3. Explora las colecciones `users` y `desks` en la base de datos `flask_app`

## 6. Comandos útiles con mongosh

```javascript
// Conectar a la base de datos
use flask_app

// Ver todas las colecciones
show collections

// Ver usuarios
db.users.find().pretty()

// Ver escritorios
db.desks.find().pretty()

// Agregar un usuario manualmente
db.users.insertOne({
  "user_id": "user-3",
  "username": "editor",
  "password_hash": "hash_aquí",
  "role": "editor",
  "created_at": new Date()
})
```

## 6. Dependencia completa de MongoDB

⚠️  **IMPORTANTE**: La aplicación requiere MongoDB para funcionar. 

Si MongoDB no está disponible:
- Los endpoints retornarán error 503 (Service Unavailable)
- Verás mensajes de error en la consola: "❌ Error conectando a MongoDB: ..."
- **La aplicación NO funcionará** sin una conexión válida a MongoDB
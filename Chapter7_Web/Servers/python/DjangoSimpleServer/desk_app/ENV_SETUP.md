# 🔐 Configuración del Archivo .env

El archivo `.env` contiene las credenciales para conectarse a MongoDB. Este archivo **NO debe subirse a Git** (ya está en `.gitignore`).

## 📝 Crear el Archivo .env

### Opción 1: Crear Manualmente

**En cualquier sistema operativo:**

1. Navega al directorio `desk_app/`
2. Crea un archivo llamado `.env` (con el punto al inicio)
3. Copia y pega el contenido según tu configuración:

### Opción 2: Copiar desde el Ejemplo

Existe un archivo `.env.example` que puedes usar como plantilla (puedes crearlo manualmente si no existe).

## 📋 Configuraciones

### Configuración A: MongoDB Local SIN Autenticación

Este es el método más simple para desarrollo local.

```env
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=desk_database
MONGODB_USERNAME=
MONGODB_PASSWORD=
```

### Configuración B: MongoDB Local CON Autenticación

Si configuraste MongoDB con usuario y contraseña:

```env
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=desk_database
MONGODB_USERNAME=mi_usuario
MONGODB_PASSWORD=mi_contraseña_segura
```

### Configuración C: MongoDB Atlas (Cloud)

Si usas MongoDB en la nube:

```env
MONGODB_URI=mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/desk_database?retryWrites=true&w=majority
```

**⚠️ Importante:** Reemplaza:
- `usuario`: Tu usuario de MongoDB Atlas
- `password`: Tu contraseña de MongoDB Atlas
- `cluster0.xxxxx`: Tu cluster ID de MongoDB Atlas
- `desk_database`: El nombre de tu base de datos

## 🔍 Verificar Configuración

Después de crear tu archivo `.env`, verifica que funcione:

```bash
python manage.py shell
```

Luego en la consola de Python:

```python
from desk.models import Desk
print("✅ Conexión exitosa!")
print(f"Mesas en DB: {Desk.objects.count()}")
```

Si ves "✅ Conexión exitosa!", tu configuración está correcta.

## 🚨 Seguridad

- **NUNCA** compartas tu archivo `.env`
- **NUNCA** subas tu archivo `.env` a Git
- **NUNCA** pongas credenciales reales en el archivo `.env.example`
- Usa contraseñas fuertes para producción
- En producción, usa variables de entorno del sistema en lugar de archivos `.env`

## 🐛 Problemas Comunes

### Error: "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### Error: "Connection refused"
MongoDB no está ejecutándose. Inicia MongoDB:
- **macOS**: `brew services start mongodb-community`
- **Linux**: `sudo systemctl start mongodb`
- **Windows**: `net start MongoDB`

### Error: "Authentication failed"
Tu usuario/contraseña es incorrecto. Verifica:
1. Que el usuario existe en MongoDB
2. Que la contraseña es correcta
3. Que el usuario tiene permisos en la base de datos

### MongoDB Atlas: "IP not whitelisted"
En MongoDB Atlas:
1. Ve a "Network Access"
2. Agrega tu IP o permite todas las IPs (0.0.0.0/0) para desarrollo

## 📚 Variables de Entorno Disponibles

| Variable | Descripción | Requerido | Default |
|----------|-------------|-----------|---------|
| `MONGODB_URI` | Connection string completo (prioridad sobre las demás) | No | - |
| `MONGODB_HOST` | Host de MongoDB | Si no hay URI | localhost |
| `MONGODB_PORT` | Puerto de MongoDB | Si no hay URI | 27017 |
| `MONGODB_DB` | Nombre de la base de datos | Si no hay URI | desk_database |
| `MONGODB_USERNAME` | Usuario (opcional) | No | - |
| `MONGODB_PASSWORD` | Contraseña (opcional) | No | - |

## ✅ Ejemplo Completo

Contenido de un archivo `.env` funcional:

```env
# MongoDB Configuration para desarrollo local
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=desk_database
MONGODB_USERNAME=
MONGODB_PASSWORD=

# Descomenta la siguiente línea si usas MongoDB Atlas:
# MONGODB_URI=mongodb+srv://miusuario:mipassword@cluster0.abc123.mongodb.net/desk_database?retryWrites=true&w=majority
```


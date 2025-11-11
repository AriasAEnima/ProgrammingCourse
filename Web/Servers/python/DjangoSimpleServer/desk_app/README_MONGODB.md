# Integración con MongoDB

Este proyecto Django utiliza MongoDB para almacenar y gestionar las mesas (desks).

## 📋 Requisitos Previos

1. **Python 3.8+**
2. **MongoDB instalado y en ejecución**
   - Para instalar MongoDB localmente:
     - **macOS**: `brew install mongodb-community`
     - **Ubuntu/Debian**: `sudo apt-get install mongodb`
     - **Windows**: Descarga desde [mongodb.com](https://www.mongodb.com/try/download/community)
   - O usar **MongoDB Atlas** (cloud gratuito): [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

## 🚀 Configuración

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Las nuevas dependencias incluyen:
- `pymongo`: Cliente oficial de MongoDB para Python
- `mongoengine`: ODM (Object Document Mapper) para MongoDB
- `python-dotenv`: Para cargar variables de entorno desde archivo `.env`

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en el directorio `desk_app/`:

```bash
cd desk_app
touch .env
```

**Opción A: MongoDB Local (sin autenticación)**

```env
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=desk_database
MONGODB_USERNAME=
MONGODB_PASSWORD=
```

**Opción B: MongoDB Local (con autenticación)**

```env
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=desk_database
MONGODB_USERNAME=tu_usuario
MONGODB_PASSWORD=tu_contraseña
```

**Opción C: MongoDB Atlas (Cloud)**

```env
MONGODB_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/desk_database?retryWrites=true&w=majority
```

### 3. Iniciar MongoDB

**Para MongoDB local:**

```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongodb

# Windows
net start MongoDB
```

**Para MongoDB Atlas:**
- Crea una cuenta en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Crea un cluster gratuito
- Obtén tu connection string
- Agrégalo a tu archivo `.env` como `MONGODB_URI`

### 4. Iniciar el Servidor Django

```bash
python manage.py runserver
```

## 📝 Modelo de Datos

El modelo `Desk` tiene los siguientes campos:

```python
class Desk(Document):
    name = StringField(required=True, max_length=100)
    width = IntField(required=True, min_value=0)
    height = IntField(required=True, min_value=0)
```

## 🔌 API Endpoints

### 1. Crear una Mesa (POST)

```bash
curl -X POST http://localhost:8000/api/desk/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mesa Venture",
    "width": 125,
    "height": 225
  }'
```

**Respuesta:**
```json
{
  "desk_id": "673a2f1b8e4d2a1c3b5e6f7a",
  "name": "Mesa Venture",
  "width": 125,
  "height": 225
}
```

### 2. Obtener Todas las Mesas (GET)

```bash
curl http://localhost:8000/api/desk/all
```

**Respuesta:**
```json
[
  {
    "desk_id": "673a2f1b8e4d2a1c3b5e6f7a",
    "name": "Mesa Venture",
    "width": 125,
    "height": 225
  },
  {
    "desk_id": "673a2f1b8e4d2a1c3b5e6f7b",
    "name": "Mesa Koto",
    "width": 200,
    "height": 223
  }
]
```

### 3. Obtener una Mesa por ID (GET)

```bash
curl http://localhost:8000/api/desk/673a2f1b8e4d2a1c3b5e6f7a
```

**Respuesta:**
```json
{
  "desk_id": "673a2f1b8e4d2a1c3b5e6f7a",
  "name": "Mesa Venture",
  "width": 125,
  "height": 225
}
```

### 4. Actualizar una Mesa (PUT)

```bash
curl -X PUT http://localhost:8000/api/desk/673a2f1b8e4d2a1c3b5e6f7a \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mesa Venture XL",
    "width": 150,
    "height": 250
  }'
```

**Respuesta:**
```json
{
  "desk_id": "673a2f1b8e4d2a1c3b5e6f7a",
  "name": "Mesa Venture XL",
  "width": 150,
  "height": 250
}
```

### 5. Eliminar una Mesa (DELETE)

```bash
curl -X DELETE http://localhost:8000/api/desk/673a2f1b8e4d2a1c3b5e6f7a
```

**Respuesta:**
```json
{
  "message": "Mesa 673a2f1b8e4d2a1c3b5e6f7a eliminada exitosamente"
}
```

## 🧪 Script para Poblar la Base de Datos

Puedes usar el siguiente script para agregar datos de ejemplo:

```python
# En la consola de Django (python manage.py shell)
from desk.models import Desk

# Limpiar la colección
Desk.objects.delete()

# Crear mesas de ejemplo
desks_data = [
    {"name": "Mesa Venture", "width": 125, "height": 225},
    {"name": "Mesa Koto", "width": 200, "height": 223},
    {"name": "Mesa Amatista", "width": 200, "height": 300},
]

for desk_data in desks_data:
    desk = Desk(**desk_data)
    desk.save()
    print(f"Mesa creada: {desk.name} (ID: {desk.id})")
```

O crea un archivo `seed_db.py` (ver abajo).

## 🔍 Verificar la Conexión a MongoDB

Para verificar que la conexión a MongoDB funciona correctamente:

```bash
python manage.py shell
```

```python
from desk.models import Desk

# Crear una mesa de prueba
desk = Desk(name="Mesa Test", width=100, height=200)
desk.save()

# Verificar que se guardó
print(Desk.objects.all())

# Limpiar
desk.delete()
```

## 🛠️ Troubleshooting

### Error: "Connection refused"
- Verifica que MongoDB esté ejecutándose: `brew services list` (macOS) o `sudo systemctl status mongodb` (Linux)
- Verifica el puerto: MongoDB usa el puerto `27017` por defecto

### Error: "Authentication failed"
- Verifica que tu usuario y contraseña sean correctos en el archivo `.env`
- Verifica que el usuario tenga permisos en la base de datos

### Error: "ModuleNotFoundError: No module named 'mongoengine'"
- Instala las dependencias: `pip install -r requirements.txt`

## 📚 Recursos Adicionales

- [Documentación de MongoDB](https://docs.mongodb.com/)
- [Documentación de MongoEngine](http://docs.mongoengine.org/)
- [Django REST Framework](https://www.django-rest-framework.org/)


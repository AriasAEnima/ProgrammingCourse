# 🚀 Inicio Rápido - MongoDB + Django

## 1️⃣ Instalar MongoDB

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**Windows:**
Descarga desde [mongodb.com](https://www.mongodb.com/try/download/community) e instala.

**O usa MongoDB Atlas (Cloud):**
- Crea cuenta gratis en [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
- Crea un cluster
- Obtén tu connection string

## 2️⃣ Instalar Dependencias

```bash
pip install -r ../requirements.txt
```

## 3️⃣ Crear Archivo .env

Crea un archivo `.env` en el directorio `desk_app/`:

```bash
# Para MongoDB local
cat > .env << 'EOF'
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=desk_database
MONGODB_USERNAME=
MONGODB_PASSWORD=
EOF
```

Si usas MongoDB Atlas, crea el archivo así:

```bash
cat > .env << 'EOF'
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/desk_database?retryWrites=true&w=majority
EOF
```

Reemplaza `usuario`, `password` y `cluster` con tus credenciales reales.

## 4️⃣ Poblar Base de Datos (Opcional)

```bash
python seed_db.py
```

## 5️⃣ Iniciar Servidor

```bash
python manage.py runserver
```

## 6️⃣ Probar API

**Crear una mesa:**
```bash
curl -X POST http://localhost:8000/api/desk/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Mesa Test", "width": 100, "height": 200}'
```

**Ver todas las mesas:**
```bash
curl http://localhost:8000/api/desk/all
```

## 🎉 ¡Listo!

Para más detalles, consulta [README_MONGODB.md](./README_MONGODB.md)


# 🔌 Conexión Django → MongoDB: ¿Cuándo usar qué?

## 🤔 La Pregunta Importante

Cuando tu aplicación Django corre en Docker, **¿cómo se conecta a MongoDB?**

La respuesta depende de **DÓNDE está MongoDB**.

---

## 📊 Tres Escenarios

### Escenario 1: MongoDB en tu PC (FUERA de Docker)

```
┌──────────────────────────┐
│   Tu PC (Windows)        │
│                          │
│  ┌─────────────┐         │
│  │  MongoDB    │ ← Puerto 27017
│  └─────────────┘         │
│         ↑                │
│         │ host.docker.internal
│         │                │
│  ┌─────────────┐         │
│  │  Container  │         │
│  │  Django     │         │
│  └─────────────┘         │
└──────────────────────────┘
```

**Usar:**
```bash
-e MONGODB_HOST=host.docker.internal
```

**¿Por qué?**  
`host.docker.internal` es una dirección especial que Docker traduce a la IP de tu máquina host.

**Comando:**
```bash
docker run -p 8000:8000 \
  -e MONGODB_HOST=host.docker.internal \
  -e MONGODB_PORT=27017 \
  desk-api
```

---

### Escenario 2: MongoDB DENTRO de Docker (Mismo Ecosistema)

```
┌──────────────────────────────────┐
│   Docker Network: desk-network   │
│                                  │
│  ┌──────────────┐                │
│  │  Container   │                │
│  │  "mongodb"   │ ← nombre       │
│  │  MongoDB     │                │
│  └──────────────┘                │
│         ↑                        │
│         │ nombre del contenedor  │
│         │                        │
│  ┌──────────────┐                │
│  │  Container   │                │
│  │  Django      │                │
│  └──────────────┘                │
└──────────────────────────────────┘
```

**Usar:**
```bash
-e MONGODB_HOST=mongodb
```

**¿Por qué?**  
Dentro de la misma red Docker, los contenedores se pueden contactar por su **nombre**.

**Comandos:**
```bash
# 1. Crear red
docker network create desk-network

# 2. Iniciar MongoDB
docker run -d --name mongodb-app --network desk-network desk-mongodb

# 3. Iniciar Django (apunta al nombre "mongodb")
docker run -p 8000:8000 --network desk-network  -e MONGO_HOST=mongodb-app desk-api
```

---

### Escenario 3: MongoDB Atlas (Cloud)

```
┌──────────────────────┐           ☁️ Internet ☁️
│   Tu PC              │                │
│                      │                │
│  ┌────────────┐      │                │
│  │ Container  │ ─────┼────────────────┤
│  │ Django     │      │                │
│  └────────────┘      │          ┌─────────────┐
│                      │          │ MongoDB     │
└──────────────────────┘          │ Atlas       │
                                  └─────────────┘
```

**Usar:**
```bash
-e MONGODB_URI="mongodb+srv://usuario:password@cluster.mongodb.net/desk_database"
```

**¿Por qué?**  
MongoDB Atlas usa un connection string completo.

**Comando:**
```bash
docker run -p 8000:8000 \
  -e MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/desk_database" \
  desk-api
```

---

## 🎯 Tabla Resumen

| Ubicación MongoDB | Variable a usar | Valor |
|-------------------|----------------|-------|
| **Tu PC (local)** | `MONGODB_HOST` | `host.docker.internal` |
| **Otro contenedor Docker** | `MONGODB_HOST` | Nombre del contenedor (ej: `mongodb`) |
| **Cloud (Atlas)** | `MONGODB_URI` | Connection string completo |

---

## 🔍 ¿Cómo Funciona Internamente?

### Con `host.docker.internal`:

```python
# Django en Docker intenta conectarse a:
# host.docker.internal:27017

# Docker traduce internamente:
host.docker.internal → 192.168.65.2 (IP de tu PC)

# Resultado:
# Django se conecta a MongoDB en tu PC
```

### Con nombre de contenedor:

```python
# Django en Docker intenta conectarse a:
# mongodb:27017

# Docker hace DNS lookup dentro de la red:
mongodb → 172.18.0.2 (IP del contenedor MongoDB)

# Resultado:
# Django se conecta al otro contenedor
```

---

## 🐛 Errores Comunes

### Error: "Connection refused" con `host.docker.internal`

**Causa:** MongoDB no está corriendo en tu PC.

**Solución:**
```bash
# Windows: Abrir Services → Iniciar MongoDB
# Mac: brew services start mongodb-community
```

---

### Error: "Name or service not known" con `mongodb`

**Causa:** Los contenedores no están en la misma red.

**Solución:**
```bash
# Verificar que ambos estén en la misma red
docker network inspect desk-network

# Deberías ver ambos contenedores listados
```

---

### Error: `host.docker.internal` no funciona en Linux

**Causa:** Linux no incluye `host.docker.internal` por defecto.

**Solución:**
```bash
docker run -p 8000:8000 \
  --add-host=host.docker.internal:host-gateway \
  -e MONGODB_HOST=host.docker.internal \
  desk-api
```

---

## 💡 Mejores Prácticas

### Para Desarrollo:
- ✅ MongoDB local + `host.docker.internal` (más simple)
- ✅ O ambos en Docker con red compartida (más aislado)

### Para Producción:
- ✅ MongoDB Atlas + connection string (más robusto)
- ✅ O servicio gestionado de tu cloud provider

---

## 🧪 Probar tu Conexión

### Desde fuera del contenedor:
```bash
# Ver logs para verificar conexión
docker logs desk-api

# Deberías ver:
# "Starting development server at http://0.0.0.0:8000/"
# Sin errores de conexión a MongoDB
```

### Desde dentro del contenedor:
```bash
# Entrar al contenedor
docker exec -it desk-api bash

# Probar conexión a MongoDB
python desk_app/manage.py shell

# En el shell de Python:
from desk.models import Desk
print(Desk.objects.count())  # Si funciona, está conectado!
```

---

## 📚 Recursos

- [Docker Networking](https://docs.docker.com/network/)
- [host.docker.internal](https://docs.docker.com/desktop/networking/#use-cases-and-workarounds)
- [MongoDB Connection Strings](https://www.mongodb.com/docs/manual/reference/connection-string/)


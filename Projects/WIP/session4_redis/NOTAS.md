# 🔴 Sesión 4: Redis - NOTAS

## ⚠️ Prerequisito: Redis con Docker

**IMPORTANTE:** Abre Docker Desktop primero y espera a que inicie completamente.

### Comandos de Docker (funcionan en Windows, macOS, Linux):

```bash
# 1. Iniciar Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 2. Verificar que funciona
docker exec redis redis-cli ping
# Debe responder: PONG

# 3. Ver logs (opcional)
docker logs redis

# 4. Detener cuando termines
docker stop redis
docker rm redis
```

**Si ya existe un contenedor "redis":**
```bash
# Limpiar y empezar de nuevo
docker stop redis
docker rm redis
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

---

## 🎯 Cómo Ejecutar los Demos

### 1. Activar entorno

**Windows:**
```cmd
cd session4_redis
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd session4_redis
source venv/bin/activate
```

### 2. Verificar Redis

```bash
docker exec redis redis-cli ping
# Debe responder: PONG
```

Si no responde, revisa los comandos de arriba.

### 3. Ejecutar demos

```bash
python demos/demo_redis_basic.py
python demos/demo_distributed_workers.py
```

# Demo distribuido
python demos/demo_distributed_workers.py
```

---

## 📚 Contenido de la Sesión

### Código Implementado:

✅ `workers/redis_task_queue.py` - Cola distribuida en Redis  
✅ `workers/redis_worker.py` - Worker que procesa desde Redis  
✅ `demos/demo_redis_basic.py` - Demo con 3 tareas  
✅ `demos/demo_distributed_workers.py` - 3 workers, 15 tareas  

### Conceptos:

- Redis como cola persistente y distribuida
- Operaciones atómicas (RPOPLPUSH)
- Multiprocessing para evitar GIL
- Persistencia de tareas y resultados
- Monitoreo con redis-cli

---

## 🔧 Comandos Útiles de Redis

Todos estos comandos usan `docker exec` (funcionan igual en Windows, macOS, Linux):

```bash
# Ver todas las keys
docker exec redis redis-cli KEYS "*"

# Ver tareas pendientes
docker exec redis redis-cli LRANGE image_processing:pending 0 -1

# Ver tareas completadas
docker exec redis redis-cli LRANGE image_processing:completed 0 -1

# Limpiar todo
docker exec redis redis-cli FLUSHDB

# Monitorear en tiempo real
docker exec -it redis redis-cli MONITOR

# Entrar a la consola interactiva de Redis
docker exec -it redis redis-cli
```

---

## ✅ Estado

**Sesión 4:** ✅ Código completo y listo para ejecutar  
**Requisito:** Redis debe estar corriendo

Cuando tengas Redis corriendo, ejecuta los demos! 🚀


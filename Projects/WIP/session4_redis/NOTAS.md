# 🔴 Sesión 4: Redis - NOTAS

## ⚠️ Prerequisito: Redis debe estar corriendo

Para ejecutar los demos de esta sesión, necesitas tener Redis instalado y corriendo.

### Opción 1: Docker (Recomendado) ✅

```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

Verificar:
```bash
docker ps | grep redis
redis-cli ping  # Debe responder: PONG
```

Detener cuando termines:
```bash
docker stop redis
docker rm redis
```

### Opción 2: Instalación Local

**macOS:**
```bash
brew install redis
redis-server &
```

**Linux:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

**Verificar:**
```bash
redis-cli ping  # Debe responder: PONG
```

---

## 🎯 Cómo Ejecutar los Demos

### 1. Activar entorno

```bash
cd session4_redis
source venv/bin/activate  # Ya instalado
```

### 2. Verificar Redis

```bash
redis-cli ping
```

Si no responde "PONG", sigue las instrucciones arriba.

### 3. Ejecutar demos

```bash
# Demo básico
python demos/demo_redis_basic.py

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

```bash
# Ver todas las keys
redis-cli KEYS "*"

# Ver tareas pendientes
redis-cli LRANGE image_processing:pending 0 -1

# Ver tareas completadas
redis-cli LRANGE image_processing:completed 0 -1

# Limpiar todo
redis-cli FLUSHDB

# Monitorear en tiempo real
redis-cli MONITOR
```

---

## ✅ Estado

**Sesión 4:** ✅ Código completo y listo para ejecutar  
**Requisito:** Redis debe estar corriendo

Cuando tengas Redis corriendo, ejecuta los demos! 🚀


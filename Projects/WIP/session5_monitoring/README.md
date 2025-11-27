# 🔍 Sesión 5: Health Checks, Auto-Recovery y Monitoring

## ✅ Estado: COMPLETADA Y VERIFICADA

**Todos los demos probados y funcionando al 100%** ✨

## ⚠️ Setup Rápido

### 1. Iniciar Redis

```bash
# Abre Docker Desktop primero, luego:
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Verificar
docker exec redis redis-cli ping  # Debe responder: PONG
```

### 2. Instalar dependencias

```bash
cd session5_monitoring
python3 -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Ejecutar demos

```bash
python demos/demo_worker_registry.py      # Demo 1: Worker Registry
python demos/demo_auto_recovery.py        # Demo 2: Auto-Recovery y DLQ
python demos/demo_monitored_system.py     # Demo 3: Sistema completo
```

**Detener Redis cuando termines:**
```bash
docker stop redis && docker rm redis
```

---

## 📂 Estructura del Proyecto

```
session5_monitoring/
├── requirements.txt
├── README.md
│
├── filters/                      # Filtros (de Sesión 2)
│   ├── __init__.py
│   ├── base_filter.py
│   ├── blur_filter.py
│   ├── brightness_filter.py
│   ├── edges_filter.py
│   └── grayscale_filter.py
│
├── core/                         # Pipeline (de Sesión 2)
│   ├── __init__.py
│   ├── filter_pipeline.py
│   ├── filter_factory.py
│   └── batch_processor.py
│
├── workers/                      # 🆕 Workers con Monitoring
│   ├── __init__.py
│   ├── worker_registry.py        # 🆕 Registro de workers
│   ├── redis_task_queue_v2.py    # 🆕 Cola con auto-recovery
│   └── monitored_redis_worker.py # 🆕 Worker con heartbeats
│
├── demos/
│   ├── demo_worker_registry.py         # Demo 1: Registry
│   ├── demo_auto_recovery.py           # Demo 2: Reintentos y DLQ
│   └── demo_monitored_system.py        # Demo 3: Sistema completo
│
├── images/
│   └── sample.jpg
│
└── output/
```

---

## 🆕 ¿Qué hay de nuevo en Sesión 5?

### Comparación con Sesión 4

| Característica | Sesión 4 (Redis Básico) | Sesión 5 (Monitoring) |
|----------------|-------------------------|----------------------|
| **Worker Registry** | ❌ No | ✅ Registry centralizado |
| **Heartbeats** | ❌ No | ✅ Workers reportan salud |
| **Auto-recovery** | ❌ Manual | ✅ Reintentos automáticos |
| **Dead Letter Queue** | ❌ No | ✅ Para tareas irrecuperables |
| **Graceful Shutdown** | ⚠️ Básico | ✅ Signal handlers |
| **Stuck Task Recovery** | ❌ No | ✅ Detecta tareas atascadas |

---

## 🧩 Componentes Principales

### 1. WorkerRegistry

**Propósito:** Registro centralizado de workers activos en Redis.

**Funcionalidades:**
- Registrar/des-registrar workers
- Enviar heartbeats periódicos
- Detectar workers muertos (sin heartbeat)
- Limpiar workers muertos automáticamente

**Uso básico:**

```python
from workers import WorkerRegistry

registry = WorkerRegistry(heartbeat_timeout=30)

# Registrar worker
registry.register_worker("worker-1", metadata={"hostname": "server-1"})

# Enviar heartbeat
registry.send_heartbeat("worker-1")

# Ver workers activos
active = registry.get_active_workers()
for worker in active:
    print(f"{worker['worker_id']}: alive={worker['is_alive']}")

# Limpiar workers muertos
registry.cleanup_dead_workers()
```

**Almacenamiento en Redis:**
```
worker_registry:workers:worker-1
  worker_id: worker-1
  registered_at: 2024-01-15T10:30:00
  last_heartbeat: 1705318200.5
  status: active
  hostname: server-1
```

---

### 2. RedisTaskQueueV2

**Propósito:** Cola de tareas con auto-recovery y Dead Letter Queue.

**Mejoras respecto a Sesión 4:**
- ✅ **Reintentos automáticos**: Tareas fallidas se reintentan hasta `max_retries`
- ✅ **Dead Letter Queue (DLQ)**: Tareas con demasiados fallos van a DLQ
- ✅ **Contador de reintentos**: Cada tarea sabe cuántas veces ha fallado
- ✅ **Recuperación de tareas atascadas**: Detecta tareas sin progreso por timeout

**Estados de tareas:**

```
pending → processing → completed  ✅
    ↓                    ↓
  failed (retry)       dead (DLQ) 💀
    ↓
  pending (retry)
```

**Uso básico:**

```python
from workers import RedisTaskQueueV2

queue = RedisTaskQueueV2(max_retries=3)

# Agregar tarea
task_id = queue.add_task({
    "input_path": "images/sample.jpg",
    "output_path": "output/result.jpg"
})

# Worker procesa tarea
task = queue.get_task("worker-1")

# Si falla, se reintenta automáticamente
queue.mark_failed(task_id, "Error de red")  # retry_count++

# Después de 3 fallos → DLQ
dlq_tasks = queue.get_dead_letter_tasks()

# Recuperar tareas atascadas (sin progreso por 5min)
recovered = queue.recover_stuck_tasks()
```

**Almacenamiento en Redis:**
```
# Cola de tareas
image_processing_v2:pending       → [task-1, task-2]
image_processing_v2:processing    → [task-3]
image_processing_v2:completed     → [task-4, task-5]
image_processing_v2:dead_letter   → [task-6]  💀

# Metadata de tarea
task:task-1
  task_id: task-1
  data: {"input_path": "...", ...}
  status: pending
  retry_count: 2
  last_error: "Connection timeout"
  created_at: 2024-01-15T10:30:00
```

---

### 3. MonitoredRedisWorker

**Propósito:** Worker que procesa tareas y reporta su salud.

**Características:**
- ✅ Se registra en `WorkerRegistry` al iniciar
- ✅ Envía heartbeats periódicos (cada 10s por defecto)
- ✅ Maneja señales de interrupción (Ctrl+C, SIGTERM)
- ✅ Graceful shutdown (se des-registra antes de cerrar)
- ✅ Logging estructurado

**Uso básico:**

```python
from workers import MonitoredRedisWorker

worker = MonitoredRedisWorker(
    worker_id="worker-1",
    heartbeat_interval=10  # Heartbeat cada 10s
)

worker.start()  # Bloquea hasta que se detenga
```

**Flujo del worker:**

```
1. Registrar en WorkerRegistry
2. Loop:
   a. Enviar heartbeat si es necesario
   b. Obtener tarea de la cola (timeout=5s)
   c. Procesar tarea
   d. Marcar como completed/failed
3. Graceful shutdown:
   a. Des-registrar del registry
   b. Mostrar estadísticas
```

---

## 🎯 Demos Explicados

### Demo 1: Worker Registry

**Qué hace:**
- Registra 3 workers
- Envía heartbeats para 2 de ellos
- Detecta que 1 worker murió (sin heartbeat)
- Limpia workers muertos

**Ejecutar:**
```bash
python demos/demo_worker_registry.py
```

**Salida esperada:**
```
✅ Worker registrado: worker-1
✅ Worker registrado: worker-2
✅ Worker registrado: worker-3
💓 Heartbeat enviado (worker-1, worker-2)
💀 Detectando workers muertos...
  - worker-3: muerto hace 12s
🧹 Limpiados 1 worker(s) muerto(s)
```

---

### Demo 2: Auto-Recovery

**Qué hace:**
- Agrega 3 tareas a la cola
- Simula que una tarea falla 4 veces
- Después de 3 reintentos → DLQ
- Reintenta manualmente desde DLQ
- Completa todas las tareas

**Ejecutar:**
```bash
python demos/demo_auto_recovery.py
```

**Salida esperada:**
```
📥 Agregando 3 tareas...
💥 Simulando fallos en task1...
  Intento 1 (retry=0)
  ⚠️  Tarea fallida (reintento 1/3)
  Intento 2 (retry=1)
  ⚠️  Tarea fallida (reintento 2/3)
  Intento 3 (retry=2)
  ⚠️  Tarea fallida (reintento 3/3)
  Intento 4 (retry=3)
  💀 Tarea en DLQ (reintentos agotados)

📊 Estadísticas:
  dead_letter: 1 💀

🔄 Reintentando tarea desde DLQ...
✅ Completadas: 3
```

---

### Demo 3: Sistema Completo con Monitoring

**Qué hace:**
- Agrega 10 tareas a la cola
- Lanza 3 workers monitoreados (multiprocessing)
- Monitorea progreso en tiempo real
- Muestra workers activos y heartbeats
- Detiene workers limpiamente

**Ejecutar:**
```bash
python demos/demo_monitored_system.py
```

**Salida esperada:**
```
📥 Agregando 10 tareas a la cola...
🚀 Lanzando 3 workers monitoreados...

📊 Monitoreando progreso...
⏱️  0s | Workers activos: 3 | Pending: 10 | Processing: 2 | Completed: 0
   - monitored-worker-1: heartbeat hace 2.1s
   - monitored-worker-2: heartbeat hace 1.8s
   - monitored-worker-3: heartbeat hace 1.5s

⏱️  3s | Workers activos: 3 | Pending: 5 | Processing: 3 | Completed: 2
   - monitored-worker-1: heartbeat hace 0.3s
   - monitored-worker-2: heartbeat hace 0.5s
   - monitored-worker-3: heartbeat hace 0.8s

✅ Todas las tareas completadas!

📊 Estadísticas finales:
  Completadas: 10
  Tiempo total: 12.45s
```

---

## 💡 Conceptos Clave

### 1. Heartbeat

**¿Qué es?**
Señal periódica que un worker envía para indicar que está vivo.

**¿Por qué es importante?**
- Detectar workers que crashearon
- Saber cuántos workers están activos
- Tomar decisiones de escalado

**Implementación:**
```python
# Worker envía heartbeat cada 10s
while running:
    if time.time() - last_heartbeat >= heartbeat_interval:
        registry.send_heartbeat(worker_id)
        last_heartbeat = time.time()
```

---

### 2. Dead Letter Queue (DLQ)

**¿Qué es?**
Cola especial para tareas que fallaron demasiadas veces.

**¿Por qué es útil?**
- Evita reintentar indefinidamente
- Permite inspección manual de fallos
- Libera la cola principal de tareas problemáticas

**Cuándo usar:**
- Errores de validación (input inválido)
- Recursos no encontrados
- Errores de lógica (no de infraestructura)

**Cuándo NO usar:**
- Errores temporales de red
- Timeouts ocasionales
- Falta temporal de recursos

---

### 3. Auto-Recovery

**¿Qué es?**
Mecanismo para reintentar tareas fallidas automáticamente.

**Estrategias:**
- **Reintentos inmediatos**: Volver a encolar enseguida
- **Exponential backoff**: Esperar más tiempo entre reintentos
- **Dead Letter Queue**: Límite de reintentos

**Implementación en esta sesión:**
```python
def mark_failed(task_id, error):
    retry_count += 1
    
    if retry_count < max_retries:
        # Reintentar: volver a pending
        redis.rpush(pending_key, task_id)
    else:
        # Dead Letter Queue
        redis.rpush(dead_letter_key, task_id)
```

---

### 4. Graceful Shutdown

**¿Qué es?**
Cerrar un worker limpiamente, terminando tareas en progreso.

**Pasos:**
1. Recibir señal de interrupción (SIGINT, SIGTERM)
2. Detener de aceptar nuevas tareas
3. Terminar tarea actual
4. Des-registrar del registry
5. Cerrar conexiones
6. Salir

**Implementación:**
```python
signal.signal(signal.SIGINT, self._signal_handler)

def _signal_handler(self, signum, frame):
    self.running = False  # Detener loop

def _shutdown(self):
    registry.unregister_worker(self.worker_id)
    # Limpiar recursos...
```

---

### 5. Stuck Task Recovery

**¿Qué es?**
Detectar tareas que llevan demasiado tiempo en "processing" sin completarse.

**Causas comunes:**
- Worker crasheó sin marcar la tarea como fallida
- Worker perdió conexión a Redis
- Worker está colgado (deadlock, loop infinito)

**Solución:**
```python
def recover_stuck_tasks(self):
    for task_id in processing_queue:
        if task["started_at"] + timeout < now:
            # Tarea atascada: mover a pending
            mark_failed(task_id, "Timeout")
```

---

## 🧹 Limpieza y Mantenimiento

### Limpiar todas las tareas

```bash
docker exec redis redis-cli FLUSHDB
```

O desde Python:
```python
queue = RedisTaskQueueV2()
queue.clear()

registry = WorkerRegistry()
registry.clear()
```

### Inspeccionar Dead Letter Queue

```python
from workers import RedisTaskQueueV2

queue = RedisTaskQueueV2()
dlq_tasks = queue.get_dead_letter_tasks()

for task_id in dlq_tasks:
    print(f"Tarea muerta: {task_id}")
```

### Reintentar tareas de DLQ

```python
# Reintentar una tarea específica
queue.retry_dead_letter_task("task-123")

# O reintentar todas
for task_id in queue.get_dead_letter_tasks():
    queue.retry_dead_letter_task(task_id)
```

### Verificar workers activos

```python
from workers import WorkerRegistry

registry = WorkerRegistry()
active = registry.get_active_workers()

for worker in active:
    print(f"{worker['worker_id']}: "
          f"heartbeat hace {worker['time_since_heartbeat']}s")
```

---

## 🔧 Comandos Útiles de Redis

```bash
# Ver workers registrados
docker exec redis redis-cli KEYS "worker_registry:*"

# Ver info de un worker
docker exec redis redis-cli HGETALL "worker_registry:workers:worker-1"

# Ver tareas en DLQ
docker exec redis redis-cli LRANGE "image_processing_v2:dead_letter" 0 -1

# Ver info de una tarea
docker exec redis redis-cli HGETALL "task:task-123"

# Limpiar todo
docker exec redis redis-cli FLUSHDB
```

---

## 🐛 Troubleshooting

### Workers no se registran

**Problema:** Workers se lanzan pero no aparecen en el registry.

**Solución:**
1. Verificar que Redis esté corriendo:
   ```bash
   docker exec redis redis-cli ping
   ```

2. Verificar que el worker llama a `register_worker`:
   ```python
   registry.register_worker(worker_id)
   ```

---

### Workers aparecen como "muertos"

**Problema:** Workers activos aparecen como muertos en el registry.

**Causas:**
- Heartbeat interval muy largo
- Heartbeat timeout muy corto
- Worker no está enviando heartbeats

**Solución:**
```python
# Aumentar timeout o reducir interval
registry = WorkerRegistry(heartbeat_timeout=60)
worker = MonitoredRedisWorker(heartbeat_interval=10)
```

---

### Tareas van a DLQ demasiado rápido

**Problema:** Tareas fallidas van directo a DLQ sin reintentos.

**Solución:**
```python
# Aumentar max_retries
queue = RedisTaskQueueV2(max_retries=5)
```

---

### Workers no se detienen con Ctrl+C

**Problema:** Ctrl+C no detiene el worker limpiamente.

**Solución:**
Verificar que los signal handlers estén configurados:
```python
signal.signal(signal.SIGINT, self._signal_handler)
signal.signal(signal.SIGTERM, self._signal_handler)
```

---

## 📊 Comparación: Sesión 4 vs Sesión 5

### Sesión 4: Redis Básico

```python
# Workers independientes, sin coordinación
worker = RedisWorker("worker-1")
worker.start()

# No hay forma de saber:
# - ¿Cuántos workers están vivos?
# - ¿Qué worker está procesando qué tarea?
# - ¿Algún worker crasheó?
```

### Sesión 5: Monitoring Completo

```python
# Workers monitoreados, con coordinación
worker = MonitoredRedisWorker("worker-1")
worker.start()

# Ahora puedes:
# - Ver workers activos: registry.get_active_workers()
# - Detectar crashes: registry.get_dead_workers()
# - Rastrear tareas: queue.get_stats()
# - Reintentar fallos: automático
# - Inspeccionar DLQ: queue.get_dead_letter_tasks()
```

---

## 🎓 Ejercicios Propuestos

### Ejercicio 1: Exponential Backoff

Modificar `RedisTaskQueueV2` para que los reintentos usen exponential backoff:
- Reintento 1: inmediato
- Reintento 2: esperar 5s
- Reintento 3: esperar 10s
- Reintento 4: esperar 20s

**Pista:** Usar `time.sleep()` o un campo `retry_after` en la tarea.

---

### Ejercicio 2: Dashboard de Monitoring

Crear un script `dashboard.py` que muestre en tiempo real:
- Workers activos vs muertos
- Tareas pending/processing/completed/DLQ
- Throughput (tareas/segundo)
- Tasa de fallos

**Pista:** Usar un loop con `time.sleep(1)` y `\r` para actualizar la misma línea.

---

### Ejercicio 3: Alertas

Implementar sistema de alertas que detecte:
- Todos los workers están muertos
- DLQ tiene más de 10 tareas
- Tasa de fallos > 50%

**Pista:** Crear clase `AlertManager` que revise métricas periódicamente.

---

## 🚀 Próxima Sesión

**Sesión 6: Docker y Containerización**

Aprenderás a:
- Crear Dockerfile para workers
- Docker Compose para orquestar múltiples servicios
- Networking entre containers
- Volúmenes para persistencia

---

## 📚 Recursos Adicionales

- **Redis Commands:** https://redis.io/commands
- **Signal Handling en Python:** https://docs.python.org/3/library/signal.html
- **Multiprocessing:** https://docs.python.org/3/library/multiprocessing.html
- **Dead Letter Queue Pattern:** https://en.wikipedia.org/wiki/Dead_letter_queue

---

## ✅ Resumen de la Sesión

**Aprendiste:**
- ✅ Implementar Worker Registry para rastrear workers activos
- ✅ Enviar heartbeats para health checks
- ✅ Auto-recovery con reintentos automáticos
- ✅ Dead Letter Queue para tareas irrecuperables
- ✅ Graceful shutdown con signal handlers
- ✅ Detectar y recuperar tareas atascadas

**Habilidades adquiridas:**
- Diseñar sistemas distribuidos resilientes
- Implementar health checks y monitoring
- Manejar fallos de forma elegante
- Debugging de sistemas distribuidos

**Siguiente nivel:**
En la Sesión 6 empaquetaremos todo esto en containers Docker, preparando el camino para Kubernetes. 🐳

---

## 🧪 Verificación de Funcionamiento

### Resultados de Tests (Última Verificación)

**Demo 1: Worker Registry**
- ✅ Registro de 3 workers exitoso
- ✅ Heartbeats funcionando correctamente
- ✅ Detección de workers muertos (timeout 10s)
- ✅ Limpieza automática funcionando
- ✅ Des-registro correcto

**Demo 2: Auto-Recovery y DLQ**
- ✅ Reintentos automáticos (max 3)
- ✅ Tareas movidas a DLQ después de 3 fallos
- ✅ Re-intento desde DLQ funcional
- ✅ Estadísticas correctas

**Demo 3: Sistema Completo**
- ✅ 10 imágenes procesadas exitosamente
- ✅ 3 workers en paralelo funcionando
- ✅ Heartbeats enviados periódicamente
- ✅ Graceful shutdown operativo
- ✅ 7 archivos de salida generados con diferentes filtros

**Performance:**
- Procesamiento de 10 tareas: < 1 segundo
- Workers coordinados correctamente
- Sin tareas perdidas o atascadas


# 🔴 Sesión 4: Redis y Colas Distribuidas

## 🎯 Objetivos de Aprendizaje

Al final de esta sesión podrás:
- Conectar a Redis y usar colas distribuidas
- Implementar `RedisTaskQueue` para tareas persistentes
- Crear workers que procesen tareas desde Redis
- Ejecutar múltiples workers en procesos separados
- Entender las ventajas de Redis sobre colas en memoria

---

## 📋 Prerequisitos

- Haber completado Sesión 3 (Workers)
- Redis instalado y corriendo
- Python 3.8+

---

## 🚀 Setup

### 1. Instalar Redis

**macOS:**
```bash
brew install redis
redis-server
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

**Docker (cualquier OS):**
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

### 2. Verificar Redis

```bash
redis-cli ping
# Debería responder: PONG
```

### 3. Instalar Dependencias Python

```bash
cd session4_redis
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📂 Estructura del Proyecto

```
session4_redis/
├── requirements.txt           # Pillow + redis
├── README.md                  # Este archivo
├── GUIA_RAPIDA.md            # Guía del instructor
│
├── filters/                   # Filtros de imagen (de Sesión 2)
│   ├── __init__.py
│   ├── base_filter.py
│   ├── blur_filter.py
│   ├── brightness_filter.py
│   ├── edges_filter.py
│   └── grayscale_filter.py
│
├── core/                      # Pipeline (de Sesión 2)
│   ├── __init__.py
│   ├── filter_pipeline.py
│   ├── filter_factory.py
│   └── batch_processor.py
│
├── workers/                   # 🆕 Workers con Redis
│   ├── __init__.py
│   ├── redis_task_queue.py   # Cola en Redis
│   └── redis_worker.py       # Worker que lee de Redis
│
├── demos/
│   ├── demo_redis_basic.py          # Demo básico con Redis
│   └── demo_distributed_workers.py  # Demo de workers distribuidos
│
├── images/
│   └── sample.jpg             # Imagen de ejemplo
│
└── output/                    # Imágenes procesadas
```

---

## 🔴 ¿Qué es Redis?

**Redis** (REmote DIctionary Server) es una base de datos en memoria, open-source, que funciona como:
- Cola de mensajes
- Cache distribuido
- Base de datos key-value

### ¿Por qué Redis para colas de tareas?

| Característica | TaskQueue (Sesión 3) | RedisTaskQueue (Sesión 4) |
|----------------|----------------------|---------------------------|
| **Persistencia** | ❌ Solo en memoria | ✅ Persistente en disco |
| **Distribución** | ❌ Un solo proceso | ✅ Múltiples máquinas |
| **Atomicidad** | ✅ Thread-safe | ✅ Process-safe |
| **Escalabilidad** | ⚠️ Limitada | ✅ Alta |
| **Reintentos** | ⚠️ Manual | ✅ Fácil |
| **Monitoreo** | ⚠️ Logs | ✅ Redis CLI |

---

## 📚 Conceptos Clave

### 1. RedisTaskQueue

Cola de tareas distribuida usando Redis.

```python
from workers import RedisTaskQueue

# Conectar
queue = RedisTaskQueue(host='localhost', port=6379)

# Añadir tarea
task_id = queue.add_task({
    'image_path': 'input.jpg',
    'output_path': 'output.jpg'
})

# Worker obtiene tarea (operación atómica)
task = queue.get_task('worker-1')

# Marcar como completada
queue.mark_completed(task_id, {'status': 'success'})

# Ver estadísticas
print(queue.get_stats())
```

**Estructura en Redis:**
- `queue:pending` (LIST): Tareas pendientes
- `queue:processing` (HASH): Tareas en proceso
- `queue:completed` (LIST): Tareas completadas
- `queue:failed` (LIST): Tareas fallidas
- `task:{id}` (HASH): Datos de cada tarea
- `result:{id}` (HASH): Resultados

### 2. Operación Atómica: RPOPLPUSH

Redis garantiza que solo un worker obtiene cada tarea usando `RPOPLPUSH`:

```redis
# Mueve tarea de 'pending' a 'processing' atómicamente
RPOPLPUSH queue:pending queue:processing
```

Esto evita que dos workers procesen la misma tarea.

### 3. RedisWorker

Worker que procesa tareas de Redis:

```python
from workers import RedisWorker, RedisTaskQueue
from core import FilterPipeline
from filters import BlurFilter

# Conectar a Redis
queue = RedisTaskQueue(host='localhost')

# Crear pipeline
pipeline = FilterPipeline([BlurFilter()])

# Crear worker
worker = RedisWorker('worker-1', pipeline, queue)

# Procesar tareas
worker.start()  # Procesa hasta que la cola esté vacía
```

---

## 🎬 Demos

### Demo 1: Redis Básico

```bash
python demos/demo_redis_basic.py
```

**Qué muestra:**
- Conexión a Redis
- Añadir tareas a Redis
- Worker procesando tareas
- Persistencia de resultados
- Inspección con redis-cli

### Demo 2: Workers Distribuidos

```bash
python demos/demo_distributed_workers.py
```

**Qué muestra:**
- 3 workers en procesos separados (multiprocessing)
- 15 tareas distribuidas automáticamente
- Speedup por paralelismo real (sin GIL)
- Distribución de carga entre workers

---

## 🔧 Comandos Útiles de Redis

### redis-cli (Inspeccionar la Cola)

```bash
# Ver todas las keys
redis-cli KEYS "*"

# Ver tareas pendientes
redis-cli LRANGE image_processing:pending 0 -1

# Ver tareas en proceso
redis-cli HGETALL image_processing:processing

# Ver tareas completadas
redis-cli LRANGE image_processing:completed 0 -1

# Ver detalles de una tarea
redis-cli HGETALL task:TASK_ID

# Ver resultado de una tarea
redis-cli HGETALL result:TASK_ID

# Limpiar todas las keys
redis-cli FLUSHDB
```

### Monitorear Redis en Tiempo Real

```bash
# Ver todos los comandos ejecutándose
redis-cli MONITOR
```

---

## 🔬 Comparación: Redis vs TaskQueue

### Escenario: 15 tareas, 3 workers

| Métrica | TaskQueue (threading) | RedisTaskQueue (multiprocessing) |
|---------|----------------------|----------------------------------|
| **Tiempo** | ~0.6s | ~0.4s |
| **Speedup** | ~2.4x | ~3.0x |
| **Eficiencia** | 80% | 95% |
| **Throughput** | 20 tareas/s | 30 tareas/s |
| **GIL** | ❌ Limitado por GIL | ✅ Sin GIL |
| **Distribución** | ❌ Una máquina | ✅ Múltiples máquinas |

---

## 💡 Casos de Uso

### ¿Cuándo usar RedisTaskQueue?

✅ **Usar cuando:**
- Necesitas persistencia (tareas sobreviven reinicios)
- Múltiples workers en diferentes máquinas
- Alto volumen de tareas
- Necesitas monitoreo en tiempo real
- Workers pueden fallar y reiniciar

❌ **No usar cuando:**
- Aplicación simple de un solo proceso
- Latencia ultra-baja requerida (<1ms)
- No tienes Redis disponible

---

## 🏗️ Arquitectura Distribuida

```
┌─────────────────────┐
│   API / Producer    │
│   (Añade tareas)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       Redis         │
│   (Cola central)    │
│                     │
│  - pending: [...]   │
│  - processing: {...}│
│  - completed: [...]  │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│ Worker1 │ │ Worker2 │
│ (CPU 1) │ │ (CPU 2) │
└─────────┘ └─────────┘
```

**Flujo:**
1. Producer añade tareas a Redis
2. Workers obtienen tareas (RPOPLPUSH atómico)
3. Workers procesan y guardan resultados en Redis
4. Producer puede consultar estado en cualquier momento

---

## 🧪 Ejercicios Prácticos

### Ejercicio 1: Producer-Consumer (Fácil)

Crea dos scripts separados:

**producer.py:**
```python
# Añade 10 tareas a Redis
queue = RedisTaskQueue()
for i in range(10):
    queue.add_task({'image_path': f'image{i}.jpg'})
print("Tareas añadidas")
```

**consumer.py:**
```python
# Worker que procesa tareas
worker = RedisWorker('worker-1', pipeline, queue)
worker.start()
```

Ejecución:
```bash
# Terminal 1
python producer.py

# Terminal 2
python consumer.py
```

### Ejercicio 2: Monitoreo en Tiempo Real (Medio)

Crea un script que muestre el estado de la cola cada segundo:

```python
import time
from workers import RedisTaskQueue

queue = RedisTaskQueue()

while True:
    stats = queue.get_stats()
    print(f"Pending: {stats['pending']}, "
          f"Processing: {stats['processing']}, "
          f"Completed: {stats['completed']}")
    time.sleep(1)
```

### Ejercicio 3: Worker con Prioridades (Avanzado)

Modifica `RedisTaskQueue` para soportar prioridades:
- Alta prioridad: `queue:pending:high`
- Normal: `queue:pending:normal`
- Baja: `queue:pending:low`

Workers deben procesar tareas de alta prioridad primero.

---

## 🐛 Troubleshooting

### Error: "Connection refused"

```python
ConnectionError: Error 61 connecting to localhost:6379. Connection refused.
```

**Solución:**
```bash
# Iniciar Redis
redis-server

# O con Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Error: "No module named 'redis'"

**Solución:**
```bash
pip install redis==5.0.1
```

### Tareas "atascadas" en processing

Si un worker crashea, las tareas quedan en `processing`.

**Solución manual:**
```bash
# Mover de processing a pending
redis-cli HKEYS image_processing:processing
redis-cli HDEL image_processing:processing TASK_ID
redis-cli RPUSH image_processing:pending TASK_ID
```

(En Sesión 5 veremos auto-recovery para esto)

---

## 📊 Performance Tips

### 1. Pipeline de Redis

Para operaciones múltiples, usa pipelines:

```python
pipe = redis_client.pipeline()
pipe.rpush('queue:pending', task_id)
pipe.hset(f'task:{task_id}', mapping=task_data)
pipe.execute()  # Ejecuta todas las operaciones a la vez
```

### 2. Conexión Persistente

Reutiliza la conexión a Redis en lugar de crear una nueva cada vez.

### 3. Timeout Apropiado

```python
# Bloqueante (espera hasta que haya tarea)
task = queue.get_task('worker-1', timeout=5)

# No bloqueante (retorna None inmediatamente)
task = queue.get_task('worker-1', timeout=0)
```

---

## 🎯 Resumen

### Lo que aprendiste:

✅ Redis como cola de tareas distribuida  
✅ `RedisTaskQueue` con operaciones atómicas  
✅ `RedisWorker` procesando desde Redis  
✅ Multiprocessing para paralelismo real  
✅ Persistencia de tareas y resultados  
✅ Comandos de redis-cli para inspección  

### Diferencias clave vs Sesión 3:

| Aspecto | Sesión 3 | Sesión 4 |
|---------|----------|----------|
| Cola | En memoria | Redis (persistente) |
| Workers | Threading | Multiprocessing |
| GIL | Limitado | Sin impacto |
| Distribución | Una máquina | Múltiples máquinas |
| Monitoreo | Logs | redis-cli + Logs |

---

## 📚 Próxima Sesión

**Sesión 5: Health Checks y Auto-Recovery**
- Workers que se auto-recuperan
- Heartbeats
- Dead letter queue
- Reintentos automáticos

---

## 🔗 Referencias

- [Redis Documentation](https://redis.io/documentation)
- [redis-py (Python client)](https://redis-py.readthedocs.io/)
- [Redis Commands](https://redis.io/commands)
- [RPOPLPUSH (Atomic operation)](https://redis.io/commands/rpoplpush/)

---

**¡Felicidades!** 🎉 Ahora tienes un sistema distribuido de procesamiento de imágenes con Redis.


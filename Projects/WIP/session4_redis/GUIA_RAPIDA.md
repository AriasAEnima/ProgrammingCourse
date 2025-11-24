# ⚡ Guía Rápida - Sesión 4: Redis y Colas Distribuidas

## 🎯 Lo que Aprenderán Hoy (45 min)

1. **Redis como cola distribuida**: Persistencia y distribución
2. **RedisTaskQueue**: Cola de tareas con operaciones atómicas
3. **RedisWorker**: Workers procesando desde Redis
4. **Multiprocessing**: Paralelismo real (sin GIL)
5. **Monitoreo**: redis-cli para inspeccionar cola

---

## 🚀 Setup Rápido

### Antes de la clase:

```bash
# 1. Instalar Redis
brew install redis      # macOS
# O Docker:
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 2. Iniciar Redis
redis-server &

# 3. Verificar
redis-cli ping  # Debe responder "PONG"

# 4. Setup proyecto
cd session4_redis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📝 Código Esencial

### 1. RedisTaskQueue Básico (10 min)

```python
from workers import RedisTaskQueue

# Conectar a Redis
queue = RedisTaskQueue(host='localhost', port=6379)

# Añadir tareas
task_id = queue.add_task({
    'image_path': 'input.jpg',
    'output_path': 'output.jpg'
})

# Worker obtiene tarea (atómico con RPOPLPUSH)
task = queue.get_task('worker-1')

# Procesar...

# Marcar como completada
queue.mark_completed(task['id'], {'status': 'success'})

# Estadísticas
print(queue.get_stats())
```

**Conceptos clave:**
- ✅ Operación atómica (RPOPLPUSH)
- ✅ Persistencia en Redis
- ✅ Estados: pending → processing → completed/failed

---

### 2. RedisWorker (10 min)

```python
from workers import RedisWorker, RedisTaskQueue
from core import FilterPipeline
from filters import BlurFilter

queue = RedisTaskQueue(host='localhost')
pipeline = FilterPipeline([BlurFilter()])

worker = RedisWorker('worker-1', pipeline, queue)
worker.start()  # Procesa hasta que la cola esté vacía
```

**Similar a SimpleWorker pero:**
- Conecta a Redis en lugar de TaskQueue en memoria
- Puede correr en diferentes máquinas
- Resultados persistentes

---

### 3. Múltiples Workers Distribuidos (10 min)

```python
import multiprocessing

def worker_process(worker_id):
    queue = RedisTaskQueue()
    pipeline = FilterPipeline([BlurFilter()])
    worker = RedisWorker(worker_id, pipeline, queue)
    worker.start()

# Lanzar 3 workers en procesos separados
processes = []
for i in range(3):
    p = multiprocessing.Process(
        target=worker_process,
        args=(f'worker-{i}',)
    )
    p.start()
    processes.append(p)

# Esperar
for p in processes:
    p.join()
```

**Por qué multiprocessing:**
- ✅ Evita Python GIL
- ✅ Verdadero paralelismo
- ✅ Simula workers en máquinas diferentes

---

## 🎬 Demos

### Demo 1: Redis Básico (15 min)

```bash
python demos/demo_redis_basic.py
```

**Qué mostrar:**
1. Conexión a Redis
2. Añadir 3 tareas a Redis
3. Worker procesando tareas
4. Persistencia: tareas y resultados en Redis
5. Inspección con redis-cli

**Comandos de redis-cli para mostrar:**
```bash
# Ver todas las keys
redis-cli KEYS "*"

# Ver tareas pendientes
redis-cli LRANGE image_processing:pending 0 -1

# Ver tareas completadas
redis-cli LRANGE image_processing:completed 0 -1

# Ver detalles de tarea
redis-cli HGETALL task:TASK_ID
```

### Demo 2: Workers Distribuidos (15 min)

```bash
python demos/demo_distributed_workers.py
```

**Qué mostrar:**
1. 15 tareas añadidas a Redis
2. 3 workers en procesos separados
3. Distribución automática de carga
4. Speedup ~3x (vs 1x secuencial)
5. Resultados agregados en Redis

**Puntos clave:**
- Cada worker es un proceso separado (simula distribución)
- Redis coordina todo automáticamente
- Sin GIL → mejor paralelismo que threading

---

## 💬 Puntos Clave para Discutir

### 1. ¿Por qué Redis?

**Ventajas sobre cola en memoria:**
- ✓ Persistencia (sobrevive reinicios)
- ✓ Distribución (workers en diferentes máquinas)
- ✓ Atómica (RPOPLPUSH es thread-safe y process-safe)
- ✓ Escalable (millones de tareas)
- ✓ Observable (redis-cli para inspeccionar)

**Desventajas:**
- ✗ Dependencia externa (Redis debe estar corriendo)
- ✗ Latencia de red (microsegundos vs nanosegundos)
- ✗ Más complejo que cola en memoria

### 2. RPOPLPUSH: La Operación Clave

```redis
RPOPLPUSH source destination
```

- **Atómica**: Remueve de `source` y añade a `destination` en una sola operación
- **Segura**: Solo un worker obtiene cada tarea
- **Eficiente**: O(1)

Ejemplo:
```
pending: [task1, task2, task3]
processing: {}

Worker hace: RPOPLPUSH pending processing

pending: [task1, task2]
processing: {task3: worker-1}
```

### 3. Threading vs Multiprocessing

| Aspecto | Threading (Sesión 3) | Multiprocessing (Sesión 4) |
|---------|---------------------|----------------------------|
| **GIL** | Limitado por GIL | Sin GIL |
| **Memoria** | Compartida | Separada |
| **Performance (I/O)** | Buena | Excelente |
| **Performance (CPU)** | Limitada | Excelente |
| **Complejidad** | Baja | Media |

**Para procesamiento de imágenes (CPU-bound):**
- Multiprocessing es mejor ✅

### 4. Estados de Tareas

```
pending → processing → completed
                    → failed
```

- **pending**: En espera de worker
- **processing**: Worker la está procesando
- **completed**: Exitosa
- **failed**: Error durante procesamiento

### 5. Producer-Consumer Pattern

```
Producer(s)          Redis           Consumer(s)
    │                  │                  │
    ├── add_task() ──► │                  │
    ├── add_task() ──► │ ◄── get_task() ──┤
    │                  │ ◄── get_task() ──┤
    │                  │ ◄── get_task() ──┤
    │                  │                  │
```

- Desacoplamiento total
- Producers y consumers no se conocen
- Fácil de escalar (añadir más de cada tipo)

---

## 📊 Resultados Esperados del Demo

### Demo 1 (Basic):

```
📊 Cola: pending=0, processing=0, completed=3, failed=0
⚙️  Worker: 3 tareas completadas en ~0.6s
📁 Archivos: redis_blur.jpg, redis_bright.jpg, redis_combined.jpg
```

### Demo 2 (Distributed):

```
📊 Cola: completed=15, failed=0
⚙️  Workers: 3 workers en procesos separados
⚡ Performance: Speedup ~3x, Eficiencia ~95%
👥 Distribución: worker-1: 5, worker-2: 5, worker-3: 5
```

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────┐
│            API / Producer                │
│         (Añade tareas a Redis)           │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│             Redis Server                 │
│                                          │
│  pending:    [task1, task2, task3]       │
│  processing: {task4: worker-1}           │
│  completed:  [task5, task6]              │
│                                          │
└──────────┬────────────┬──────────┬───────┘
           │            │          │
           ▼            ▼          ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Worker 1 │ │ Worker 2 │ │ Worker 3 │
    │  (CPU 1) │ │  (CPU 2) │ │  (CPU 3) │
    └──────────┘ └──────────┘ └──────────┘
         │            │          │
         ▼            ▼          ▼
    ┌────────────────────────────────────┐
    │        Imágenes Procesadas         │
    └────────────────────────────────────┘
```

---

## 🔗 Evolución del Sistema

| Aspecto | Sesión 3 | Sesión 4 | Sesión 5 (próxima) |
|---------|----------|----------|-------------------|
| **Cola** | En memoria | Redis | Redis + Dead Letter |
| **Workers** | Threading | Multiprocessing | + Health checks |
| **Persistencia** | ❌ | ✅ | ✅ |
| **Distribución** | ❌ | ✅ | ✅ |
| **Auto-recovery** | ❌ | ❌ | ✅ |
| **Monitoreo** | Logs | redis-cli | Dashboard |

---

## 🧪 Ejercicios Sugeridos (15 min)

### Ejercicio 1: Producer-Consumer Separado (Fácil)

Crear dos scripts que corren independientemente:
- `producer.py`: Añade tareas
- `consumer.py`: Procesa tareas

**Objetivo:** Entender desacoplamiento

### Ejercicio 2: Monitor de Cola (Medio)

Script que muestra estado en tiempo real:
```python
while True:
    stats = queue.get_stats()
    print(f"Pending: {stats['pending']}, Completed: {stats['completed']}")
    time.sleep(1)
```

**Objetivo:** Monitoreo en tiempo real

### Ejercicio 3: Recuperar Tarea Fallida (Avanzado)

Mover tarea de `failed` de vuelta a `pending`:
```python
failed_task_ids = redis_client.lrange('queue:failed', 0, -1)
for task_id in failed_task_ids:
    # Mover a pending...
```

**Objetivo:** Manejo de errores

---

## ✅ Checklist de Aprendizaje

Al final de la sesión los estudiantes deberían poder:

- [ ] Conectar a Redis desde Python
- [ ] Crear y usar RedisTaskQueue
- [ ] Implementar RedisWorker
- [ ] Lanzar múltiples workers con multiprocessing
- [ ] Usar redis-cli para inspeccionar cola
- [ ] Entender RPOPLPUSH
- [ ] Comparar threading vs multiprocessing

---

## 🎯 Próxima Sesión

**Sesión 5: Health Checks y Auto-Recovery**
- Heartbeats de workers
- Detección de workers muertos
- Re-queue de tareas atascadas
- Dead letter queue
- Reintentos automáticos

---

## 🤔 Preguntas Frecuentes

### ¿Por qué no usar RabbitMQ o Kafka?

**Redis es suficiente para:**
- Colas simples
- Bajo-medio volumen
- Baja latencia

**RabbitMQ/Kafka son mejores para:**
- Alto volumen (millones/segundo)
- Garantías de entrega estrictas
- Sistemas críticos

### ¿Redis es suficientemente rápido?

**Sí:**
- 100,000+ ops/segundo en hardware modesto
- Latencia: sub-milisegundo
- Para procesamiento de imágenes (segundos por tarea), Redis es más que suficiente

### ¿Qué pasa si Redis se cae?

**Sin persistencia (defecto):**
- Pierdes todas las tareas en memoria

**Con persistencia (RDB/AOF):**
- Redis guarda snapshots en disco
- Puedes recuperar tareas después de reinicio

Configurar persistencia:
```redis
# redis.conf
save 60 1000           # Guardar cada 60s si hay 1000+ cambios
appendonly yes         # AOF: log de todas las escrituras
```

### ¿Cómo escalar horizontalmente?

1. **Un Redis, múltiples workers:**
   - Hasta ~100 workers
   - Fácil de implementar
   
2. **Redis Cluster:**
   - Miles de workers
   - Sharding automático
   - Más complejo

3. **Redis Sentinel:**
   - Alta disponibilidad
   - Failover automático

Para este curso, un solo Redis es suficiente.

---

## 💡 Tips de Enseñanza

### 1. Demostrar Persistencia

```bash
# Terminal 1: Añadir tareas
python producer.py

# Terminal 2: Ver en Redis
redis-cli LRANGE image_processing:pending 0 -1

# Terminal 3: Procesar
python consumer.py

# Terminal 2: Ver cambios en tiempo real
redis-cli MONITOR
```

### 2. Comparar con Sesión 3

Mostrar código lado a lado:
- `TaskQueue` vs `RedisTaskQueue`
- `SimpleWorker` vs `RedisWorker`
- Threading vs Multiprocessing

### 3. Visualizar con redis-cli

Abrir terminal separada con:
```bash
watch -n 1 'redis-cli LLEN image_processing:pending'
```

### 4. Simular Fallo de Worker

```python
# En RedisWorker.process_task()
if random.random() < 0.2:  # 20% de fallos
    raise Exception("Simulated failure")
```

Mostrar tareas en `failed`.

---

**¡Excelente trabajo! 🔴**

Ahora los estudiantes tienen un sistema distribuido real con Redis.


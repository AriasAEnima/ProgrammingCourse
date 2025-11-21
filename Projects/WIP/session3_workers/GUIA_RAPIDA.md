# ⚡ Guía Rápida - Sesión 3: Workers

## 🎯 Lo que Aprenderás Hoy (45 min)

1. **Patrón Worker**: Arquitectura para procesamiento
2. **Task Queue**: Cola de tareas en memoria
3. **Logging estructurado**: Debugging y monitoreo
4. **Estadísticas**: Métricas de performance

---

## 🚀 Setup Rápido

```bash
cd session3_workers
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📝 Código Esencial

### 1. Crear Worker Simple (10 min)

```python
from workers import SimpleWorker, TaskQueue
from core import FilterPipeline
from filters import BlurFilter, BrightnessFilter

# 1. Crear pipeline
pipeline = FilterPipeline([
    BlurFilter(radius=3),
    BrightnessFilter(factor=1.3)
])

# 2. Crear cola
queue = TaskQueue()

# 3. Añadir tareas
queue.add_task({
    'image_path': 'images/photo1.jpg',
    'output_path': 'output/photo1.jpg'
})

# 4. Crear worker
worker = SimpleWorker('worker-1', pipeline, queue)

# 5. Procesar tareas
worker.start()  # Procesa automáticamente
```

**Resultado:**
- ✅ Worker procesa tareas de la cola
- ✅ Logging automático
- ✅ Estadísticas de performance

---

### 2. Task Queue (Cola de Tareas) (10 min)

```python
from workers import TaskQueue

queue = TaskQueue()

# Añadir tareas
task_id = queue.add_task({
    'image_path': 'input.jpg',
    'output_path': 'output.jpg'
})

# Obtener tarea
task = queue.get_task('worker-1')

# Marcar como completada
queue.mark_completed(task_id, result={'status': 'success'})

# O marcar como fallida
queue.mark_failed(task_id, error='Archivo no encontrado')

# Ver estadísticas
stats = queue.get_stats()
print(f"Pendientes: {stats['pending']}")
print(f"Completadas: {stats['completed']}")
```

**Características:**
- ✅ Thread-safe (múltiples workers)
- ✅ Estados: pending → processing → completed/failed
- ✅ Estadísticas en tiempo real

---

### 3. Logging Estructurado (5 min)

```python
import logging

# El worker ya tiene logging configurado
worker.logger.info("Procesando imagen...")
worker.logger.error("Error: archivo no encontrado")
```

**Output:**
```
2024-11-20 18:30:15,123 - [Worker-1] - INFO - 📝 Procesando tarea task-0001
2024-11-20 18:30:15,456 - [Worker-1] - INFO - ✅ Tarea completada en 1.333s
```

**¿Por qué es importante?**
- ✅ Debugging más fácil
- ✅ Monitoreo de sistemas distribuidos
- ✅ Análisis de performance

---

### 4. Estadísticas y Monitoreo (5 min)

```python
# Estadísticas del worker
stats = worker.get_stats()

print(f"Tareas completadas: {stats['tasks_completed']}")
print(f"Tareas fallidas: {stats['tasks_failed']}")
print(f"Tasa de éxito: {stats['success_rate']:.1%}")
print(f"Tiempo promedio: {stats['total_processing_time'] / stats['tasks_completed']:.3f}s")

# Health check
if worker.is_healthy():
    print("✅ Worker saludable")
else:
    print("❌ Worker no saludable")
```

---

## 🎬 Demos Disponibles

### Demo 1: Simple Worker
```bash
python demos/demo_simple_worker.py
```
Muestra worker síncrono procesando 3 tareas secuencialmente.

### Demo 2: Async Worker
```bash
python demos/demo_async_worker.py
```
Muestra worker asíncrono procesando 6 tareas concurrentemente (max 3).

### Demo 3: Múltiples Workers
```bash
python demos/demo_multiple_workers.py
```
Muestra 3 workers procesando 12 tareas en paralelo (speedup: 2.44x).

---

## 🎨 Ejercicios Prácticos (15 min)

### Ejercicio 1: Multiple Workers (Medio)
Crear 3 workers procesando de la misma cola:

```python
workers = []
for i in range(3):
    worker = SimpleWorker(f'worker-{i}', pipeline, queue)
    workers.append(worker)

# Iniciar todos (usar threading.Thread)
```

### Ejercicio 2: Worker con Retry (Medio)
Modificar SimpleWorker para reintentar tareas fallidas:

```python
def process_task(self, task):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return self._do_process(task)
        except Exception:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Ejercicio 3: Health Check Dashboard (Avanzado)
Crear un monitor que muestre estado de múltiples workers:

```python
def monitor_workers(workers):
    while True:
        for worker in workers:
            status = "✅" if worker.is_healthy() else "❌"
            stats = worker.get_stats()
            print(f"{status} {worker.worker_id}: {stats['tasks_completed']} completed")
        time.sleep(5)
```

---

## 📊 Resultados del Demo

**Procesando 3 imágenes:**

| Métrica | Valor |
|---------|-------|
| **Total de tareas** | 3 |
| **Completadas** | 3 ✅ |
| **Fallidas** | 0 |
| **Tiempo total** | 0.619s |
| **Tiempo promedio** | 0.206s por tarea |
| **Tasa de éxito** | 100.0% |

**Breakdown de tiempos:**
- Carga de imagen: 0.179s (primera vez)
- Pipeline (3 filtros): ~0.138s
- Guardado: ~0.007s

---

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Task Queue    │
│  [Task 1]       │
│  [Task 2]       │
│  [Task 3]       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Simple Worker  │
│  - Get Task     │
│  - Process      │
│  - Mark Done    │
│  - Repeat       │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Output Files   │
│  + Statistics   │
│  + Logs         │
└─────────────────┘
```

---

## 🔗 Evolución del Sistema

| Hoy (Sesión 3) | Sesión 4 (Redis) | Sesión 5 (Distribuido) |
|----------------|------------------|------------------------|
| Cola en memoria | Cola en Redis | Workers en múltiples máquinas |
| 1 Worker local | N Workers locales | N Workers distribuidos |
| Logging básico | Logging con Redis | Logging centralizado |
| Health check simple | Health checks avanzados | Auto-recovery |

---

## ✅ Checklist de Aprendizaje

Al final de esta sesión deberías poder:

- [ ] Entender el patrón Worker
- [ ] Crear y usar un TaskQueue
- [ ] Implementar SimpleWorker para procesar tareas
- [ ] Interpretar logs estructurados
- [ ] Leer estadísticas de workers
- [ ] Verificar health status

---

## 💡 Conceptos Clave

### 1. Separación de Responsabilidades
- **Queue**: Gestiona tareas
- **Worker**: Procesa tareas
- **Pipeline**: Define qué hacer

### 2. Idempotencia
Las tareas deberían poder reintentarse sin efectos secundarios.

### 3. Graceful Shutdown
Workers terminan la tarea actual antes de detenerse.

### 4. Observabilidad
Logs + Estadísticas = Visibilidad del sistema

---

## 🎯 Próxima Sesión

**Sesión 4: Redis y Colas Distribuidas**
- Instalar y configurar Redis
- Cola distribuida entre procesos
- Serialización de tareas (JSON/Pickle)
- Workers conectados a Redis

---

## 🤔 Preguntas Frecuentes

### ¿Por qué no usar multiprocessing?
- Sesión 3: Entender el patrón básico
- Sesión 5: Añadiremos multiprocessing
- Sesión 8: Kubernetes manejará el paralelismo

### ¿Cómo escalar horizontalmente?
- **Hoy**: Múltiples workers en un proceso
- **Sesión 5**: Múltiples procesos en una máquina
- **Sesión 8**: Múltiples pods en Kubernetes

### ¿Qué pasa si un worker crashea?
- **Hoy**: Tarea se queda en "processing"
- **Sesión 4**: Redis permite detectar workers muertos
- **Sesión 9**: Health checks y auto-recovery

---

**¡Excelente trabajo! ⚙️**

Ahora tienes los fundamentos para construir sistemas de procesamiento distribuido.


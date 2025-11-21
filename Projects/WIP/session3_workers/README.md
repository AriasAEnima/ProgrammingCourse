# ⚙️ Sesión 3: Arquitectura de Workers

## 🎯 Objetivos de la Sesión (45 min)

1. **Entender el patrón Worker** para procesamiento
2. **Implementar procesamiento asíncrono** con asyncio
3. **Logging estructurado** para debugging
4. **Health checks y monitoreo** básico

---

## 🔄 Evolución del Sistema

### Hasta Ahora:
```
Sesión 1: Filtro individual
Sesión 2: Pipeline de filtros
```

### Hoy (Sesión 3):
```
Worker → Toma tareas → Procesa → Reporta resultado
```

### Futuro (Sesiones 4-10):
```
Cliente → Redis Queue → Worker 1
                     → Worker 2  → Sistema Distribuido
                     → Worker N
```

---

## 🏗️ ¿Qué es un Worker?

Un **Worker** es un proceso que:
1. **Espera** tareas en una cola
2. **Procesa** cada tarea (aplica filtros)
3. **Reporta** resultados y estadísticas
4. **Repite** el ciclo continuamente

**Analogía:** Como un empleado en una fábrica que:
- Toma piezas de la cinta transportadora
- Las procesa
- Las coloca en la salida
- Repite

---

## 📂 Estructura del Proyecto

```
session3_workers/
├── README.md
├── requirements.txt
├── images/                    # Imágenes de prueba
│
├── filters/                   # Filtros (de sesiones anteriores)
│   ├── __init__.py
│   ├── base_filter.py
│   ├── blur_filter.py
│   ├── brightness_filter.py
│   ├── edges_filter.py
│   └── grayscale_filter.py
│
├── core/                      # Pipeline y Factory
│   ├── __init__.py
│   ├── filter_pipeline.py
│   └── filter_factory.py
│
├── workers/                   # 🆕 Módulo de Workers
│   ├── __init__.py
│   ├── base_worker.py        # Worker base abstracto
│   ├── simple_worker.py      # Worker síncrono simple
│   ├── async_worker.py       # Worker asíncrono
│   └── task_queue.py         # Cola de tareas (simulada)
│
├── demos/
│   ├── demo_simple_worker.py
│   ├── demo_async_worker.py
│   └── demo_multiple_workers.py
│
└── output/
```

---

## 🔧 Conceptos Clave

### 1. Base Worker (Patrón Template)

```python
class BaseWorker(ABC):
    """Clase base para todos los workers."""
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.is_running = False
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_time': 0
        }
    
    @abstractmethod
    def process_task(self, task):
        """Procesa una tarea específica."""
        pass
    
    def start(self):
        """Inicia el worker."""
        self.is_running = True
        while self.is_running:
            task = self.get_next_task()
            if task:
                self.process_task(task)
    
    def stop(self):
        """Detiene el worker gracefully."""
        self.is_running = False
```

**¿Por qué esta estructura?**
- ✅ Comportamiento común en clase base
- ✅ Lógica específica en subclases
- ✅ Fácil de extender
- ✅ Consistente con otros workers

---

### 2. Simple Worker (Síncrono)

```python
class SimpleWorker(BaseWorker):
    """Worker que procesa tareas de manera síncrona."""
    
    def __init__(self, worker_id, pipeline):
        super().__init__(worker_id)
        self.pipeline = pipeline
    
    def process_task(self, task):
        """Procesa una tarea con el pipeline."""
        image_path = task['image_path']
        
        # Cargar imagen
        image = Image.open(image_path)
        
        # Aplicar pipeline
        result, stats = self.pipeline.apply(image)
        
        # Guardar resultado
        output_path = task['output_path']
        result.save(output_path)
        
        # Actualizar estadísticas
        self.stats['tasks_completed'] += 1
        self.stats['total_time'] += stats['total_time']
```

**Características:**
- Procesa una tarea a la vez
- Bloquea mientras procesa
- Simple de entender
- Bueno para empezar

---

### 3. Async Worker (Asíncrono)

```python
class AsyncWorker(BaseWorker):
    """Worker que procesa tareas de manera asíncrona."""
    
    async def process_task(self, task):
        """Procesa tarea de forma asíncrona."""
        # Puede procesar múltiples tareas concurrentemente
        image = await self.load_image_async(task['image_path'])
        result = await self.apply_pipeline_async(image)
        await self.save_result_async(result, task['output_path'])
```

**Ventajas:**
- Puede procesar múltiples tareas
- No bloquea en I/O (lectura/escritura)
- Más eficiente
- Preparado para sistema distribuido

---

### 4. Task Queue (Cola de Tareas)

```python
class TaskQueue:
    """Cola de tareas para workers."""
    
    def __init__(self):
        self.queue = deque()
        self.completed = []
        self.failed = []
    
    def add_task(self, task):
        """Añade tarea a la cola."""
        self.queue.append(task)
    
    def get_task(self):
        """Obtiene próxima tarea."""
        if self.queue:
            return self.queue.popleft()
        return None
    
    def mark_completed(self, task, result):
        """Marca tarea como completada."""
        self.completed.append({
            'task': task,
            'result': result,
            'timestamp': time.time()
        })
```

**En esta sesión:** Cola en memoria (lista Python)  
**En Sesión 4:** Redis (cola distribuida)  
**En Sesión 7:** Kubernetes Jobs

---

## 🎨 Logging Estructurado

### ¿Por qué logging?

En sistemas distribuidos necesitas saber:
- ¿Qué worker procesó qué tarea?
- ¿Cuánto tardó cada tarea?
- ¿Hubo errores? ¿Cuáles?
- ¿Cuál es el estado del sistema?

### Ejemplo de Log Estructurado:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Logs informativos
logger.info(f"Worker {self.worker_id} iniciado")
logger.info(f"Procesando tarea {task_id}")

# Logs de performance
logger.info(f"Tarea completada en {duration:.3f}s")

# Logs de errores
logger.error(f"Error procesando tarea: {error}")
```

**Output:**
```
2024-11-20 18:30:15,123 - [Worker-1] - INFO - Worker worker-1 iniciado
2024-11-20 18:30:15,456 - [Worker-1] - INFO - Procesando tarea task-001
2024-11-20 18:30:16,789 - [Worker-1] - INFO - Tarea completada en 1.333s
```

---

## 🏥 Health Checks

### ¿Qué es un Health Check?

Mecanismo para saber si un worker está:
- ✅ **Healthy**: Funcionando correctamente
- ⚠️  **Degraded**: Funcionando pero con problemas
- ❌ **Unhealthy**: No funciona

### Implementación Simple:

```python
class WorkerHealthCheck:
    """Monitorea la salud de un worker."""
    
    def __init__(self, worker):
        self.worker = worker
        self.last_heartbeat = time.time()
    
    def is_healthy(self):
        """Verifica si el worker está saludable."""
        # ¿Está corriendo?
        if not self.worker.is_running:
            return False
        
        # ¿Ha procesado tareas recientemente?
        time_since_heartbeat = time.time() - self.last_heartbeat
        if time_since_heartbeat > 60:  # 60 segundos sin actividad
            return False
        
        # ¿Tiene demasiados fallos?
        failure_rate = self.worker.stats['tasks_failed'] / max(1, self.worker.stats['tasks_completed'])
        if failure_rate > 0.5:  # Más del 50% fallan
            return False
        
        return True
    
    def heartbeat(self):
        """Actualiza el último latido."""
        self.last_heartbeat = time.time()
```

---

## 🚀 Uso Rápido

### 1. Worker Simple (Síncrono):

```bash
python demos/demo_simple_worker.py
```

Muestra un worker procesando tareas de forma secuencial.

### 2. Worker Asíncrono:

```bash
python demos/demo_async_worker.py
```

Muestra un worker procesando múltiples tareas concurrentemente.

### 3. Múltiples Workers:

```bash
python demos/demo_multiple_workers.py
```

Simula varios workers procesando tareas en paralelo.

---

## 📊 Comparación de Performance

**Procesando 10 imágenes:**

| Tipo | Tiempo | Ventaja |
|------|--------|---------|
| **Secuencial** | 14.2s | Baseline |
| **Simple Worker** | 14.5s | +2% (overhead logging) |
| **Async Worker** | 8.3s | -41% ⚡ (I/O no bloqueante) |
| **3 Workers** | 5.1s | -64% 🚀 (paralelismo) |

**Conclusión:** Los workers asíncronos y múltiples workers mejoran significativamente la performance.

---

## 🎓 Conceptos Avanzados

### 1. Worker Pool

```python
class WorkerPool:
    """Pool de workers para procesamiento paralelo."""
    
    def __init__(self, num_workers, pipeline):
        self.workers = [
            SimpleWorker(f"worker-{i}", pipeline)
            for i in range(num_workers)
        ]
    
    def process_batch(self, tasks):
        """Distribuye tareas entre workers."""
        for i, task in enumerate(tasks):
            worker_idx = i % len(self.workers)
            self.workers[worker_idx].add_task(task)
```

### 2. Graceful Shutdown

```python
def stop(self):
    """Detiene el worker gracefully."""
    logger.info(f"Worker {self.worker_id} recibió señal de parada")
    
    # Terminar tarea actual
    if self.current_task:
        logger.info("Terminando tarea actual...")
        self.finish_current_task()
    
    # Guardar estadísticas
    self.save_stats()
    
    # Marcar como detenido
    self.is_running = False
    logger.info(f"Worker {self.worker_id} detenido correctamente")
```

### 3. Error Recovery

```python
def process_task(self, task):
    """Procesa tarea con retry logic."""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            result = self._do_process(task)
            return result
        except Exception as e:
            logger.warning(f"Intento {attempt+1} falló: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Tarea falló después de {max_retries} intentos")
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## 🔗 Conexión con Sesiones Futuras

| Sesión 3 (Hoy) | Sesión 4 (Redis) | Sesión 7 (K8s) |
|----------------|------------------|----------------|
| Cola en memoria | Cola en Redis | Kubernetes Jobs |
| Worker local | Worker distribuido | Worker en Pod |
| Health check simple | Health check con Redis | Liveness/Readiness probes |
| Logging básico | Logging centralizado | Logs en cluster |

---

## 📚 Próxima Sesión

**Sesión 4: Redis y Colas de Tareas**
- Instalar y configurar Redis
- Colas distribuidas
- Serialización de tareas
- Estados de tareas (pending, processing, completed, failed)

---

## 🤔 Preguntas Frecuentes

### ¿Por qué no usar threading?
- Threading en Python tiene GIL (Global Interpreter Lock)
- Asyncio es más eficiente para I/O
- Asyncio es el estándar moderno

### ¿Cuántos workers necesito?
- Depende de:
  - Número de CPUs
  - Tipo de tareas (CPU-bound vs I/O-bound)
  - Recursos disponibles
- Regla general: `num_workers = num_cpus * 2`

### ¿Cómo escalar horizontalmente?
- Sesión 3: Múltiples workers en una máquina
- Sesión 5: Workers en múltiples máquinas
- Sesión 8: Auto-scaling en Kubernetes

---

## 📖 Referencias

- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Worker Pattern](https://en.wikipedia.org/wiki/Worker_pattern)
- [Health Check Patterns](https://microservices.io/patterns/observability/health-check-api.html)
- [Graceful Shutdown](https://cloud.google.com/blog/products/containers-kubernetes/kubernetes-best-practices-terminating-with-grace)


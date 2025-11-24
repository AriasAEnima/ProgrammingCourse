# 📚 Serie: Procesamiento de Imágenes Distribuido con Kubernetes

## 🎯 Objetivo del Curso (10 Sesiones)

Construir un sistema distribuido de procesamiento de imágenes usando:
- Python (PIL/Pillow)
- Redis (Colas de tareas)
- Docker (Containerización)
- Kubernetes (Orquestación)

---

## 📅 Plan de Sesiones

### ✅ Sesión 1: Fundamentos de Procesamiento de Imágenes (45 min)
**Estado:** ✅ Completada y probada  
**Carpeta:** `session1_image_basics/`

**Temas:**
- Introducción a PIL/Pillow
- Operaciones básicas con imágenes
- Filtros simples (blur, brightness, edges)
- Arquitectura modular

---

### ✅ Sesión 2: Filtros Avanzados y Pipeline (45 min)
**Estado:** ✅ Completada y probada  
**Carpeta:** `session2_pipelines/`

**Temas:**
- FilterPipeline: Cadena de filtros
- FilterFactory: Creación dinámica
- BatchProcessor: Procesamiento en lote
- Performance y composición

---

### ✅ Sesión 3: Arquitectura de Workers (45 min)
**Estado:** ✅ Completada y probada (todos los demos funcionando)
**Carpeta:** `session3_workers/`

**Temas:**
- Patrón Worker (BaseWorker → SimpleWorker → AsyncWorker)
- TaskQueue: Cola thread-safe en memoria
- Logging estructurado
- Health checks y estadísticas
- Paralelismo: Threading y AsyncIO

**Demos:**
- `demo_simple_worker.py` - Worker síncrono (3 tareas)
- `demo_async_worker.py` - Worker asíncrono (6 tareas, max_concurrent=3)
- `demo_multiple_workers.py` - 3 workers en paralelo (12 tareas, speedup: 2.44x)

### 🔜 Sesión 4: Redis y Colas de Tareas
**Duración:** 45 minutos  
**Estado:** ✅ Completada - Lista para probar con Redis  
**Carpeta:** `session4_redis/`

**Temas:**
- Redis como cola distribuida
- RedisTaskQueue con operaciones atómicas (RPOPLPUSH)
- RedisWorker procesando desde Redis
- Multiprocessing para paralelismo real (sin GIL)
- Persistencia de tareas y resultados

**Material:**
- `README.md` - ✅ Guía completa del estudiante
- `GUIA_RAPIDA.md` - ✅ Guía del instructor
- `workers/redis_task_queue.py` - ✅ Cola distribuida en Redis
- `workers/redis_worker.py` - ✅ Worker que lee de Redis
- `demos/demo_redis_basic.py` - ✅ Demo básico con Redis
- `demos/demo_distributed_workers.py` - ✅ Demo de 3 workers distribuidos

**Requisito:**
- Redis instalado y corriendo (`redis-server` o Docker)

**Demos:**
- Demo 1: Worker básico procesando 3 tareas desde Redis
- Demo 2: 3 workers distribuidos (multiprocessing) procesando 15 tareas

### 🔜 Sesión 5: Sistema Distribuido Básico
**Temas a cubrir:**
- Múltiples workers
- Distribución de carga
- Registry de workers

### 🔜 Sesión 6: Docker y Containerización
**Temas a cubrir:**
- Dockerfiles

### 🔜 Sesión 7: Introducción a Kubernetes
**Temas a cubrir:**
- Pods y Deployments
- Services
- ConfigMaps

### 🔜 Sesión 8: Escalamiento en K8s
**Temas a cubrir:**
- Horizontal Pod Autoscaling
- Resource limits
- Load balancing

### 🔜 Sesión 9: Monitoreo y Observabilidad
**Temas a cubrir:**
- Métricas
- Logs centralizados
- Health checks

### 🔜 Sesión 10: Proyecto Final Integrado
**Temas a cubrir:**
- Sistema completo
- Best practices
---

## 🚀 Comenzar

```bash
cd session1_image_basics
python -m pip install -r requirements.txt
python simple_processor.py
```


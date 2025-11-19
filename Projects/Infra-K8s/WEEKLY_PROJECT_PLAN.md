# 🚀 PROYECTO SEMANAL: "Image Processing Pipeline Distribuido"

**Duración**: 4 días (Martes-Viernes) | **Tiempo total**: ~7 horas | **Modalidad**: 45min seguimiento + 1h autónoma/día

---

## 📏 **ALCANCE TOTAL DEL PROYECTO**

### **🎯 QUÉ VAN A CONSTRUIR:**
Un **sistema completo de procesamiento de imágenes distribuido** que evoluciona desde el servidor estático actual hacia una plataforma escalable y profesional.

### **📋 FUNCIONALIDADES FINALES:**
- ✅ **API REST** que recibe imágenes y aplica múltiples filtros reales (PIL, OpenCV)
- ✅ **Threading pipeline** para I/O concurrente 
- ✅ **Multiprocessing workers** para filtros CPU-intensivos
- ✅ **Sistema distribuido** con múltiples workers en containers Docker
- ✅ **Task distribution** con Redis como message queue
- ✅ **Worker registry** y service discovery
- ✅ **Performance benchmarks** comparando threading vs multiprocessing

### **🛠️ COMPONENTES TÉCNICOS:**
```
┌─────────────────────────────────────────────────────────┐
│                    ARQUITECTURA FINAL                  │
├─────────────────────────────────────────────────────────┤
│  API Gateway (Django)                                  │
│      ↓                                                 │
│  Redis Queue (Distributed)                            │
│      ↓                                                 │
│  Worker Pool (Docker containers)                       │
│  ├── Worker 1: Threading filters                      │
│  ├── Worker 2: Multiprocessing filters                │
│  └── Worker N: Auto-scaling                           │
│      ↓                                                 │
│  Storage (Processed images)                           │
│      ↓                                                 │
│  Monitoring (Prometheus/Custom)                       │
└─────────────────────────────────────────────────────────┘
```

### **⚖️ COMPLEJIDAD ALCANZABLE:**
**🟢 MÍNIMO (todos deben lograr):**
- 3 filtros funcionando (resize, blur, brightness)
- Threading con speedup >2x vs sequential
- API endpoint funcional
- Docker containers básicos

**🟡 OBJETIVO (mayoría debería lograr):**
- 5+ filtros incluyendo CPU-intensivos
- Multiprocessing + threading coordinados
- Task distribution automática entre workers especializados
- Testing automatizado

**🔴 AVANZADO (algunos lograrán):**
- Fault tolerance completo
- Smart load monitoring system
- CI/CD pipeline full
- Real-time metrics dashboard

### **📊 MÉTRICAS DE ÉXITO:**
- **Performance**: >5x speedup vs secuencial inicial
- **Escalabilidad**: Procesar 10+ imágenes 4K simultáneamente  
- **Disponibilidad**: 99% uptime con worker failures
- **Automation**: Deploy sin intervención manual

### **🚫 QUÉ NO ESTÁ EN SCOPE:**
- Machine Learning / AI
- Frontend web UI (solo API)
- Base de datos compleja
- Kubernetes (solo Docker)
- Monitoring avanzado (Grafana/Prometheus completo)

---

## 🎯 **OBJETIVO GENERAL**

Evolucionar el servidor de imágenes 4K hacia un **pipeline distribuido de procesamiento** que integre:

- ✅ **Threading** (Session 1) → Procesamiento paralelo de imágenes
- ✅ **Multiprocessing** (Session 2) → Workers CPU-intensivos  
- ✅ **Async** (Session 3) → API no-bloqueante
- ✅ **IPC** (Session 4) → Comunicación entre workers
- ✅ **Distributed Systems** (Session 5) → Load balancing y tolerancia a fallos
- ✅ **CI/CD** (Chapter CI) → Docker, testing, deployment

## 📈 **EVOLUCIÓN DEL SISTEMA**

```
DÍA 0 (Lunes): [Servidor básico] → [Sistema distribuido]
DÍA 1 (Martes): [Sistema distribuido] → [Pipeline con threading]
DÍA 2 (Miércoles): [Pipeline threading] → [Workers multiprocessing]
DÍA 3 (Jueves): [Workers locales] → [Workers distribuidos + Docker]
DÍA 4 (Viernes): [Sistema manual] → [CI/CD automatizado + Demo]
```

---

## 📅 **PLANIFICACIÓN DETALLADA**

### **🔥 DÍA 1 - MARTES: Threading + Image Processing Pipeline**
**Objetivo**: Convertir servidor estático → pipeline de procesamiento con threading

#### **📋 Entregables:**
1. **Image Processing API** con threading
2. **Task Queue** para procesar imágenes
3. **Multiple filters** ejecutados en paralelo

#### **🛠️ Tareas (1.75h total):**

**45min Seguimiento (en clase):**
- ✅ Review Session 5 aplicada
- ✅ Setup del pipeline básico
- ✅ Implementar primer filtro con threading
- ✅ Q&A y debugging

**1h Autónoma:**
- ✅ Implementar 3 filtros: resize, blur, brightness
- ✅ ThreadPoolExecutor para procesar múltiples imágenes
- ✅ Progress tracking con threads
- ✅ Testing básico

#### **📂 Archivos a crear/modificar:**
```
Projects/
├── image_api/
│   ├── processors.py      # ← Image processing con threading
│   ├── filters.py         # ← Filtros (resize, blur, etc.)
│   └── tasks.py          # ← Task queue con threading
├── static/processed/      # ← Imágenes procesadas
└── tests/
    └── test_processors.py # ← Tests unitarios
```

#### **🧪 Demo del día:**
```bash
# Upload imagen → API procesa con 3 filtros en paralelo → Download resultados
curl -X POST -F "image=@test.jpg" http://localhost:8000/api/process/
```

---

### **⚡ DÍA 2 - MIÉRCOLES: Multiprocessing + Heavy Processing**
**Objetivo**: Threading → Multiprocessing para tareas CPU-intensivas

#### **📋 Entregables:**
1. **Worker processes** para filtros pesados
2. **Process Pool** escalable
3. **IPC communication** entre API y workers

#### **🛠️ Tareas (1.75h total):**

**45min Seguimiento:**
- ✅ Migrar filtros pesados a multiprocessing
- ✅ Implementar Process Pool
- ✅ Comparar performance: threading vs multiprocessing

**1h Autónoma:**
- ✅ Workers separados por tipo de filtro
- ✅ Queue-based communication (Session 4)
- ✅ Resource monitoring (CPU/memoria)
- ✅ Error handling robusto

#### **📂 Archivos nuevos:**
```
Projects/
├── workers/
│   ├── filter_worker.py   # ← Multiprocessing workers
│   ├── queue_manager.py   # ← IPC con queues
│   └── monitor.py         # ← Resource monitoring
└── benchmarks/
    └── threading_vs_mp.py # ← Performance comparison
```

#### **🧪 Demo del día:**
```bash
# Benchmark: procesar 10 imágenes 4K simultáneamente
python benchmarks/threading_vs_mp.py
```

---

### **🌐 DÍA 3 - JUEVES: Distributed Workers + Docker**
**Objetivo**: Workers locales → Workers distribuidos en containers

#### **📋 Entregables:**
1. **Dockerized workers** independientes
2. **Distributed task queue** (Redis)
3. **Task distribution system** con workers especializados

#### **🛠️ Tareas (1.75h total):**

**45min Seguimiento:**
- ✅ Containerizar workers con Docker
- ✅ Setup Redis para distributed queue
- ✅ Implementar worker discovery

**1h Autónoma:**
- ✅ Docker-compose con múltiples workers
- ✅ Health checks distribuidos
- ✅ Fault tolerance (workers que fallan)
- ✅ Scaling horizontal

#### **📂 Archivos nuevos:**
```
Projects/
├── docker/
│   ├── Dockerfile.worker  # ← Worker container
│   ├── Dockerfile.api     # ← API container
│   └── docker-compose.yml # ← Orchestration
├── distributed/
│   ├── redis_queue.py     # ← Distributed queue
│   ├── worker_registry.py # ← Service discovery
│   └── load_balancer.py   # ← Distribute tasks
└── config/
    └── cluster.yml        # ← Cluster configuration
```

#### **🧪 Demo del día:**
```bash
# Levantar cluster de 3 workers + API + Redis
docker-compose up --scale worker=3
curl -X POST -F "image=@huge_4k.jpg" http://localhost:8000/api/process/
```

---

### **🚀 DÍA 4 - VIERNES: Sistema de Monitoreo Real + Stress Testing** ✅ **COMPLETADO**
**Objetivo**: Sistema básico → Sistema con métricas reales y debugging production

#### **📋 Entregables Alcanzados:**
1. **Sistema de métricas real** con CPU/Memory tracking ✅
2. **Worker utilization monitoring** en tiempo real ✅
3. **Scaling recommendations** educativas (sin ejecución automática) ✅ 
4. **5 scripts de stress testing** para generar carga controlada ✅
5. **Dashboard tiempo real** via terminal CLI ✅
6. **Debugging sistemático** de problemas reales (timeouts, métricas) ✅

#### **🛠️ Tareas Completadas (1.75h total):**

**45min Seguimiento:**
- ✅ Implementar sistema de métricas con psutil
- ✅ Crear 5 tipos de stress tests (burst, continuous, simple, etc.)
- ✅ Resolver problemas de Docker containers usando código viejo
- ✅ Debugging de métricas incorrectas y API timeouts

**1h Autónoma:**
- ✅ Sistema funcionando: ver workers pasar de 0% a 100% utilización
- ✅ Monitoreo que cambia recomendaciones basado en carga real
- ✅ Documentation completa con troubleshooting real
- ✅ Demo funcional: métricas cambian en < 5 segundos

#### **📂 Archivos Reales Creados:**
```
Projects/
├── simple_monitoring/           # ← Sistema de monitoreo real
│   ├── __init__.py
│   ├── cli.py                  # ← Terminal CLI para métricas
│   ├── metrics_collector.py    # ← Recopilación de métricas real
│   ├── recommendations.py      # ← Lógica de recomendaciones
│   └── dashboard.py            # ← Dashboard tiempo real
├── stress testing scripts/      # ← 2 tipos de stress tests (limpio)
│   ├── burst_stress.py         # ← Carga rápida/paralela (50 tareas)
│   └── continuous_stress.py    # ← Carga sostenida (5/seg x tiempo)
└── README.md                   # ← Documentation completa con troubleshooting real
```

#### **🎭 Demo Real Funcional:**
```bash
# Demo completo de monitoreo (< 5 segundos para ver resultados)
1. python simple_monitoring/cli.py metrics   # ⚡ Busy Workers: 0
2. python burst_stress.py 50               # Lanzar 50 tareas concurrentes  
3. python simple_monitoring/cli.py metrics   # ⚡ Busy Workers: 3 (100% utilization)
4. Ver recomendaciones cambiar: MAINTAIN vs SCALE_UP
5. Dashboard en tiempo real: python simple_monitoring/cli.py monitor

# Troubleshooting demo (problemas reales resueltos)
- API timeouts → Solución: endpoint async
- Métricas incorrectas → Solución: rebuild Docker container
- Workers 0% utilization → Solución: corregir metrics_collector.py
```

---

## 🎯 **CRITERIOS DE ÉXITO**

### **Funcionalidad:**
- ✅ API procesa imágenes con múltiples filtros
- ✅ Threading + Multiprocessing coordinados
- ✅ Workers distribuidos en Docker
- ✅ Sistema tolera fallos
- ✅ CI/CD pipeline funcional

### **Performance:**
- ✅ >3x speedup vs secuencial
- ✅ Escala horizontalmente (más workers = más throughput)
- ✅ <2s latencia para imagen 4K
- ✅ 99% uptime con failover

### **Arquitectura:**
- ✅ Modular y extensible
- ✅ Logs y monitoring
- ✅ Tests automatizados
- ✅ Documentation completa

---

## 📊 **MATRIZ DE HABILIDADES**

| Día | Threading | Multiprocessing | Async | IPC | Distributed | Docker | CI/CD |
|-----|-----------|-----------------|-------|-----|-------------|---------|-------|
| 1   | 🔥🔥🔥   | ⚪             | ⚪    | ⚪  | ⚪          | ⚪      | ⚪    |
| 2   | 🔥        | 🔥🔥🔥         | ⚪    | 🔥🔥| ⚪          | ⚪      | ⚪    |
| 3   | 🔥        | 🔥             | 🔥    | 🔥  | 🔥🔥🔥      | 🔥🔥🔥  | ⚪    |
| 4   | 🔥        | 🔥             | 🔥    | 🔥  | 🔥          | 🔥      | 🔥🔥🔥|

---

## 🛠️ **RECURSOS Y HERRAMIENTAS**

### **Librerías Python:**
```python
# Image processing
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import numpy as np

# Concurrency
import threading
import multiprocessing
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Distributed
import redis
import requests
import docker

# Monitoring
import psutil
import prometheus_client
```

### **Infraestructura:**
- **Redis**: Distributed task queue
- **Docker**: Containerización
- **GitHub Actions**: CI/CD
- **Prometheus**: Monitoring (opcional)

### **Testing:**
- **pytest**: Unit testing
- **load testing**: Performance
- **integration tests**: End-to-end

---

## 🚨 **CONTINGENCIAS**

### **Si van retrasados:**
- **Día 1**: Enfocarse solo en threading básico
- **Día 2**: Saltar multiprocessing, usar threading avanzado
- **Día 3**: Docker simple sin orchestration
- **Día 4**: GitHub Actions básico + demo simple

### **Si van adelantados:**
- **Extensiones**: Machine learning filters, real-time streaming, web UI
- **Optimizaciones**: Caching, batch processing, GPU acceleration
- **Monitoring**: Grafana dashboards, alerting

### **Problemas técnicos comunes:**
- **Docker issues**: Usar virtual environments
- **Redis setup**: Usar in-memory queue
- **Performance**: Focus en correctness over speed

---

## 🎓 **EVALUACIÓN FINAL**

### **Demo Presentation (20 min):**
1. **Architecture overview** (5 min)
2. **Live processing demo** (10 min)
3. **Performance comparison** (3 min)
4. **Q&A** (2 min)

### **Entregables:**
- ✅ **Código funcionando** en GitHub
- ✅ **Documentation** completa
- ✅ **Demo video** (opcional)
- ✅ **Performance report**

---

**🎯 ¡Proyecto diseñado para aplicar TODOS los conceptos de concurrencia en un sistema real y escalable!** 🚀 
# 🖼️ Pipeline de Procesamiento de Imágenes Distribuido

**Proyecto de 4 días: De Threading a Sistemas Distribuidos con Monitoreo Real** ✅

Este proyecto evoluciona desde un servidor Django básico hasta un **sistema distribuido de procesamiento de imágenes** completo con **monitoreo en tiempo real**, demostrando conceptos de concurrencia, paralelismo, arquitecturas distribuidas y métricas de producción.

## 🎯 Objetivos del Proyecto

### **📅 DÍA 1: Foundation** 
- ✅ **I/O-bound operations**: Leer archivos grandes del disco
- ✅ **Threading vs Multiprocessing**: Comparación de rendimiento  
- ✅ **Load testing**: Medición de concurrencia

### **📅 DÍA 2: Real Processing**
- ✅ **Filtros reales**: PIL (Pillow) y OpenCV 
- ✅ **CPU-bound tasks**: Blur, sharpen, edge detection, resize
- ✅ **Performance benchmarking**: Sequential vs Threading vs Multiprocessing
- ✅ **Resource monitoring**: CPU, memory, processing time

### **📅 DÍA 3: Distributed System** 
- ✅ **Sistema distribuido**: Redis + Worker containers
- ✅ **Task distribution**: FIFO queue distribuyendo tareas entre workers especializados
- ✅ **Fault tolerance**: Worker registration, heartbeat, failure handling
- ✅ **Docker orchestration**: docker-compose con múltiples servicios
- ✅ **Monitoring**: Worker status, task tracking, performance metrics

### **📅 DÍA 4: Smart Monitoring & Metrics** ✅ **COMPLETADO**
- ✅ **Sistema de métricas real**: CPU, memoria, utilización de workers en tiempo real
- ✅ **Detección de carga**: Queue length, busy workers, success rate
- ✅ **Recomendaciones educativas**: Cuándo escalar workers (sin ejecución automática)
- ✅ **Dashboard tiempo real**: Terminal UI mostrando métricas en vivo
- ✅ **Stress testing funcional**: Scripts para generar carga y ver métricas cambiar
- ✅ **Debugging completo**: Resueltos timeouts, métricas incorrectas, Docker issues

### **📅 DÍA 5: Real Auto-Scaling con Kubernetes** ✅ **COMPLETADO**
- ✅ **Migración a Kubernetes**: De docker-compose a K8s deployments
- ✅ **Imágenes optimizadas**: Reducción de 6GB → 2.2GB (63% optimización)
- ✅ **Horizontal Pod Autoscaler (HPA)**: Auto-scaling real basado en CPU/memoria
- ✅ **Metrics Server**: Configuración específica para Docker Desktop
- ✅ **Cross-platform**: Compatible con Windows, macOS (ARM64/Intel) y Linux
- ✅ **Demo funcional**: Auto-scaling funcionando con métricas reales
- ✅ **Troubleshooting completo**: Solución de errores comunes de K8s en desarrollo

## 🏗️ Arquitectura del Sistema

```
                    🌐 Client
                (curl requests)
                       |
                   🐍 Django API
                    :8000
                 (Single Instance)
                       |
                📡 Redis Queue
              (Task Distribution
               Worker Registry)
                   /  |  \
                  /   |   \
                 /    |    \
            👷 Worker-1  👷 Worker-2  👷 Worker-3
           I/O Specialist CPU Specialist General Purpose
           resize, blur,   sharpen,      ALL FILTERS
           brightness     edges            |
                |           |              |
                |           |              |
           🖼️ Static Images ←→ 💾 Processed Images
           sample_4k.jpg      static/processed/
           misurina-sunset.jpg
                
    📊 Smart Monitoring System (Day 4) ✅
    ├── 🔥 CPU Usage & 🧠 Memory Usage (psutil)
    ├── ⚡ Busy Workers & 📈 Worker Utilization  
    ├── 📋 Queue Length & ✅ Success Rate
    ├── 🎬 Scaling Recommendations (Educational)
    ├── 📊 Real-time Terminal Dashboard
    └── 🚀 Stress Testing Scripts (5 tipos)
```

### **🔄 Flujo de Procesamiento:**

```
1. 📤 Client: POST /api/process-batch/distributed/
                    ↓
2. 🐍 Django API: Crea task_id único y encola en Redis (LPUSH)
                    ↓
3. 📡 Redis Queue: [task1, task2, task3] → Workers pull (BRPOP)
                    ↓
4. 👷 Worker: Toma próximo task disponible (FIFO)
                    ↓
5. 🔍 Worker: Revisa capabilities DESPUÉS de tomar task
                    ↓
6a. ✅ Compatible: Procesa filtros → Guarda en static/processed/
6b. ❌ Incompatible: Marca task como FAILED (💀 Tarea perdida)
                    ↓
7. 📊 Client: Consulta status con /api/task/{task_id}/status/
```

## 🚀 Setup y Ejecución

### **Opción A: Setup Local (Días 1-2)**

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear directorios necesarios
mkdir -p static/processed

# 3. Ejecutar servidor local
python manage.py runserver 8000
```

### **Opción B: Setup Distribuido con Docker (Día 3)**

```bash
# 1. Construir imágenes
docker-compose build

# 2. Levantar sistema completo
docker-compose up -d

# 3. Verificar servicios
docker-compose ps
```

### **Verificar instalación:**
```bash
# Health check
curl http://localhost:8000/api/health/

# Ver workers activos (solo Docker)
curl http://localhost:8000/api/workers/status/
```

## ⚡ **DEMO RÁPIDO: Ver Métricas Cambiar** 

**🎯 Para ver el sistema funcionando inmediatamente:**

```bash
# Terminal 1: Ver métricas limpias
python simple_monitoring/cli.py metrics
# ⚡ Busy Workers: 0    📈 Utilization: 0.0%

# Terminal 2: Lanzar stress test  
cd k8s && python stress_test.py 3 15

# Terminal 1: Ver métricas cambiar INMEDIATAMENTE
python simple_monitoring/cli.py metrics  
# ⚡ Busy Workers: 3    📈 Utilization: 100.0%
# 🎬 Action: MAINTAIN   📝 Reason: System at optimal capacity
```

**🔥 Resultado**: En **< 5 segundos** verás workers pasar de 0% a 100% utilización con recomendaciones inteligentes.

## 🧪 Testing y Comandos

### **📅 DÍA 1: Endpoints Básicos**

```bash
# Health check
curl http://localhost:8000/api/health/

# Información de imagen (rápido)
curl http://localhost:8000/api/image/info/

# Descargar imagen 4K (I/O-bound)  
curl http://localhost:8000/api/image/4k/ -o downloaded_4k.jpg

# Imagen con procesamiento lento
curl "http://localhost:8000/api/image/slow/?delay=3.0" -o slow_4k.jpg

# Estadísticas del servidor
curl http://localhost:8000/api/stats/
```

### **📅 DÍA 2: Filtros Reales (PIL/OpenCV)**

```bash
# Procesamiento con filtros secuencial
curl -X POST http://localhost:8000/api/process-batch/sequential/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["resize", "blur"], "filter_params": {"resize": {"width": 800, "height": 600}, "blur": {"radius": 3.0}}}'

# Procesamiento con threading
curl -X POST http://localhost:8000/api/process-batch/threading/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["sharpen", "edges"]}'

# Procesamiento con multiprocessing
curl -X POST http://localhost:8000/api/process-batch/multiprocessing/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["brightness"], "filter_params": {"brightness": {"factor": 1.5}}}'

# Comparar todos los métodos
curl -X POST http://localhost:8000/api/process-batch/compare-all/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["resize", "blur"]}'

# Stress test
curl -X POST http://localhost:8000/api/process-batch/stress/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["sharpen", "edges"], "num_iterations": 5}'
```

### **📅 DÍA 3: Sistema Distribuido (Docker)**

```bash
# Procesamiento distribuido
curl -X POST http://localhost:8000/api/process-batch/distributed/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["resize", "sharpen", "edges"], "filter_params": {"resize": {"width": 1024, "height": 768}}}'

# Estado de workers
curl http://localhost:8000/api/workers/status/ | python -m json.tool

# Monitoreo en tiempo real
watch -n 2 'curl -s http://localhost:8000/api/workers/status/ | python -m json.tool'

# Consultar estado de task individual (usar task_id de la respuesta anterior)
curl http://localhost:8000/api/task/{TASK_ID}/status/ | python -m json.tool
```

### **🎯 Testing Worker Specialization**

```bash
# Test: Solo worker-2 puede hacer 'sharpen'
# 1. Parar worker-3: docker-compose stop worker-3
# 2. Enviar múltiples tareas sharpen:
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/process-batch/distributed/ \
    -H "Content-Type: application/json" \
    -d '{"filters": ["sharpen"]}' &
done

# 3. Ver resultados: worker-1 falla, worker-2 procesa
curl http://localhost:8000/api/workers/status/
```

### **🔍 Testing Job Failure vs Worker Failure**

```bash
# SCENARIO 1: Job Failure (Worker incompatible)
# 1. Enviar task que worker-1 no puede manejar
curl -X POST http://localhost:8000/api/process-batch/distributed/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["sharpen"]}' \
  | jq '.task_id' # Guardar task_id

# 2. Consultar status específico del job
curl http://localhost:8000/api/task/{TASK_ID}/status/ | jq '
{
  status: .status,
  failure_type: .failure_type,
  failure_reason: .failure_reason,
  explanation: .explanation,
  error: .error
}'

# RESPUESTA de Job Failure:
# {
#   "status": "failed",
#   "failure_type": "job_failure",
#   "failure_reason": "worker_capability_mismatch", 
#   "explanation": "Worker tomó task pero no puede manejar el filtro requerido",
#   "error": "Worker worker-1 cannot handle filters: ['sharpen']"
# }

# SCENARIO 2: Worker Failure (Worker caído)
# 1. Parar todos los workers
docker-compose stop worker-1 worker-2 worker-3

# 2. Enviar task
curl -X POST http://localhost:8000/api/process-batch/distributed/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["resize"]}' \
  | jq '.task_id'

# 3. Consultar después de timeout
curl http://localhost:8000/api/task/{TASK_ID}/status/ | jq '
{
  status: .status,
  explanation: "No workers available to process task"
}'

# RESPUESTA de Worker Failure:
# {
#   "status": "pending",  # Task nunca fue tomada
#   "explanation": "No workers available to process task"
# }
```

## 📊 Endpoints Disponibles

### **DÍA 1: Básicos**
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/health/` | GET | Health check del servidor |
| `/api/image/info/` | GET | Metadata de imagen sin transferir |
| `/api/image/4k/` | GET | Descargar imagen 4K (I/O-bound) |
| `/api/image/slow/?delay=N` | GET | Imagen con delay simulado |
| `/api/stats/` | GET | Estadísticas del servidor |

### **DÍA 2: Procesamiento Real**
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/process-batch/sequential/` | POST | Procesamiento secuencial con filtros |
| `/api/process-batch/threading/` | POST | Procesamiento con threading |
| `/api/process-batch/multiprocessing/` | POST | Procesamiento con multiprocessing |
| `/api/process-batch/compare/` | POST | Comparar threading vs multiprocessing |
| `/api/process-batch/compare-all/` | POST | Comparar todos los métodos |
| `/api/process-batch/stress/` | POST | Test de estrés con múltiples iteraciones |

### **DÍA 3: Sistema Distribuido**
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/process-batch/distributed/` | POST | Procesamiento distribuido con workers |
| `/api/workers/status/` | GET | Estado de todos los workers |
| `/api/task/<task_id>/status/` | GET | **Estado de task individual** (job failure vs worker failure) |

### **DÍA 4: Sistema de Monitoreo** ✅
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/metrics/` | GET | **Métricas del sistema** (CPU, memoria, workers, recomendaciones) |

### **Comandos CLI de Monitoreo:**
| Comando | Descripción |
|---------|-------------|
| `python simple_monitoring/cli.py check` | Verificar API disponible |
| `python simple_monitoring/cli.py metrics` | Ver métricas actuales |
| `python simple_monitoring/cli.py monitor` | Dashboard en tiempo real |
| `python simple_monitoring/cli.py stress 10` | Stress test via API |

### **Comandos de Limpieza:**
| Comando | Descripción |
|---------|-------------|
| **Limpiar imágenes procesadas:** | `rm -rf static/processed/*` (Linux/Mac) |
| | `Remove-Item static\processed\* -Force` (PowerShell) |
| | `del /q static\processed\*` (CMD Windows) |
| **Purgar Redis (Docker):** | `docker exec image_processing_redis redis-cli FLUSHALL` |
| **Purgar Redis (K8s):** | `kubectl exec deployment/redis-deployment -- redis-cli FLUSHALL` |

### **Filtros Disponibles:**
- **`resize`**: Cambiar tamaño (PIL) - I/O-bound
- **`blur`**: Difuminado gaussiano (PIL) - I/O-bound  
- **`brightness`**: Ajuste de brillo (PIL) - I/O-bound
- **`sharpen`**: Nitidez avanzada (OpenCV) - CPU-bound
- **`edges`**: Detección de bordes (OpenCV) - CPU-bound

## 🔍 Análisis de Rendimiento

### **🏃‍♂️ DÍA 2: Threading vs Multiprocessing**

**Para filtros I/O-bound (resize, blur, brightness):**
- ✅ **Threading wins**: ~3-5x más rápido que secuencial
- ⚡ **Multiprocessing**: ~2-3x más rápido (overhead de procesos)
- 🧠 **Razón**: GIL se libera durante I/O, threading es más eficiente

**Para filtros CPU-bound (sharpen, edges):**
- ✅ **Multiprocessing wins**: ~4-6x más rápido que secuencial  
- 🐌 **Threading**: ~1.2x más rápido (limitado por GIL)
- 🧠 **Razón**: CPU-bound necesita verdadero paralelismo

### **🌐 DÍA 3: Sistema Distribuido**

**Características del FIFO Queue:**
- ⚖️ **Load Balancing**: Simple FIFO, no inteligente
- ❌ **Fault Tolerance**: Tareas fallan si worker incompatible las toma
- 🎯 **Worker Specialization**: Configurado por `WORKER_CAPABILITIES`
- 📊 **Monitoring**: Worker registry con heartbeat

**Worker-3 como "Salvador":**
- 🛡️ Worker-3 (`capabilities=all`) previene fallos
- 🎲 Distribución basada en timing, no capabilities
- ⚠️ Si worker-3 se cae, tareas incompatibles fallan para siempre

## 📊 **DÍA 4: Sistema de Monitoreo Real** ✅

### **🎯 Métricas en Tiempo Real**

El sistema incluye **monitoreo inteligente** que recopila métricas reales del sistema:

```bash
# Ver métricas actuales
python simple_monitoring/cli.py metrics

# Resultado example:
📊 SYSTEM METRICS
========================================
🔥 CPU Usage:          30.5%
🧠 Memory Usage:       69.5%
💽 Memory Available:    2.3 GB

⚙️ WORKER METRICS
--------------------
👥 Active Workers:        3
⚡ Busy Workers:          3
📈 Utilization:      100.0%
📋 Queue Length:          0
✅ Success Rate:      100.0%

🎓 SCALING RECOMMENDATION (Educational)
----------------------------------------
📊 Current Workers:       3
🎯 Recommended:           3
🎬 Action:           MAINTAIN
📝 Reason:           System operating within optimal parameters
🎯 Confidence:        80.0%
⚡ Urgency:          NONE
```

### **🚀 Stress Testing Scripts**

**Script unificado de stress test** multiplataforma para generar carga:

```bash
cd k8s
# Uso: python stress_test.py [minutos] [tareas_por_batch]

# 1. BURST STRESS - Carga rápida (Kubernetes auto-scaling)
python stress_test.py 5 20       # 5 minutos, 20 tareas por batch

# 2. CONTINUOUS STRESS - Carga sostenida  
python stress_test.py 10 15      # 10 minutos, 15 tareas por batch
```

### **📈 Ver Métricas Cambiar en Tiempo Real**

```bash
# Terminal 1: Lanzar stress test
cd k8s && python stress_test.py 5 15

# Terminal 2: Ver métricas cambiar inmediatamente  
python simple_monitoring/cli.py metrics

# Antes del stress:
⚡ Busy Workers: 0    📈 Utilization: 0.0%

# Durante el stress:
⚡ Busy Workers: 3    📈 Utilization: 100.0%
🎬 Action: MAINTAIN   📝 Reason: System at optimal capacity
```

### **🎛️ Dashboard en Tiempo Real**

```bash
# Terminal interactivo con métricas en vivo
python simple_monitoring/cli.py monitor

# Actualiza métricas cada 2 segundos mostrando:
# - CPU/Memory usage en tiempo real
# - Worker utilization dinámica  
# - Recomendaciones que cambian con la carga
# - Success rate y estadísticas
```

## 🛠️ Troubleshooting

### **Local Setup Issues**
```bash
# Dependencias faltantes
pip install -r requirements.txt

# Directorios faltantes  
mkdir -p static/processed static/images

# Puerto en uso
python manage.py runserver 8080
```

### **Docker Issues**
```bash
# Servicios no inician
docker-compose down && docker-compose up --build

# Redis connection failed
docker-compose logs redis

# Workers no registran
docker-compose logs worker-1
```

### **Workers No Processan**
```bash
# Verificar workers activos
curl http://localhost:8000/api/workers/status/

# Verificar cola Redis
docker-compose exec redis redis-cli LLEN task_queue

# Restart workers
docker-compose restart worker-1 worker-2 worker-3
```

### **📊 Problemas de Monitoreo (Resueltos)** ✅

```bash
# PROBLEMA: Métricas muestran "Busy Workers: 0" durante alta carga
# CAUSA: API container usando código viejo
# SOLUCIÓN: Rebuild agresivo del container
docker-compose stop api && docker-compose rm -f api
docker rmi projects-api
docker-compose build api --no-cache && docker-compose up -d api

# PROBLEMA: API timeouts durante stress tests  
# CAUSA: API esperando sincrónicamente tareas distribuidas
# SOLUCIÓN: Endpoint distribuido retorna task_id inmediatamente

# PROBLEMA: Métricas incorrectas en Redis
# CAUSA: Datos viejos acumulados de tests anteriores
# SOLUCIÓN: Purgar Redis entre tests
docker exec image_processing_redis redis-cli FLUSHALL

# VERIFICAR: Métricas funcionando correctamente
python simple_monitoring/cli.py metrics
# Debe mostrar busy workers > 0 durante carga alta
```

## 🏆 Logros del Proyecto

### **📈 Progresión Técnica:**
1. **Día 1**: Servidor básico I/O-bound → Threading fundamentals
2. **Día 2**: Filtros reales PIL/OpenCV → CPU vs I/O bound analysis  
3. **Día 3**: Sistema distribuido → Redis, Docker, Load balancing
4. **Día 4**: **Sistema de monitoreo completo** → Métricas reales, stress testing, debugging

### **🎯 Conceptos Demostrados:**
- ✅ **GIL Impact**: Threading vs Multiprocessing en diferentes workloads
- ✅ **Real-world Libraries**: PIL, OpenCV, Redis en production
- ✅ **Distributed Architectures**: Message queues, worker pools, fault tolerance
- ✅ **DevOps Integration**: Docker, docker-compose, multi-service systems
- ✅ **Performance Analysis**: Benchmarking, monitoring, bottleneck identification
- ✅ **Real-time Monitoring**: CPU/Memory tracking, worker utilization metrics
- ✅ **Stress Testing**: 5 tipos de scripts para generar carga controlada
- ✅ **Production Debugging**: Resolver timeouts, métricas incorrectas, Docker issues

### **🚀 Logros Únicos de este Proyecto:**
- 🎯 **Métricas que cambian en tiempo real** - Ver utilización de workers subir de 0% a 100%
- 🔄 **Debugging sistemático** - Resolver problemas reales de desarrollo distribuido
- 📊 **Monitoreo educativo** - Recomendaciones de scaling sin ejecución automática  
- ⚡ **Stress testing científico** - Scripts controlados para generar cargas específicas
- 🐳 **Docker debugging avanzado** - Resolver containers usando código viejo
- 📈 **Performance real** - 300+ tareas procesadas, workers al 100% utilización

---

**🚀 De conceptos básicos de concurrencia a sistemas distribuidos con monitoreo real en 4 días!**

## 🖥️ **SETUP PARA WINDOWS**

### **Instalación rápida:**
```cmd
# 1. Ir a Projects folder
cd ProgrammingCourse\Chapter-Threads\Projects

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear directorio
mkdir static\processed

# 5. Verificar
python manage.py check

# 6. Iniciar servidor
python manage.py runserver 8000
```

### **Endpoints disponibles por día:**

**📅 Día 1-2 (Threading/Multiprocessing):**
- `/api/process-batch/sequential/` - Procesamiento secuencial
- `/api/process-batch/threading/` - Con threading  
- `/api/process-batch/multiprocessing/` - Con multiprocessing
- `/api/process-batch/compare-all/` - Comparar todos los métodos

**📅 Día 3-4 (Distributed + Monitoring):**
- `/api/process-batch/distributed/` - Sistema distribuido con Redis + Workers
- `/api/metrics/` - Métricas del sistema en tiempo real

**📅 Día 5 (Kubernetes):**
- **Mismo endpoint:** `/api/process-batch/distributed/` 
- **Diferencia:** Ahora corre en **pods auto-escalables** 🚀

### **Ejemplo de uso en K8s:**
```bash
# 1. Port-forward EN OTRA TERMINAL (se queda corriendo):
kubectl port-forward service/api-service 8000:8000

# 2. Ahora puedes usar el mismo endpoint desde tu PC:
curl -X POST http://localhost:8000/api/process-batch/distributed/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["resize", "blur"]}'
```

**💡 TIP:** El port-forward es como un "cable virtual" que conecta tu PC con Kubernetes.

---

## 🚀 **KUBERNETES: Auto-Scaling Real (Día 5)**

### **🎯 ¿Por qué Kubernetes?**

Docker Compose es excelente para desarrollo, pero tiene limitaciones:
- ❌ **No hay auto-scaling real** - Los nombres de containers son fijos
- ❌ **Scaling manual** - `docker-compose scale worker=5` no es automático
- ❌ **Sin métricas integradas** - No puede escalar basado en CPU/memoria

**Kubernetes soluciona esto con:**
- ✅ **Auto-scaling automático** - HPA (Horizontal Pod Autoscaler)
- ✅ **Métricas integradas** - CPU, memoria, métricas custom
- ✅ **Escalado inteligente** - Basado en carga real
- ✅ **Tolerancia a fallos** - Pods se recrean automáticamente

### **📊 Arquitectura Kubernetes**

```
                    🌐 Client
                (kubectl port-forward)
                       |
                   🐍 API Service
                  (LoadBalancer)
                       |
                📡 Redis Service 
               (ClusterIP)
                   /  |  \
                  /   |   \
             👷 Worker Pod  👷 Worker Pod  
            (CPU: 100m-200m) (Memory: 128Mi-256Mi)
                  |               |
                  └─── HPA ───────┘
               (CPU target: 70%)
              (Memory target: 80%)
                      |
               📊 Metrics Server
              (Recolecta métricas)
```

### **🔧 Quick Start: Demo Kubernetes**

#### **1. Prerequisitos:**
```bash
# Verificar que Kubernetes esté habilitado en Docker Desktop
kubectl version --client
kubectl cluster-info
```

#### **2. Setup automático (recomendado):**
```bash
# Setup completo (Docker + Kubernetes)
python setup.py

# O setup por partes:
python setup.py --docker-only    # Solo Docker Compose
python setup.py --k8s-only       # Solo Kubernetes
python setup.py --check          # Verificar prerequisitos
```

#### **2b. Build manual (alternativo):**
```bash
# Construir imágenes optimizadas (2.2GB vs 6GB originales)
python build.py

# Si los cambios no se aplican (problema común en Windows):
python build.py --clean
# O build sin caché:
docker build --no-cache -f docker/Dockerfile.api.final -t projects-api-final:latest .

# Verificar imágenes
docker images | grep projects-.*-final
```

#### **3. Ejecutar demo completo (multiplataforma):**
```bash
cd k8s
python demo.py
```

**🌟 NUEVO: Demo 100% multiplataforma:**
- ✅ **Windows**: Detecta PowerShell automáticamente, usa `find /c` en lugar de `wc -l`
- ✅ **Linux/Mac**: Usa comandos nativos `curl` y `grep`
- ✅ **Auto-detección**: Detecta si `requests` está disponible para stress test avanzado
- ✅ **Fallback inteligente**: Si falta `requests`, usa `curl` multiplataforma

El demo automáticamente:
- ✅ **Despliega Redis, API y Workers**
- ✅ **Configura HPA optimizado** (escalado rápido + descalado en 1min)
- ✅ **Instala Metrics Server** (específico para Docker Desktop)
- ✅ **Stress test real** con procesamiento de imágenes
- ✅ **Muestra escalado Y descalado** en tiempo real
- ✅ **Verifica que todo funcione**
- ✅ **Muestra métricas reales**: `cpu: 1%/70%, memory: 27%/80%`

### **📊 ¿Qué es el Metrics Server y por qué es necesario?**

#### **🤔 Problema sin Metrics Server:**
```bash
kubectl get hpa
NAME         TARGETS
worker-hpa   <unknown>/70%  ❌ HPA "ciego" - no puede medir
```

#### **✅ Solución con Metrics Server:**
```bash
kubectl get hpa  
NAME         TARGETS
worker-hpa   cpu: 1%/70%, memory: 27%/80%  ✅ HPA "inteligente" 
```

#### **🔍 ¿Por qué hay que instalarlo?**

**En clusters reales (producción):**
- **AWS EKS, Google GKE, Azure AKS:** ✅ Viene preinstalado

**En desarrollo local:**
- **Docker Desktop, minikube, kind:** ❌ Hay que instalarlo manualmente

#### **🎯 ¿Cómo funciona?**
```mermaid
graph TD
    A[Pods ejecutándose] --> B[Metrics Server]
    B --> C[Recolecta CPU/Memory cada 15s]
    C --> D[HPA Controller]
    D --> E{CPU > 70%?}
    E -->|Sí| F[kubectl scale deployment worker +2 pods]
    E -->|No| G[Mantener pods actuales]
    F --> A
    G --> A
```

**Analogía:** Es como un **termostato con termómetro**
- **Sin metrics server:** Termostato sin termómetro (no sabe la temperatura)
- **Con metrics server:** Puede medir y tomar decisiones inteligentes

### **⚡ Configuración de Descalado Optimizada**

**🚨 Problema común:** El descalado por defecto es MUY lento (5 minutos)
```yaml
# ❌ ANTES: Configuración por defecto
# stabilizationWindowSeconds: 300  # 5 minutos!
```

**✅ SOLUCIÓN: HPA optimizado para demos:**
```yaml
behavior:
  scaleUp:
    stabilizationWindowSeconds: 30  # Escalado rápido: 30s
    policies:
    - type: Percent
      value: 100  # Puede duplicar pods inmediatamente
      periodSeconds: 60
  scaleDown:
    stabilizationWindowSeconds: 60   # Descalado rápido: 1min (vs 5min)
    policies:
    - type: Percent
      value: 50   # Puede remover 50% de pods por minuto
      periodSeconds: 60
```

**🎯 Resultado:** 
- **Escalado**: 2 → 8 pods en ~1 minuto
- **Descalado**: 8 → 2 pods en ~2 minutos (vs 10+ minutos por defecto)

### **🔧 Comandos Útiles**

#### **Ver auto-scaling en tiempo real:**
```bash
# Terminal 1: Ver HPA cambiando
kubectl get hpa -w

# Terminal 2: Ver pods escalando  
kubectl get pods -w

# Terminal 3: Generar carga CPU
kubectl exec -it deployment/worker-deployment -- sh -c "while true; do :; done"
```

#### **Métricas y debugging:**
```bash
# Ver métricas de nodos
kubectl top nodes

# Ver métricas de pods
kubectl top pods

# Describir HPA (troubleshooting)
kubectl describe hpa worker-hpa

# Ver logs de un pod específico
kubectl logs deployment/worker-deployment --tail=20
```

#### **Port forwarding para testing:**

**🔌 ¿Por qué necesito port-forward?**
- **Sin port-forward:** API solo accesible dentro del cluster de Kubernetes
- **Con port-forward:** Puedes usar `localhost:8000` desde tu PC como siempre

**⚠️ IMPORTANTE: Port-forward se ejecuta en una terminal separada porque es un proceso que queda corriendo:**

```bash
# Terminal 1 (se queda "ocupada" escuchando):
kubectl port-forward service/api-service 8000:8000
# ↑ Este comando NO termina - crea un "puente" entre tu PC y Kubernetes
# Forwarding from 127.0.0.1:8000 -> 8000
# [Se queda aquí corriendo...]

# Terminal 2 (libre para usar la API):
curl -X POST http://localhost:8000/api/process-batch/distributed/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["resize", "blur"]}'

# O ejecutar script de stress unificado:
cd k8s
python stress_test.py 5 10  # 5 minutos, 10 tareas por batch
```

**💡 Alternativa (una sola terminal):**
```bash
# Ejecutar en background con &
kubectl port-forward service/api-service 8000:8000 &

# Ahora puedes seguir usando la misma terminal
curl http://localhost:8000/api/process-batch/distributed/
```

### **⚠️ Troubleshooting Común**

#### **🌍 Diferencias de Plataforma (Automáticamente detectadas)**

**✅ Windows (detectado automáticamente):**
- **Encoding**: Usa UTF-8 automáticamente para evitar errores de emojis
- **Comandos**: Reemplaza `grep` con `findstr` y `wc -l` con `find /c`
- **curl**: Detecta PowerShell y usa `Invoke-WebRequest` cuando es necesario
- **Paths**: Maneja rutas de Windows correctamente

**✅ Linux/Mac (detectado automáticamente):**
- **Comandos**: Usa comandos nativos `grep`, `wc`, `curl`
- **Paths**: Maneja rutas Unix/POSIX

#### **🐛 Windows: Error de emojis/encoding**
```powershell
# Error: UnicodeEncodeError: 'charmap' codec can't encode character
# Solución: ✅ Ya arreglado automáticamente en demo.py (UTF-8 encoding)
```

#### **🐛 Windows: Comandos grep no funcionan**
```powershell
# Error: 'grep' is not recognized as an internal or external command
# Solución: ✅ Ya arreglado automáticamente - demo.py detecta Windows y usa comandos compatibles
```

#### **🐛 Windows: curl en PowerShell**
```powershell
# Error: curl da "Connection terminated unexpectedly"
# Solución: ✅ Ya arreglado automáticamente - demo.py usa Invoke-WebRequest cuando es necesario

# Fallback manual si necesario:
curl.exe http://localhost:8000/api/metrics/
# O PowerShell nativo:
Invoke-WebRequest -Uri http://localhost:8000/api/metrics/ | Select-Object -ExpandProperty Content
```

#### **🐛 Dependencias Python faltantes**
```bash
# Error: ModuleNotFoundError: No module named 'requests'
# Solución: ✅ demo.py detecta automáticamente y usa curl como fallback

# Para stress test completo (opcional):
pip install requests
```

#### **🐛 Docker caché problemático**
```bash
# Problema: Cambios en Dockerfile no se aplican
# Solución: Rebuild sin caché
docker build --no-cache -f docker/Dockerfile.api.final -t projects-api-final:latest .

# O usar tag único:
docker build -f docker/Dockerfile.api.final -t projects-api-final:v2 .
kubectl set image deployment/api-deployment api=projects-api-final:v2
```

#### **Error: `ErrImageNeverPull`**
```bash
# Problema: Docker Compose crea imágenes con sufijos numéricos
docker images | grep projects
# projects-worker-1  ❌
# projects-worker-2  ❌

# Solución: Tag manual
docker tag projects-worker-1:latest projects-worker-final:latest
```

#### **Error: HPA muestra `<unknown>`**
```bash
# Problema: Metrics server no funciona
kubectl get hpa
# worker-hpa   <unknown>/70%  ❌

# Solución: Configurar metrics server para Docker Desktop
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

#### **Error: Pods en `CrashLoopBackOff`**
```bash
# Ver logs para diagnosticar
kubectl logs deployment/worker-deployment --tail=20

# Errores comunes:
# - ModuleNotFoundError: No module named 'distributed'
# - Redis connection failed
```

#### **🐛 kubectl delete -f . falla**
```bash
# Error: Object 'Kind' is missing in 'docker-compose.yml'
# Problema: kubectl intenta leer docker-compose.yml como YAML de K8s

# Solución: Usar archivos específicos
kubectl delete -f redis-deployment.yaml
kubectl delete -f api-deployment.yaml  
kubectl delete -f worker-deployment.yaml

# O mover docker-compose.yml temporalmente
mv docker-compose.yml docker-compose.yml.bak
kubectl delete -f .
```

### **📈 Comparación: Docker Compose vs Kubernetes**

| Aspecto | Docker Compose | Kubernetes |
|---------|----------------|------------|
| **Auto-scaling** | ❌ Manual (`docker-compose scale`) | ✅ **Automático (HPA)** |
| **Métricas** | ❌ Externas (psutil) | ✅ **Integradas (Metrics Server)** |
| **Decisiones** | ❌ Humanas | ✅ **Automáticas basadas en carga** |
| **Tolerancia fallos** | ❌ Manual restart | ✅ **Auto-restart de pods** |
| **Producción** | ❌ Solo desarrollo | ✅ **Listo para producción** |
| **Learning curve** | ✅ Fácil | ⚠️ **Más complejo pero poderoso** |

### **🎓 Valor Educativo**

Este proyecto demuestra la **evolución completa** de un sistema:

1. **Threading/Multiprocessing** → Conceptos de concurrencia
2. **Docker Compose** → Orchestración básica  
3. **Redis + Workers** → Arquitectura distribuida
4. **Monitoring** → Observabilidad en producción
5. **Kubernetes** → **Auto-scaling real y métricas**

**¿El resultado?** Un sistema que:
- ✅ **Se escala automáticamente** bajo carga
- ✅ **Optimiza recursos** cuando no hay trabajo
- ✅ **Funciona en cualquier plataforma** (Windows, Mac, Linux)
- ✅ **Está listo para producción** con modificaciones mínimas

---

**🎯 ¡Felicidades! Has construido un sistema distribuido con auto-scaling real funcionando en Kubernetes!** 🚀

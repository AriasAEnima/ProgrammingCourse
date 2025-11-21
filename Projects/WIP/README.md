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
**Estado:** ✅ Completada y probada  
**Carpeta:** `session3_workers/`

**Temas:**
- Patrón Worker (BaseWorker → SimpleWorker)
- TaskQueue: Cola de tareas en memoria
- Logging estructurado
- Health checks y estadísticas

### 🔜 Sesión 4: Redis y Colas de Tareas
**Temas a cubrir:**
- Redis como cola
- Serialización de tareas
- Estados de tareas

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


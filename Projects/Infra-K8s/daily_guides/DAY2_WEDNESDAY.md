# 🔥 DÍA 2 - MIÉRCOLES: "Multiprocessing + Heavy Processing"

**Duración**: 45min seguimiento + 1h autónoma | **Objetivo**: Threading → Multiprocessing para CPU-intensivos

---

## 🎯 **OBJETIVOS DEL DÍA**

### **🧠 CONCEPTUAL:**
- Entender diferencia entre **I/O bound** vs **CPU bound**
- Aplicar **multiprocessing** para tareas computacionalmente intensivas
- Implementar **Process Pool** escalable
- Usar **IPC Queues** para comunicación entre procesos

### **🛠️ TÉCNICO:**
- Migrar filtros pesados a **ProcessPoolExecutor**
- Implementar **workers dedicados** por tipo de filtro
- **Resource monitoring** en tiempo real
- **Benchmark** threading vs multiprocessing

### **📊 MÉTRICAS DE ÉXITO:**
- **Speedup >3x** en filtros CPU-intensivos vs threading
- **10+ imágenes 4K** procesadas simultáneamente
- **CPU utilization >80%** durante procesamiento
- **Zero crashes** durante stress testing

---

## ⏰ **AGENDA - 45 MINUTOS SEGUIMIENTO**

### **🔥 WARM-UP (5 min)**
```bash
# Verificar estado actual
cd Chapter-Threads/Projects
python manage.py runserver 8000 &

# Test threading actual
curl -X POST http://localhost:8000/api/process-batch/compare/ \
     -d '{"count": 3, "filters": ["resize", "blur", "brightness"]}'
```

### **⚡ IMPLEMENTACIÓN CORE (25 min)**

#### **1. Filtros Pesados Reales (8 min)**
- Implementar `heavy_sharpen_filter` con OpenCV
- Implementar `edge_detection_filter` con procesamiento real
- Test individual de filtros pesados

#### **2. Process Pool (10 min)**  
- Crear `ProcessPoolExecutor` en `processors.py`
- Migrar filtros CPU-intensivos a workers separados
- Test básico de multiprocessing

#### **3. Benchmark Setup (7 min)**
- Crear script de comparación `threading_vs_mp.py`
- Métricas: tiempo, CPU usage, memory usage
- Demo en vivo del speedup

### **🧪 DEMO FINAL (10 min)**
```bash
# Comparación directa - esperamos >3x speedup
python benchmarks/threading_vs_mp.py

# Stress test - 10 imágenes simultáneamente  
curl -X POST http://localhost:8000/api/process-batch/multiprocessing/ \
     -d '{"count": 10, "filters": ["sharpen", "edges"]}'
```

### **📝 WRAP-UP (5 min)**
- Review de métricas alcanzadas
- Troubleshooting común
- Plan para 1h autónoma

---

## 🚀 **TRABAJO AUTÓNOMO - 1 HORA**

### **🎯 OBJETIVOS AUTÓNOMOS:**
1. **Workers especializados** por tipo de operación
2. **Queue-based IPC** para comunicación robusta  
3. **Resource monitoring** con alertas
4. **Error handling** y recovery

### **📋 CHECKLIST AUTÓNOMO:**

#### **🔧 WORKERS AVANZADOS (25 min)**
- [ ] `FilterWorker` class con especialización por filtro
- [ ] Worker pools dedicados (`io_pool`, `cpu_pool`) 
- [ ] Worker lifecycle management (start/stop/restart)
- [ ] Load balancing entre workers disponibles

#### **🔗 IPC COMMUNICATION (20 min)**
- [ ] `QueueManager` con multiprocessing.Queue
- [ ] Message passing entre API y workers
- [ ] Request/response correlation
- [ ] Queue monitoring y stats

#### **📊 MONITORING (10 min)**
- [ ] Real-time CPU/memory tracking con `psutil`
- [ ] Worker health checks
- [ ] Performance alerts (>90% CPU)
- [ ] Metrics dashboard simple

#### **🛡️ ERROR HANDLING (5 min)**
- [ ] Worker crash detection y restart
- [ ] Timeout handling para filtros pesados
- [ ] Graceful degradation (fallback a threading)

---

## 📂 **ARCHIVOS A CREAR HOY**

### **🆕 NUEVOS ARCHIVOS:**
```
Projects/
├── workers/
│   ├── __init__.py
│   ├── filter_worker.py     # ← ProcessPoolExecutor workers
│   ├── queue_manager.py     # ← IPC con multiprocessing.Queue  
│   └── monitor.py           # ← psutil monitoring
├── benchmarks/
│   ├── __init__.py
│   └── threading_vs_mp.py   # ← Performance comparison
└── tests/
    └── test_multiprocessing.py # ← Unit tests MP
```

### **📝 ARCHIVOS A ACTUALIZAR:**
- `image_api/filters.py` → Implementar filtros pesados reales
- `image_api/processors.py` → Agregar multiprocessing support
- `image_api/views.py` → Endpoints multiprocessing
- `requirements_extended.txt` → Agregar OpenCV, psutil

---

## 🎨 **FILTROS DEL DÍA**

### **🧵 THREADING (Día 1):**
- `resize` → 0.2s (I/O + resize simple)
- `blur` → 0.3s (I/O + blur ligero)  
- `brightness` → 0.1s (I/O + ajuste simple)

### **🔄 MULTIPROCESSING (Día 2):**
- `heavy_sharpen` → 2.0s (CPU intensivo)
- `edge_detection` → 1.5s (CPU + algoritmos complejos)

### **📊 PERFORMANCE ESPERADO:**
```
THREADING (3 filtros ligeros):
├── Sequential: ~0.6s × 3 imágenes = 1.8s
└── Parallel: ~0.6s (speedup 3x)

MULTIPROCESSING (2 filtros pesados):  
├── Sequential: ~3.5s × 3 imágenes = 10.5s
├── Threading: ~3.5s (GIL limitation)
└── Multiprocessing: ~3.5s / cores (speedup 4x+ en quad-core)
```

---

## 🧪 **COMANDOS DE TESTING**

### **⚡ QUICK TESTS:**
```bash
# 1. Test filtros pesados individuales
curl -X POST http://localhost:8000/api/filters/sharpen/ \
     -F "image=@static/images/sample_4k.jpg"

# 2. Benchmark automático
python benchmarks/threading_vs_mp.py --images=5 --verbose

# 3. Resource monitoring
python workers/monitor.py --duration=30
```

### **🔥 STRESS TESTS:**
```bash
# Procesar 10 imágenes 4K simultáneamente
curl -X POST http://localhost:8000/api/process-batch/stress/ \
     -d '{"count": 10, "filters": ["sharpen", "edges", "resize"]}'

# Monitor durante stress test
python workers/monitor.py --stress-mode
```

---

## 🎓 **CONCEPTOS CLAVE PARA ESTUDIANTES**

### **🧠 I/O BOUND vs CPU BOUND:**
```python
# I/O BOUND (threading wins)
def resize_filter(image):
    image_data = open(file).read()  # ← Disk I/O
    return simple_resize(image_data)

# CPU BOUND (multiprocessing wins)  
def edge_detection(image):
    for pixel in millions_of_pixels:    # ← Pure computation
        complex_algorithm(pixel)
```

### **⚡ GIL IMPACT:**
- **Threading**: Perfect para I/O, limitado por GIL en CPU
- **Multiprocessing**: Bypass GIL, cada proceso = core dedicado

### **🔗 IPC PATTERNS:**
- **Queues**: Para task distribution
- **Pipes**: Para worker communication  
- **Shared Memory**: Para data sharing

---

## 🚨 **TROUBLESHOOTING COMÚN**

### **❌ PROBLEMA**: "ProcessPoolExecutor hangs"
**✅ SOLUCIÓN**: 
```python
# Timeout para evitar hangs
with ProcessPoolExecutor() as executor:
    future = executor.submit(heavy_filter, image)
    result = future.result(timeout=30)
```

### **❌ PROBLEMA**: "Queue memory overflow"
**✅ SOLUCIÓN**:
```python
# Limitar queue size
queue = multiprocessing.Queue(maxsize=100)
```

### **❌ PROBLEMA**: "Workers not releasing memory"
**✅ SOLUCIÓN**: Restart workers periodically

---

## 📊 **CRITERIOS DE EVALUACIÓN**

### **🟢 BÁSICO (todos deben lograr):**
- [ ] 2+ filtros pesados funcionando
- [ ] ProcessPoolExecutor con speedup >2x
- [ ] Benchmark script ejecutable

### **🟡 INTERMEDIO (mayoría debería lograr):**
- [ ] Workers especializados por filtro
- [ ] Queue-based communication
- [ ] Resource monitoring básico
- [ ] Error handling robusto

### **🔴 AVANZADO (algunos lograrán):**
- [ ] Auto-scaling de worker pools
- [ ] Real-time metrics dashboard  
- [ ] Intelligent load balancing
- [ ] Graceful degradation

---

## 🎯 **PREPARACIÓN PARA MAÑANA (DÍA 3)**

**Objetivo Día 3**: Workers locales → **Workers distribuidos** en Docker containers

**Setup requerido**:
- Redis server para distributed queues
- Docker containers preparados
- Load balancer básico

¡**Hoy construimos la fundación multiprocessing** para mañana escalar distribuidamente! 🚀 
# 🔥 **GUÍA INSTRUCTOR - DÍA 2 - MULTIPROCESSING + CPU-BOUND**

**Fecha**: Martes - Día 2 del Proyecto  
**Objetivo**: Threading vs Multiprocessing - ¿Cuándo usar cada uno?  
**Material**: Servidor Django + Filtros **THREADING YA FUNCIONANDO** (ayer)

---

## 🎯 **CONTEXTO: DÍA 2 DE 4**

### **✅ AYER (Día 1) vieron:**
- Threading con ThreadPoolExecutor
- Filtros I/O-bound (resize, blur, brightness)
- Threading funcionó PERFECTO para leer archivos

### **🔥 HOY (Día 2) veremos:**
- Multiprocessing con ProcessPoolExecutor  
- Filtros CPU-bound (sharpen, edge detection)
- ¿Cuándo Threading NO es suficiente?

---

## ⏰ **CRONOGRAMA (45 MIN)**

### **📚 MINUTOS 0-10: REVIEW + SETUP**

#### **Minuto 0-3: Review día anterior**
```
"¡Buenos días! Ayer implementamos Threading para filtros I/O-bound.
¿Recuerdan por qué Threading funcionó bien para resize, blur, brightness?

RESPUESTA: Porque leer archivos del disco es I/O-bound.
El GIL se libera durante I/O, permitiendo concurrencia real."
```

#### **Minuto 3-7: Plantear problema de hoy**
```
"PREGUNTA: ¿Qué pasa si tenemos filtros que saturan la CPU?
Ejemplo: Edge detection, sharpen, complex mathematical operations.

¿Threading seguirá siendo efectivo?
¡Vamos a descubrirlo!"
```

#### **Minuto 7-10: Verificar estado actual**
```bash
# Verificar servidor funcionando
curl http://localhost:8000/api/health/

# Test threading como baseline (lo que ya saben)
curl -X POST http://localhost:8000/api/process-batch/threading/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["resize", "blur"], "filter_params": {"resize": {"width": 800, "height": 600}, "blur": {"radius": 3.0}}}'
```

---

### **🔧 MINUTOS 10-25: DEMOS CPU-BOUND**

#### **Minuto 10-13: Demo filtro CPU-intensivo con Threading**
```bash
# DEMO 1: Threading con filtro pesado (sharpen)
curl -X POST http://localhost:8000/api/process-batch/threading/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["sharpen"], "filter_params": {"sharpen": {"intensity": 3}}}'
```

**Explicar mientras corre:**
```
"El filtro 'sharpen' usa OpenCV y NumPy para operaciones matriciales.
Es CPU-intensivo: muchas multiplicaciones y convoluciones.
¿Notaron que tarda más? ¿Threading ayuda tanto como ayer?"
```

#### **Minuto 13-18: Demo Multiprocessing con mismo filtro**
```bash
# DEMO 2: Multiprocessing con filtro pesado 
curl -X POST http://localhost:8000/api/process-batch/multiprocessing/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["sharpen"], "filter_params": {"sharpen": {"intensity": 3}}}'
```

**Explicar:**
```
"Multiprocessing = procesos separados, no threads.
Cada proceso tiene su propia memoria, su propio GIL.
Para CPU-bound tasks, esto permite VERDADERO paralelismo."
```

#### **Minuto 18-22: Comparación directa TODOS los métodos**
```bash
# DEMO 3: Comparación completa (¡EL MOMENTO CLAVE!)
curl -X POST http://localhost:8000/api/process-batch/compare-all/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["resize", "sharpen"], "filter_params": {"resize": {"width": 800, "height": 600}, "sharpen": {"intensity": 2}}}'
```

**Analizar resultados:**
```
"¡Miremos los resultados!
- Sequential: X.X segundos
- Threading: Y.Y segundos  
- Multiprocessing: Z.Z segundos

¿Qué observan? Para resize (I/O), ¿quién gana?
Para sharpen (CPU), ¿quién gana?"
```

#### **Minuto 22-25: Demo extremo - Edge Detection**
```bash
# DEMO 4: Filtro MUY CPU-intensivo
curl -X POST http://localhost:8000/api/process-batch/multiprocessing/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["edges"], "filter_params": {"edges": {"threshold1": 50, "threshold2": 150}}}'
```

**Explicar:**
```
"Edge detection usa algoritmos de Canny en OpenCV.
Es EXTREMADAMENTE CPU-intensivo.
Aquí Multiprocessing debería brillar."
```

---

### **🎯 MINUTOS 25-40: CONCEPTOS PROFUNDOS**

#### **Minuto 25-30: Threading vs Multiprocessing - ¿Cuándo usar qué?**
```
"REGLA DE ORO:

Threading = I/O-bound
- Leer archivos, bases de datos, APIs
- Network requests, disk operations
- GIL se libera durante I/O

Multiprocessing = CPU-bound  
- Cálculos matemáticos pesados
- Image processing algorithms
- Machine learning, data science
- Cada proceso = GIL independiente"
```

#### **Minuto 30-35: Hands-on experimentos**
```bash
# Experimento 1: Threading vs MP con mix de filtros
curl -X POST http://localhost:8000/api/process-batch/compare-all/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["resize", "blur", "sharpen"], "filter_params": {"resize": {"width": 800, "height": 600}, "blur": {"radius": 2.0}, "sharpen": {"intensity": 3}}}'

# Experimento 2: Stress test con multiprocessing
curl -X POST http://localhost:8000/api/process-batch/stress/ \
  -H "Content-Type: application/json" \
  -d '{"filters": ["sharpen", "edges"], "filter_params": {"sharpen": {"intensity": 3}, "edges": {"threshold1": 50, "threshold2": 150}}}'
```

**Que experimenten:**
```
"Cambien la intensidad del sharpen: 1, 2, 3, 4, 5
¿Cómo cambian los tiempos?
¿En qué punto Multiprocessing DOMINA sobre Threading?"
```

#### **Minuto 35-40: Ver y analizar resultados**
```bash
# Ver todas las imágenes procesadas
ls -la static/processed/

# Mostrar diferencias visuales
# sharpen vs edge detection vs resize
```

**Explicar costos:**
```
"Multiprocessing NO es gratis:
- Overhead de crear procesos
- Comunicación entre procesos más lenta  
- Mayor uso de memoria

¿Vale la pena? Depende de si la tarea es CPU-bound."
```

---

### **🚀 MINUTOS 40-45: WRAP-UP**

#### **Minuto 40-43: Síntesis y preguntas**
```
"SÍNTESIS DEL DÍA:

Threading = GIL compartido, perfecto para I/O
Multiprocessing = GIL independiente, perfecto para CPU

¿Preguntas?
- ¿Cuándo elegir uno u otro?
- ¿Cómo saber si mi tarea es I/O-bound o CPU-bound?
- ¿Se pueden combinar ambos enfoques?"
```

#### **Minuto 43-45: Preview mañana**
```
"MAÑANA - Día 3: ASYNC + DISTRIBUTED

Pregunta: ¿Y si necesitamos manejar 1000 requests simultáneos?
Threading tiene límites, Multiprocessing consume mucha memoria.

Solución: Async programming + Distributed workers
- async/await para concurrencia masiva
- Message queues para distribución
- Redis/Celery para trabajos en background"
```

---

## 🎯 **CURLS PARA DEMOS**

### **1. Comparación Threading vs Multiprocessing:**
```bash
curl -X POST http://localhost:8000/api/process-batch/compare-all/ -H "Content-Type: application/json" -d '{"filters": ["resize", "sharpen"], "filter_params": {"resize": {"width": 800, "height": 600}, "sharpen": {"intensity": 2}}}'
```

### **2. Solo Multiprocessing CPU-intensivo:**
```bash
curl -X POST http://localhost:8000/api/process-batch/multiprocessing/ -H "Content-Type: application/json" -d '{"filters": ["sharpen", "edges"], "filter_params": {"sharpen": {"intensity": 3}, "edges": {"threshold1": 50, "threshold2": 150}}}'
```

### **3. Stress test multiprocessing:**
```bash
curl -X POST http://localhost:8000/api/process-batch/stress/ -H "Content-Type: application/json" -d '{"filters": ["sharpen"], "filter_params": {"sharpen": {"intensity": 4}}}'
```

---

## 📊 **MÉTRICAS ESPERADAS HOY**

| Filtro | Threading | Multiprocessing | Ganador |
|--------|-----------|-----------------|---------|
| resize (I/O) | 1.2s | 1.8s | **Threading** |
| blur (I/O) | 1.0s | 1.5s | **Threading** |  
| sharpen (CPU) | 3.5s | 2.1s | **Multiprocessing** |
| edges (CPU) | 5.2s | 2.8s | **Multiprocessing** |

---

## 🎓 **TAKEAWAYS CLAVE**

1. **Threading ≠ Multiprocessing** - Casos de uso diferentes
2. **I/O-bound = Threading** (GIL se libera)
3. **CPU-bound = Multiprocessing** (GIL independiente)
4. **Overhead matters** - Multiprocessing no es gratis
5. **Real world**: Combinar ambos enfoques según necesidad

**¡Hoy dominamos cuándo usar cada herramienta de concurrencia!** 🚀 
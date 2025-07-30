# 🔥 **GUÍA INSTRUCTOR - 45 MINUTOS - THREADING + IMAGE PROCESSING**

**Fecha**: Martes - Día 1 del Proyecto  
**Objetivo**: Demostrar ventajas de Threading vs Sequential en procesamiento de imágenes  
**Material**: Servidor Django + Filtros PIL/OpenCV **YA FUNCIONANDO**

---

## ⏰ **CRONOGRAMA DETALLADO (45 MIN)**

### **📚 MINUTOS 0-10: SETUP + CONTEXTO**

#### **Minuto 0-3: Bienvenida y revisión**
```
"¡Buenos días! Ayer vimos sistemas distribuidos.
Hoy empezamos un proyecto de 4 días: procesar imágenes con concurrencia.

El objetivo: ¿Cuándo usar Threading vs Multiprocessing?
Respuesta corta: Threading = I/O, Multiprocessing = CPU"
```

#### **Minuto 3-7: Verificar setup**
```bash
# Verificar que todos tengan el servidor funcionando
curl http://localhost:8000/api/health/

# Verificar imágenes disponibles
ls static/images/

# Mostrar que static/processed/ está vacío (o casi)
ls static/processed/
```

#### **Minuto 7-10: Explicar problema**
```
"Tenemos un servidor que sirve imágenes estáticas.
Queremos aplicar filtros: resize, blur, brightness, sharpen, edge detection.

PREGUNTA: ¿Qué es más lento: leer un archivo o procesarlo?
RESPUESTA: Depende del filtro.

Hoy: filtros I/O-bound (resize, blur, brightness)
Mañana: filtros CPU-bound (sharpen, edge detection)"
```

---

### **🔧 MINUTOS 10-25: DEMO PRÁCTICA**

#### **Minuto 10-13: Procesamiento SECUENCIAL**
```bash
# DEMO 1: Secuencial (baseline)
curl -X POST http://localhost:8000/api/process-batch/sequential/ \
  -H "Content-Type: application/json" \
  -d '{
    "filters": ["resize", "blur"], 
    "filter_params": {
      "resize": {"width": 800, "height": 600},
      "blur": {"radius": 3.0}
    }
  }'
```

**Explicar mientras corre:**
```
"Sequential significa: procesar imagen 1, luego imagen 2, luego imagen 3.
Si cada imagen toma 1 segundo, 3 imágenes = 3 segundos total.
¿Podemos mejorar esto?"
```

**Ver resultado:**
```bash
ls static/processed/
```

#### **Minuto 13-18: Procesamiento con THREADING**
```bash
# DEMO 2: Threading
curl -X POST http://localhost:8000/api/process-batch/threading/ \
  -H "Content-Type: application/json" \
  -d '{
    "filters": ["resize", "blur", "brightness"], 
    "filter_params": {
      "resize": {"width": 800, "height": 600},
      "blur": {"radius": 2.0},
      "brightness": {"factor": 1.2}
    }
  }'
```

**Explicar mientras corre:**
```
"Threading significa: procesar 3 imágenes EN PARALELO.
¿Por qué funciona? Porque el filtro 'resize' lee del disco (I/O-bound).
Mientras Thread 1 lee, Thread 2 puede ejecutar, Thread 3 también."
```

#### **Minuto 18-22: COMPARACIÓN DIRECTA**
```bash
# DEMO 3: Comparación directa
curl -X POST http://localhost:8000/api/process-batch/compare/ \
  -H "Content-Type: application/json" \
  -d '{
    "filters": ["resize", "blur"], 
    "filter_params": {
      "resize": {"width": 800, "height": 600},
      "blur": {"radius": 3.0}
    }
  }'
```

**Analizar resultados juntos:**
```
"Miremos los resultados:
- Sequential time: X.X segundos
- Threading time: Y.Y segundos  
- Speedup: Z.Zx

¿Por qué Threading es más rápido?
¿Cuándo Threading NO sería más rápido?"
```

#### **Minuto 22-25: Mostrar filtros pesados**
```bash
# DEMO 4: CPU-bound (preparando para mañana)
curl -X POST http://localhost:8000/api/process-batch/multiprocessing/ \
  -H "Content-Type: application/json" \
  -d '{
    "filters": ["sharpen"], 
    "filter_params": {
      "sharpen": {"intensity": 3}
    }
  }'
```

**Explicar:**
```
"Este filtro 'sharpen' es CPU-intensivo. Usa OpenCV y NumPy.
¿Notaron que tardó más? Mañana veremos por qué Multiprocessing 
es mejor para estos casos."
```

---

### **🎯 MINUTOS 25-40: CONCEPTOS CLAVE**

#### **Minuto 25-30: Explicar Threading vs GIL**
```
"PREGUNTA CLAVE: ¿Por qué Threading funciona en Python si existe el GIL?

RESPUESTA: El GIL se LIBERA durante operaciones I/O.

Cuando el hilo lee un archivo del disco:
1. Python libera el GIL
2. Otro hilo puede ejecutar
3. El sistema operativo maneja la concurrencia

Por eso Threading es PERFECTO para:
- Leer archivos
- Hacer requests HTTP  
- Conectar a bases de datos
- Operaciones de red"
```

#### **Minuto 30-35: Hands-on - Modificar parámetros**
```bash
# Experimento 1: Más filtros
curl -X POST http://localhost:8000/api/process-batch/threading/ \
  -H "Content-Type: application/json" \
  -d '{
    "filters": ["resize", "blur", "brightness"], 
    "filter_params": {
      "resize": {"width": 1200, "height": 900},
      "blur": {"radius": 5.0},
      "brightness": {"factor": 1.5}
    }
  }'

# Experimento 2: Stress test
curl -X POST http://localhost:8000/api/process-batch/stress/ \
  -H "Content-Type: application/json" \
  -d '{
    "filters": ["resize", "blur", "brightness"], 
    "filter_params": {
      "resize": {"width": 800, "height": 600},
      "blur": {"radius": 3.0},
      "brightness": {"factor": 1.3}
    }
  }'
```

**Que experimenten:**
```
"Cambien los parámetros: width, height, radius, factor.
¿Qué pasa si usan imágenes más grandes?
¿Y si aumentan el radio del blur?"
```

#### **Minuto 35-40: Ver resultados físicos**
```bash
# Ver todas las imágenes generadas
ls -la static/processed/

# Si tienen Windows Explorer / Finder, abrir la carpeta
# Mostrar las diferencias visuales entre filtros
```

**Explicar:**
```
"Estos son archivos REALES procesados.
Noten los nombres: incluyen timestamp y parámetros.
¿Ven la diferencia entre resize_800x600 y blur_r3.0?"
```

---

### **🚀 MINUTOS 40-45: WRAP-UP Y SIGUIENTE SESIÓN**

#### **Minuto 40-43: Preguntas y respuestas**
```
"¿Preguntas sobre Threading?
¿Quedó claro cuándo usar Threading vs cuándo NO?
¿Entendieron por qué funciona a pesar del GIL?"

Respuestas típicas:
- Threading = I/O-bound (leer archivos, red, DB)
- GIL se libera durante I/O
- ThreadPoolExecutor maneja los hilos automáticamente
```

#### **Minuto 43-45: Preview mañana**
```
"MAÑANA - Día 2: MULTIPROCESSING

¿Cuándo Threading NO es suficiente?
- Filtros que saturan CPU (edge detection, sharpen)
- Algoritmos matemáticos pesados
- Cuando necesitas VERDADERO paralelismo

Compararemos:
curl .../compare-all/
- Sequential 
- Threading
- Multiprocessing

¡Veremos cuándo Multiprocessing DOMINA sobre Threading!"
```

---

## 🎯 **CURLS LISTOS PARA COPIAR/PEGAR**

### **Demo básica:**
```bash
curl -X POST http://localhost:8000/api/process-batch/compare/ -H "Content-Type: application/json" -d '{"filters": ["resize", "blur"], "filter_params": {"resize": {"width": 800, "height": 600}, "blur": {"radius": 3.0}}}'
```

### **Threading con 3 filtros:**
```bash
curl -X POST http://localhost:8000/api/process-batch/threading/ -H "Content-Type: application/json" -d '{"filters": ["resize", "blur", "brightness"], "filter_params": {"resize": {"width": 800, "height": 600}, "blur": {"radius": 2.0}, "brightness": {"factor": 1.2}}}'
```

### **Preview multiprocessing:**
```bash
curl -X POST http://localhost:8000/api/process-batch/multiprocessing/ -H "Content-Type: application/json" -d '{"filters": ["sharpen"], "filter_params": {"sharpen": {"intensity": 3}}}'
```

---

## 📊 **MÉTRICAS ESPERADAS**

| Método | Tiempo típico | Speedup |
|--------|---------------|---------|
| Sequential | 2-4 segundos | 1.0x (baseline) |
| Threading | 0.8-1.5 segundos | 2-3x |
| Multiprocessing | 1-2 segundos | 2x (mañana) |

---

## 🎓 **PUNTOS CLAVE A ENFATIZAR**

1. **Threading FUNCIONA en Python** para I/O-bound tasks
2. **GIL no es problema** cuando el hilo está esperando I/O
3. **ThreadPoolExecutor** es la herramienta correcta
4. **I/O-bound vs CPU-bound** determina la estrategia
5. **Filtros reales**: resize, blur, brightness son I/O-bound

**¡Listo para una clase exitosa!** 🚀 
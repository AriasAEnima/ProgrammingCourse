# ⚡ Guía Rápida - Sesión 2

## 🎯 Lo que Aprenderás Hoy (45 min)

1. **FilterPipeline**: Cadena de filtros
2. **FilterFactory**: Crear filtros dinámicamente  
3. **BatchProcessor**: Procesar múltiples imágenes

---

## 🚀 Setup Rápido

```bash
cd session2_pipelines
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📝 Código Esencial

### 1. Pipeline Básico (5 min)

```python
from PIL import Image
from core import FilterPipeline
from filters import BlurFilter, BrightnessFilter, EdgesFilter

# Crear pipeline
pipeline = FilterPipeline([
    BlurFilter(radius=3),
    BrightnessFilter(factor=1.3),
    EdgesFilter()
])

# Aplicar
image = Image.open('images/sample.jpg')
result, stats = pipeline.apply(image)

# Ver estadísticas
print(f"Tiempo total: {stats['total_time']:.3f}s")
for f in stats['filters']:
    print(f"{f['name']}: {f['time']:.3f}s")

# Guardar
result.save('output/result.jpg')
```

**Resultado:**
- ✅ Filtros aplicados en secuencia
- ✅ Estadísticas de performance
- ✅ Código limpio y expresivo

---

### 2. Factory Pattern (10 min)

```python
from core import FilterFactory

factory = FilterFactory()

# Crear filtros desde strings
blur = factory.create('blur', radius=5)
bright = factory.create('brightness', factor=1.5)

# Desde configuración JSON
config = [
    {'type': 'blur', 'radius': 3},
    {'type': 'brightness', 'factor': 1.2},
    {'type': 'edges'}
]

pipeline = factory.create_pipeline(config)
result, stats = pipeline.apply(image)
```

**¿Por qué es útil?**
- ✅ APIs que reciben JSON
- ✅ CLIs dinámicas
- ✅ Configuración externa
- ✅ Testing automático

---

### 3. Batch Processing (10 min)

```python
from core import BatchProcessor, FilterPipeline
from filters import GrayscaleFilter, BlurFilter

# Crear pipeline
pipeline = FilterPipeline([
    GrayscaleFilter(),
    BlurFilter(radius=2)
])

# Procesar carpeta completa
processor = BatchProcessor(
    input_dir='images/',
    output_dir='output/batch/',
    pipeline=pipeline
)

results = processor.process_all()

print(f"Procesadas: {results['successful']}/{results['total']}")
print(f"Tiempo: {results['total_time']:.2f}s")
```

**Características:**
- ✅ Procesa carpetas completas
- ✅ Muestra progreso
- ✅ Maneja errores
- ✅ Reporte detallado

---

## 🎨 Ejercicios Prácticos (20 min)

### Ejercicio 1: Preset "Vintage" (Fácil)
Crea un pipeline que simule foto antigua:
```python
vintage_pipeline = FilterPipeline([
    BrightnessFilter(factor=0.9),  # Más oscura
    # Añade más filtros aquí
])
```

### Ejercicio 2: Factory desde Config (Medio)
Lee configuración desde un archivo y crea pipeline:
```python
import json

with open('config.json') as f:
    config = json.load(f)

pipeline = factory.create_pipeline(config)
```

### Ejercicio 3: Batch con Subdirectorios (Avanzado)
Procesa carpetas recursivamente preservando estructura.

---

## 📊 Comparación de Performance

**Imagen 2000x1334 px:**

| Método | Tiempo | Ventaja |
|--------|--------|---------|
| Manual (3 filtros) | 0.142s | - |
| Pipeline (3 filtros) | 0.133s | 6% más rápido ✅ |
| Batch (10 imágenes) | 1.42s | ~0.14s por imagen |

**¿Por qué el pipeline es más rápido?**
- Imagen en memoria (no I/O)
- Menos overhead
- Optimización del flujo

---

## 🔗 Conexión con Sistema Distribuido

Lo que vimos hoy se convertirá en:

| Hoy (Sesión 2) | Futuro (Sesión 5+) |
|----------------|-------------------|
| FilterPipeline | Tarea distribuida |
| FilterFactory | Worker dinámico |
| BatchProcessor | Cola de Redis |
| Stats | Métricas de K8s |

---

## ✅ Checklist de Aprendizaje

Al final de esta sesión deberías poder:

- [ ] Crear un pipeline con 3+ filtros
- [ ] Usar FilterFactory para crear filtros desde strings
- [ ] Procesar múltiples imágenes con BatchProcessor
- [ ] Interpretar estadísticas de performance
- [ ] Modificar pipelines dinámicamente

---

## 📚 Para Profundizar

- **Design Patterns**: Factory, Pipeline, Strategy
- **Performance**: Profiling, optimización
- **Testing**: Unit tests para filtros
- **Async**: ¿Cómo hacer esto asíncrono?

---

## 🎯 Próxima Sesión: Workers

En la Sesión 3 veremos:
- Patrón Worker para procesamiento
- Procesamiento asíncrono
- Logging estructurado
- Health checks y monitoreo

---

**¡Buen trabajo! 🚀**


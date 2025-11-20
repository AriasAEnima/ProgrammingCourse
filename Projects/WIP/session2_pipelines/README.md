# 🔗 Sesión 2: Pipelines y Composición de Filtros

## 🎯 Objetivos de la Sesión (45 min)

1. **Componer filtros** en cadenas (pipelines)
2. **Factory Pattern** para crear filtros dinámicamente
3. **Procesar múltiples imágenes** en batch
4. **Medir performance** y optimizar

---

## 🔄 De Filtros Individuales a Pipelines

### Sesión 1 (Repaso):
```python
# Aplicar UN filtro a la vez
image = Image.open('photo.jpg')
result = blur_filter.apply(image)
result.save('blurred.jpg')
```

### Sesión 2 (Nuevo):
```python
# Aplicar MÚLTIPLES filtros en secuencia
pipeline = FilterPipeline([
    BlurFilter(radius=2),
    BrightnessFilter(factor=1.5),
    EdgesFilter()
])

result = pipeline.apply(image)
```

**Ventajas:**
- ✅ Más expresivo y legible
- ✅ Reutilizable (guardar pipelines)
- ✅ Fácil de modificar
- ✅ Se puede medir performance

---

## 📂 Estructura del Proyecto

```
session2_pipelines/
├── README.md
├── requirements.txt
├── images/                    # Imágenes de prueba
│   └── sample.jpg
├── filters/                   # Filtros de la sesión 1
│   ├── __init__.py
│   ├── base_filter.py
│   ├── blur_filter.py
│   ├── brightness_filter.py
│   ├── edges_filter.py
│   └── grayscale_filter.py   # 🆕 Nuevo
│
├── core/                      # 🆕 Nuevo módulo
│   ├── __init__.py
│   ├── filter_pipeline.py    # Pipeline de filtros
│   ├── filter_factory.py     # Factory para crear filtros
│   └── batch_processor.py    # Procesamiento en lote
│
├── demos/
│   ├── demo_pipeline.py      # Demo de pipelines
│   ├── demo_factory.py       # Demo de factory
│   └── demo_batch.py         # Demo de procesamiento batch
│
└── output/                    # Resultados
```

---

## 🔧 Conceptos Clave

### 1. Filter Pipeline (Cadena de Filtros)

**Problema:**
```python
# Código repetitivo y difícil de mantener
image = Image.open('photo.jpg')
temp1 = blur_filter.apply(image)
temp2 = brightness_filter.apply(temp1)
temp3 = edges_filter.apply(temp2)
result = temp3
```

**Solución:**
```python
# Pipeline elegante
pipeline = FilterPipeline([
    BlurFilter(radius=2),
    BrightnessFilter(factor=1.5),
    EdgesFilter()
])

result = pipeline.apply(image)
```

**Características:**
- Aplica filtros en orden
- Mide tiempo de cada filtro
- Maneja errores gracefully
- Puede guardar imágenes intermedias

---

### 2. Filter Factory (Patrón Factory)

**Problema:**
```python
# Crear filtros manualmente es verboso
if filter_name == 'blur':
    filter = BlurFilter(radius=5)
elif filter_name == 'brightness':
    filter = BrightnessFilter(factor=1.5)
elif filter_name == 'edges':
    filter = EdgesFilter()
# ... más código repetitivo
```

**Solución:**
```python
# Factory crea filtros dinámicamente
factory = FilterFactory()
filter = factory.create('blur', radius=5)
```

**Ventajas:**
- ✅ Crear filtros desde configuración
- ✅ Crear filtros desde strings (API, CLI)
- ✅ Registro automático de filtros
- ✅ Validación de parámetros

---

### 3. Batch Processor (Procesamiento en Lote)

**Problema:**
```python
# Procesar múltiples imágenes es tedioso
for filename in os.listdir('images/'):
    image = Image.open(f'images/{filename}')
    result = filter.apply(image)
    result.save(f'output/{filename}')
```

**Solución:**
```python
# Batch processor maneja todo
processor = BatchProcessor(
    input_dir='images/',
    output_dir='output/',
    pipeline=my_pipeline
)

results = processor.process_all()
print(f"Procesadas: {results['successful']}/{results['total']}")
```

**Características:**
- Maneja múltiples formatos (JPG, PNG, JPEG)
- Muestra progreso
- Maneja errores (imágenes corruptas)
- Genera reporte detallado

---

## 🚀 Uso Rápido

### Instalar dependencias:
```bash
cd session2_pipelines
pip install -r requirements.txt
```

### 1. Demo de Pipeline:
```bash
python demos/demo_pipeline.py
```

Muestra cómo combinar filtros en secuencia.

### 2. Demo de Factory:
```bash
python demos/demo_factory.py
```

Muestra cómo crear filtros dinámicamente.

### 3. Demo de Batch:
```bash
python demos/demo_batch.py
```

Procesa múltiples imágenes con estadísticas.

---

## 📖 Ejemplos de Código

### Pipeline Básico:

```python
from core import FilterPipeline
from filters import BlurFilter, BrightnessFilter

# Crear pipeline
pipeline = FilterPipeline([
    BlurFilter(radius=3),
    BrightnessFilter(factor=1.3)
])

# Aplicar
result, stats = pipeline.apply(image)

# Ver estadísticas
print(f"Tiempo total: {stats['total_time']:.3f}s")
for filter_stat in stats['filters']:
    print(f"  {filter_stat['name']}: {filter_stat['time']:.3f}s")
```

### Factory Dinámico:

```python
from core import FilterFactory

factory = FilterFactory()

# Crear filtros desde strings
blur = factory.create('blur', radius=5)
bright = factory.create('brightness', factor=1.5)
edges = factory.create('edges')

# Crear pipeline desde configuración
config = [
    {'type': 'blur', 'radius': 3},
    {'type': 'brightness', 'factor': 1.2},
    {'type': 'edges'}
]

pipeline = factory.create_pipeline(config)
```

### Batch Processor:

```python
from core import BatchProcessor, FilterPipeline
from filters import BlurFilter, GrayscaleFilter

# Definir pipeline
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

# Resultados
print(f"✅ Exitosas: {results['successful']}")
print(f"❌ Fallidas: {results['failed']}")
print(f"⏱️  Tiempo total: {results['total_time']:.2f}s")
```

---

## 🎨 Ejercicios Prácticos

### Ejercicio 1: Pipeline Personalizado
Crea un pipeline que:
1. Convierta a escala de grises
2. Aumente el brillo un 20%
3. Aplique desenfoque suave

### Ejercicio 2: Preset de Filtros
Crea presets predefinidos:
- **"vintage"**: Oscurecer + Blur + Edges
- **"bright"**: Brightness alto
- **"sketch"**: Grayscale + Edges

### Ejercicio 3: Pipeline con Condiciones
Crea un pipeline que aplique filtros diferentes según el tamaño de la imagen.

---

## 📊 Performance

### Comparación de Tiempos:

**Imagen 4K (2000x1334 px):**
```
Individual:
  Blur:       0.062s
  Brightness: 0.022s
  Edges:      0.058s
  Total:      0.142s

Pipeline:
  Blur:       0.058s
  Brightness: 0.020s
  Edges:      0.055s
  Total:      0.133s ✅ (6% más rápido)
```

**¿Por qué el pipeline es más rápido?**
- ✅ Menos operaciones de I/O
- ✅ Imagen se mantiene en memoria
- ✅ No hay guardado/carga intermedia

---

## 🔍 Conceptos Avanzados

### 1. Immutability (Inmutabilidad)
Los filtros NO modifican la imagen original:
```python
original = Image.open('photo.jpg')
result = pipeline.apply(original)
# original sigue intacta ✅
```

### 2. Composition (Composición)
Pipelines pueden contener otros pipelines:
```python
base_pipeline = FilterPipeline([blur, brightness])
full_pipeline = FilterPipeline([base_pipeline, edges])
```

### 3. Lazy Evaluation (Evaluación Perezosa)
En futuras sesiones veremos cómo aplicar filtros solo cuando sea necesario.

---

## 🎓 Conexión con Sistema Distribuido

En las próximas sesiones, estos conceptos se convertirán en:

- **Pipeline** → Tarea distribuible
- **Factory** → Creación dinámica de workers
- **Batch** → Cola de tareas en Redis
- **Stats** → Métricas y monitoreo

---

## 📚 Próxima Sesión

**Sesión 3: Arquitectura de Workers**
- Patrón Worker
- Procesamiento asíncrono
- Logging estructurado
- Health checks

---

## 🤔 Preguntas Frecuentes

### ¿El pipeline es siempre más rápido?
No siempre. Depende del número de filtros y tamaño de imagen. Para 1-2 filtros la diferencia es mínima.

### ¿Puedo modificar el pipeline en runtime?
Sí, puedes añadir/quitar filtros:
```python
pipeline.add_filter(new_filter)
pipeline.remove_filter(0)
```

### ¿Cómo manejo errores en el pipeline?
El pipeline tiene opciones:
- `stop_on_error=True`: Detiene al primer error
- `stop_on_error=False`: Continúa con los demás filtros

---

## 📖 Referencias

- [Design Patterns: Factory](https://refactoring.guru/design-patterns/factory-method)
- [Pipeline Pattern](https://en.wikipedia.org/wiki/Pipeline_(software))
- [Pillow Performance Tips](https://pillow.readthedocs.io/en/stable/handbook/concepts.html)


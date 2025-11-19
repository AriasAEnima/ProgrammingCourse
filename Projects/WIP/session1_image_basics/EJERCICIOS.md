# 🎓 Ejercicios Prácticos - Sesión 1

## 📝 Instrucciones

Estos ejercicios te ayudarán a practicar lo aprendido en la sesión 1.
Intenta resolver cada ejercicio por tu cuenta antes de ver las soluciones.

---

## 🟢 Ejercicio 1: Filtro de Escala de Grises (Fácil)

**Objetivo:** Crear un filtro que convierta imágenes a escala de grises.

**Pasos:**
1. Crea un archivo `filters/grayscale_filter.py`
2. Define la clase `GrayscaleFilter` que herede de `BaseFilter`
3. Implementa el método `apply()` usando `image.convert('L')`

**Pista:**
```python
def apply(self, image):
    return image.convert('L')  # L = Luminance (grayscale)
```

**Prueba:**
```python
from filters.grayscale_filter import GrayscaleFilter

gray = GrayscaleFilter()
result = gray.apply(image)
```

---

## 🟡 Ejercicio 2: Filtro de Rotación (Medio)

**Objetivo:** Crear un filtro que rote imágenes en cualquier ángulo.

**Pasos:**
1. Crea un archivo `filters/rotate_filter.py`
2. Define la clase `RotateFilter` con un parámetro `angle`
3. Implementa el método `apply()` usando `image.rotate()`

**Características:**
- Debe aceptar ángulos de 0 a 360 grados
- Debe validar que el ángulo sea válido
- El ángulo por defecto debe ser 90 grados

**Ejemplo de uso:**
```python
# Rotar 90 grados
rotate_90 = RotateFilter(angle=90)
result = rotate_90.apply(image)

# Rotar 180 grados
rotate_180 = RotateFilter(angle=180)
result = rotate_180.apply(image)
```

---

## 🟡 Ejercicio 3: Filtro de Contraste (Medio)

**Objetivo:** Crear un filtro que ajuste el contraste de la imagen.

**Pasos:**
1. Crea un archivo `filters/contrast_filter.py`
2. Usa `ImageEnhance.Contrast` (similar a BrightnessFilter)
3. El factor debe estar entre 0.0 y 2.0
   - 0.0 = sin contraste (gris)
   - 1.0 = sin cambio
   - 2.0 = contraste máximo

**Pista:**
```python
from PIL import ImageEnhance

def apply(self, image):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(self.factor)
```

---

## 🔴 Ejercicio 4: Pipeline de Filtros (Difícil)

**Objetivo:** Crear un sistema para aplicar múltiples filtros en secuencia.

**Pasos:**
1. Crea un archivo `filter_pipeline.py`
2. Define una clase `FilterPipeline` que:
   - Acepte una lista de filtros en el constructor
   - Tenga un método `apply()` que aplique todos los filtros en orden
   - Mida el tiempo de cada filtro
   - Devuelva estadísticas de procesamiento

**Ejemplo de uso:**
```python
# Crear pipeline
pipeline = FilterPipeline([
    BlurFilter(radius=2),
    BrightnessFilter(factor=1.5),
    EdgesFilter()
])

# Aplicar todos los filtros
result, stats = pipeline.apply(image)

# Ver estadísticas
print(stats)
# {'total_time': 0.523, 'filters': [
#     {'filter': 'BlurFilter', 'time': 0.201},
#     {'filter': 'BrightnessFilter', 'time': 0.112},
#     {'filter': 'EdgesFilter', 'time': 0.210}
# ]}
```

**Bonus:**
- Añade manejo de errores (si un filtro falla, continuar con los demás)
- Permite guardar imágenes intermedias (después de cada filtro)

---

## 🔴 Ejercicio 5: Procesamiento por Lotes (Difícil)

**Objetivo:** Procesar múltiples imágenes con los mismos filtros.

**Pasos:**
1. Crea un archivo `batch_processor.py`
2. Define una clase `BatchProcessor` que:
   - Acepte una carpeta de imágenes
   - Aplique filtros a todas las imágenes
   - Guarde resultados en una carpeta de salida
   - Muestre progreso (imagen 1/10, 2/10, etc.)

**Características:**
- Debe soportar múltiples formatos (JPG, PNG, JPEG)
- Debe manejar errores (imágenes corruptas, permisos, etc.)
- Debe generar un reporte al final

**Ejemplo de uso:**
```python
processor = BatchProcessor(
    input_dir='images/',
    output_dir='output/batch/',
    filters=[BlurFilter(radius=3), BrightnessFilter(factor=1.2)]
)

results = processor.process_all()
print(f"Procesadas: {results['successful']}/{results['total']}")
```

---

## 🏆 Ejercicio Bonus: Sistema de Presets

**Objetivo:** Crear presets (combinaciones predefinidas) de filtros.

**Ejemplo:**
```python
# Preset "Vintage"
vintage = FilterPreset([
    BrightnessFilter(factor=0.9),
    ContrastFilter(factor=1.2),
    # Añadir efecto sepia si lo implementas
])

# Preset "Sketch"
sketch = FilterPreset([
    GrayscaleFilter(),
    EdgesFilter(),
    BrightnessFilter(factor=1.3)
])

# Aplicar preset
result = vintage.apply(image)
```

---

## ✅ Soluciones

Las soluciones a estos ejercicios estarán disponibles en `SOLUCIONES.md`.

**Recomendación:** Intenta resolver los ejercicios por tu cuenta primero.
El aprendizaje es más efectivo cuando intentas resolver problemas antes de ver las soluciones.

---

## 📊 Criterios de Evaluación

Para cada ejercicio, considera:

1. **Funcionalidad** (40%)
   - ¿El código funciona correctamente?
   - ¿Maneja casos edge?

2. **Código Limpio** (30%)
   - ¿Es legible?
   - ¿Tiene buenos nombres de variables?
   - ¿Está bien documentado?

3. **Diseño** (20%)
   - ¿Sigue el patrón de las demás clases?
   - ¿Es fácil de extender?

4. **Manejo de Errores** (10%)
   - ¿Valida entradas?
   - ¿Maneja excepciones?

---

## 💡 Consejos

1. **Empieza simple:** Haz que funcione primero, optimiza después
2. **Prueba frecuentemente:** Ejecuta el código después de cada cambio
3. **Lee la documentación:** [Pillow Docs](https://pillow.readthedocs.io/)
4. **Pide ayuda:** Si te atascas, revisa los ejemplos existentes

¡Buena suerte! 🚀


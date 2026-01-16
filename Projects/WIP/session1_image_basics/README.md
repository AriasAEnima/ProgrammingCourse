# 📸 Sesión 1: Fundamentos de Procesamiento de Imágenes

## 🎯 Objetivos de la Sesión (45 min)

1. **Entender conceptos básicos** de procesamiento de imágenes
2. **Conocer la librería Pillow** (PIL fork)
3. **Implementar filtros simples** de manera modular
4. **Crear código limpio** y reutilizable

---

## 📚 Conceptos Clave

### ¿Qué es una imagen digital?

Una imagen digital es una **matriz de píxeles**. Cada píxel tiene:
- **RGB**: 3 canales de color (Red, Green, Blue)
- **Valores**: 0-255 por canal
- **Ejemplo**: `(255, 0, 0)` = Rojo puro

### ¿Qué es un filtro?

Un **filtro** es una función que **transforma** una imagen:
```
Imagen Original → [Filtro] → Imagen Modificada
```

Ejemplos:
- **Blur**: Suaviza la imagen
- **Brightness**: Ajusta brillo
- **Edges**: Detecta bordes
- **Sharpen**: Aumenta nitidez

---

## 📂 Estructura del Proyecto

```
session1_image_basics/
├── README.md                    # Esta guía
├── requirements.txt             # Dependencias
├── images/                      # Imágenes de prueba
│   └── sample.jpg
├── filters/                     # Módulo de filtros
│   ├── __init__.py
│   ├── base_filter.py          # Clase base abstracta
│   ├── blur_filter.py          # Filtro de desenfoque
│   ├── brightness_filter.py    # Filtro de brillo
│   └── edges_filter.py         # Filtro de detección de bordes
├── simple_processor.py          # Ejemplo básico de uso
└── demo_all_filters.py          # Demo de todos los filtros
```

---

## 🔧 Instalación

```bash
# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  
# En Windows: 
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 🚀 Uso

### 1. Ejemplo Básico

```bash
python simple_processor.py
```

Este script:
1. Carga una imagen
2. Aplica un filtro de blur
3. Guarda el resultado

### 2. Demo de Todos los Filtros

```bash
python demo_all_filters.py
```

Genera múltiples versiones de la imagen con diferentes filtros.

---

## 📖 Explicación del Código

### 1. Clase Base: `BaseFilter`

Todos los filtros heredan de esta clase abstracta:

```python
class BaseFilter:
    def apply(self, image):
        """Aplica el filtro a la imagen"""
        raise NotImplementedError
```

**¿Por qué usar una clase base?**
- ✅ Interfaz consistente
- ✅ Fácil de extender
- ✅ Polimorfismo

### 2. Filtro de Blur

```python
class BlurFilter(BaseFilter):
    def __init__(self, radius=2):
        self.radius = radius
    
    def apply(self, image):
        return image.filter(ImageFilter.GaussianBlur(self.radius))
```

**¿Qué hace?**
- Aplica un desenfoque gaussiano
- El `radius` controla la intensidad

### 3. Filtro de Brightness

```python
class BrightnessFilter(BaseFilter):
    def __init__(self, factor=1.5):
        self.factor = factor  # 1.0 = sin cambio, >1 = más brillante
    
    def apply(self, image):
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(self.factor)
```

**¿Qué hace?**
- Multiplica el brillo de cada píxel
- `factor=0.5` → imagen más oscura
- `factor=2.0` → imagen más brillante

### 4. Filtro de Edges

```python
class EdgesFilter(BaseFilter):
    def apply(self, image):
        return image.filter(ImageFilter.FIND_EDGES)
```

**¿Qué hace?**
- Detecta bordes usando gradientes
- Útil para computer vision

---

## 🎨 Ejercicios Prácticos

### Ejercicio 1: Crear tu propio filtro
Crea un filtro que convierta la imagen a **escala de grises**:

```python
class GrayscaleFilter(BaseFilter):
    def apply(self, image):
        return image.convert('L')  # L = Luminance (grayscale)
```

### Ejercicio 2: Combinar filtros
Aplica múltiples filtros en secuencia:

```python
# 1. Aumentar brillo
# 2. Aplicar blur
# 3. Detectar bordes
```

### Ejercicio 3: Filtro con parámetros
Crea un filtro de **rotación** que acepte ángulos:

```python
class RotateFilter(BaseFilter):
    def __init__(self, angle=90):
        self.angle = angle
    
    def apply(self, image):
        return image.rotate(self.angle)
```

---

## 🔍 Conceptos Importantes

### 1. Inmutabilidad
Los filtros **no modifican** la imagen original:
```python
original = Image.open('sample.jpg')
blurred = blur_filter.apply(original)  # original NO cambia
```

### 2. Cadena de Filtros (Pipeline)
```python
result = image
result = blur_filter.apply(result)
result = brightness_filter.apply(result)
result = edges_filter.apply(result)
```

### 3. Separación de Responsabilidades
- `BaseFilter`: Define interfaz
- `BlurFilter`: Implementa lógica específica
- `simple_processor.py`: Coordina el flujo

---

## 📊 Próxima Sesión

En la **Sesión 2** veremos:
- ✅ Cadena de filtros automatizada
- ✅ Factory pattern para crear filtros
- ✅ Procesamiento de múltiples imágenes
- ✅ Medición de performance

---

## 🤔 Preguntas Frecuentes

### ¿Por qué Pillow y no OpenCV?
- **Pillow**: Simple, ligero, ideal para operaciones básicas
- **OpenCV**: Potente pero complejo, mejor para computer vision avanzado

### ¿Los filtros son rápidos?
- Depende del tamaño de la imagen
- Imágenes grandes (>4K) pueden tardar segundos
- En sesiones futuras optimizaremos con workers

### ¿Puedo usar mis propias imágenes?
¡Sí! Coloca cualquier imagen en la carpeta `images/` y cambia la ruta en los scripts.

---

## 📚 Referencias

- [Pillow Documentation](https://pillow.readthedocs.io/)
- [Image Filters Explained](https://en.wikipedia.org/wiki/Image_filter)
- [Digital Image Processing Basics](https://en.wikipedia.org/wiki/Digital_image_processing)


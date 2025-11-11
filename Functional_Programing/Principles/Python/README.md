# Programación Funcional en Python

Este directorio contiene ejemplos y principios de programación funcional implementados en Python.

## 📁 Archivos Disponibles

### 🔧 Conceptos Básicos
- **`paradigms.py`** - Comparación entre paradigmas de programación
- **`principles_inmutability.py`** - Principios de inmutabilidad

### 🔄 Funciones de Orden Superior
- **`high_order.py`** - Ejemplos básicos de funciones de orden superior
- **`map_impl.py`** - Implementaciones de map
- **`python_map.py`** - Uso avanzado de map
- **`python_filter.py`** - Uso avanzado de filter  
- **`python_reduce.py`** - Uso básico de reduce
- **`reduce_advanced.py`** - Uso avanzado de reduce

### ⚙️ Conceptos Avanzados
- **`decorators_generators.py`** - **NUEVO** Decoradores y generadores funcionales
- **`no_for.py`** - Programación sin loops explícitos

### 📝 Tareas
- **`homework_0.py`** - Tarea práctica 0
- **`homework_1.py`** - Tarea práctica 1

## 🎯 Nuevo Archivo: `decorators_generators.py`

### 📖 Contenido del Archivo

El archivo `decorators_generators.py` incluye ejemplos completos de:

#### 🎭 Decoradores Funcionales
- **Decoradores puros**: Memoización sin efectos secundarios
- **Decoradores con efectos secundarios**: Medición de tiempo
- **Validación de tipos**: Usando programación funcional
- **Composición de decoradores**: Aplicación funcional de múltiples decoradores

#### 🔄 Generadores y Lazy Evaluation
- **Generadores infinitos**: Como la secuencia de Fibonacci
- **Operaciones funcionales**: filter, map para generadores
- **Pipelines funcionales**: Composición de operaciones lazy
- **Chain de generadores**: Concatenación perezosa

### 🚀 Ejemplos Destacados

#### Decorador de Memoización Pura
```python
@pure_memoize
def fibonacci_memoized(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci_memoized(n-1) + fibonacci_memoized(n-2)
```

#### Pipeline Funcional
```python
# Números 1-20 -> cuadrados -> pares -> primeros 5
pipeline_result = functional_pipeline(
    numbers,
    squares_operation,
    evens_operation, 
    limit_operation(5)
)
```

#### Generador Infinito con Lazy Evaluation
```python
def infinite_fibonacci() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
```

### ⚡ Cómo Ejecutar

```bash
cd Chapter9_Functional_Programing/Principles/Python
python decorators_generators.py
```

### 📊 Salida Esperada

El programa demuestra:
- Fibonacci con memoización (optimization)
- Validación de tipos con decoradores
- Pipelines funcionales con generadores
- Composición de generadores
- Lazy evaluation en acción

## 🎓 Principios Funcionales Demostrados

1. **Funciones de Orden Superior**: Decoradores como funciones que toman/retornan funciones
2. **Inmutabilidad**: Uso de estructuras inmutables en decoradores
3. **Lazy Evaluation**: Generadores que calculan valores solo cuando se necesitan
4. **Composición**: Combinación de funciones para crear comportamientos complejos
5. **Pureza**: Separación entre funciones puras e impuras
6. **Sin Efectos Secundarios**: Pipelines que no modifican estado externo

## 🔗 Relación con Otros Archivos

- Conecta con `high_order.py` mostrando decoradores como funciones de orden superior
- Complementa `python_map.py` y `python_filter.py` con versiones lazy usando generadores
- Extiende `reduce_advanced.py` mostrando pipelines funcionales
- Demuestra los principios de `principles_inmutability.py` en contextos prácticos

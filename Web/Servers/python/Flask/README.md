# 🚀 API REST con Flask - Guía Completa

Este proyecto muestra cómo crear una API REST completa usando Flask, incluyendo operaciones CRUD (Create, Read, Update, Delete) para un sistema de gestión de tareas.

## 📋 Tabla de Contenidos

1. [¿Qué es Flask?](#qué-es-flask)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Explicación del Código](#explicación-del-código)
5. [Endpoints de la API](#endpoints-de-la-api)
6. [Ejemplos de Uso](#ejemplos-de-uso)
7. [Conceptos Clave](#conceptos-clave)

## 🤔 ¿Qué es Flask?

Flask es un micro-framework web de Python que te permite crear aplicaciones web y APIs de forma rápida y sencilla. Es "micro" porque no incluye herramientas como ORM o validadores por defecto, pero es muy extensible.

### Ventajas de Flask:
- ✅ Ligero y minimalista
- ✅ Fácil de aprender
- ✅ Muy flexible y personalizable
- ✅ Excelente documentación
- ✅ Gran comunidad

## 📁 Estructura del Proyecto

```
Flask/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
└── README.md          # Esta documentación
```

## 🛠️ Instalación y Configuración

### Paso 1: Crear entorno virtual (recomendado)

```bash
# Crear entorno virtual
python -m venv flask_env

# Activar entorno virtual
# En macOS/Linux:
source flask_env/bin/activate
# En Windows:
flask_env\Scripts\activate
```

### Paso 2: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Ejecutar la aplicación

```bash
python app.py
```

La API estará disponible en: `http://localhost:5000`

## 🧐 Explicación del Código

### Importaciones y Configuración

```python
from flask import Flask, jsonify, request
from datetime import datetime
import uuid

app = Flask(__name__)
```

- `Flask`: Clase principal para crear la aplicación
- `jsonify`: Convierte datos Python a JSON
- `request`: Acceso a datos de la petición HTTP
- `datetime`: Para manejar fechas
- `uuid`: Para generar IDs únicos

### Base de Datos Simulada

```python
tasks = [
    {
        'id': '1',
        'title': 'Aprender Flask',
        'description': 'Completar el tutorial de Flask API',
        'completed': False,
        'created_at': '2024-01-15T10:00:00Z'
    }
]
```

Usamos una lista en memoria para simplificar. En producción usarías una base de datos real como PostgreSQL, MySQL o MongoDB.

### Decoradores de Ruta

```python
@app.route('/tasks', methods=['GET'])
def get_tasks():
    # Lógica del endpoint
```

- `@app.route()`: Define la URL y métodos HTTP
- `methods=['GET']`: Especifica qué métodos acepta

### Manejo de Errores

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Recurso no encontrado'
    }), 404
```

Captura errores globalmente y devuelve respuestas JSON consistentes.

## 🌐 Endpoints de la API

### GET / - Información de la API
```
GET http://localhost:5000/
```
Devuelve información sobre la API y endpoints disponibles.

### GET /tasks - Obtener todas las tareas
```
GET http://localhost:5000/tasks
GET http://localhost:5000/tasks?completed=true
```
- Sin parámetros: devuelve todas las tareas
- `?completed=true/false`: filtra por estado

### GET /tasks/<id> - Obtener tarea específica
```
GET http://localhost:5000/tasks/1
```
Devuelve una tarea específica por su ID.

### POST /tasks - Crear nueva tarea
```
POST http://localhost:5000/tasks
Content-Type: application/json

{
  "title": "Mi nueva tarea",
  "description": "Descripción opcional"
}
```

### PUT /tasks/<id> - Actualizar tarea completa
```
PUT http://localhost:5000/tasks/1
Content-Type: application/json

{
  "title": "Tarea actualizada",
  "description": "Nueva descripción",
  "completed": true
}
```

### PATCH /tasks/<id> - Actualización parcial
```
PATCH http://localhost:5000/tasks/1
Content-Type: application/json

{
  "completed": true
}
```

### DELETE /tasks/<id> - Eliminar tarea
```
DELETE http://localhost:5000/tasks/1
```

## 🚀 Ejemplos de Uso

### Usando curl (desde terminal)

```bash
# Obtener todas las tareas
curl http://localhost:5000/tasks

# Crear nueva tarea
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Estudiar Flask", "description": "Completar tutorial"}'

# Actualizar tarea
curl -X PATCH http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Eliminar tarea
curl -X DELETE http://localhost:5000/tasks/1
```

### Usando Python requests

```python
import requests

# Obtener tareas
response = requests.get('http://localhost:5000/tasks')
tasks = response.json()
print(tasks)

# Crear nueva tarea
new_task = {
    "title": "Aprender Python",
    "description": "Estudiar conceptos avanzados"
}
response = requests.post('http://localhost:5000/tasks', json=new_task)
print(response.json())
```

### Usando JavaScript fetch

```javascript
// Obtener tareas
fetch('http://localhost:5000/tasks')
  .then(response => response.json())
  .then(data => console.log(data));

// Crear nueva tarea
fetch('http://localhost:5000/tasks', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'Nueva tarea',
    description: 'Descripción de la tarea'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🤨 Conceptos Clave

### REST (Representational State Transfer)
- **GET**: Obtener recursos
- **POST**: Crear recursos
- **PUT**: Actualizar completo
- **PATCH**: Actualizar parcial
- **DELETE**: Eliminar recursos

### Códigos de Estado HTTP
- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado
- **404 Not Found**: Recurso no encontrado
- **400 Bad Request**: Datos inválidos
- **500 Internal Server Error**: Error del servidor

### JSON (JavaScript Object Notation)
Formato estándar para intercambio de datos:
```json
{
  "id": "1",
  "title": "Tarea ejemplo",
  "completed": false
}
```

### Diferencia PUT vs PATCH
- **PUT**: Reemplaza el recurso completo
- **PATCH**: Actualiza solo los campos enviados

## 🔧 Mejoras Sugeridas

Para llevar esta API a producción, considera:

1. **Base de datos real**: SQLAlchemy + PostgreSQL
2. **Autenticación**: JWT tokens
3. **Validación**: Marshmallow schemas
4. **Documentación**: Swagger/OpenAPI
5. **Testing**: pytest
6. **Logging**: configuración de logs
7. **CORS**: para acceso desde frontend
8. **Paginación**: para listas grandes
9. **Rate limiting**: controlar abuso
10. **Docker**: containerización

## 📚 Recursos Adicionales

- [Documentación oficial de Flask](https://flask.palletsprojects.com/)
- [Flask RESTful](https://flask-restful.readthedocs.io/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)

---

## 🎯 Proyectos de Práctica con Flask

Implementa estas APIs siguiendo el mismo patrón de la API de tareas:

### 📚 Libros
- **Endpoint**: `/api/libros/`
- **Campos**: titulo, autor, año_publicacion, genero, num_paginas, isbn, precio, disponible

### 💻 Laptops  
- **Endpoint**: `/api/laptops/`
- **Campos**: marca, modelo, procesador, ram_gb, almacenamiento_gb, tipo_disco, precio, año

### 🎬 Películas
- **Endpoint**: `/api/peliculas/`
- **Campos**: titulo, director, año, genero, duracion_min, calificacion, idioma_original

### 🍕 Restaurantes
- **Endpoint**: `/api/restaurantes/`
- **Campos**: nombre, tipo_cocina, direccion, telefono, calificacion, precio_promedio, delivery

### 🌱 Plantas
- **Endpoint**: `/api/plantas/`
- **Campos**: nombre, especie, tipo_planta, altura_cm, cuidados, interior_exterior, precio

¡Ahora tienes una API REST completa con Flask y muchos proyectos para practicar! 🎉

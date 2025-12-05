# 🎯 Ejercicio 3: Formularios con MongoDB (Sin Autenticación)

**Tiempo estimado:** 15 minutos  
**Nivel:** Intermedio  
**Objetivo:** Agregar **formularios** para crear muebles en el catálogo

---

## 🎯 Lo que Vamos a Agregar

- ✅ **Formulario** para crear muebles en MongoDB
- ✅ **Templates** con Bootstrap
- ✅ **Sin autenticación** (acceso público)

**Flujo:** Ver catálogo → Agregar mueble → Ver mueble en el catálogo

---

## 📋 Prerrequisitos

- ✅ Ejercicio 1 y 2 completados
- ✅ Catálogo funcionando en `http://127.0.0.1:8000/dynamic-pages/`
- ✅ MongoDB corriendo

---

## 📋 Parte 1: Actualizar Vista para Crear Muebles (5 minutos)

### 1.1 Vista crear_mueble en `dynamicpages/views.py`

```python
# dynamicpages/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FurnitureItem

def lista_muebles(request):
    """Vista que consulta MongoDB y muestra muebles"""
    muebles = FurnitureItem.objects.filter(publicado=True).order_by('-fecha_creacion')
    
    contexto = {
        'muebles': muebles,
        'titulo_pagina': 'Catálogo de Muebles'
    }
    
    return render(request, 'dynamicpages/lista_muebles.html', contexto)

def crear_mueble(request):
    """Vista para crear un nuevo mueble (sin autenticación)"""
    if request.method == 'POST':
        mueble = FurnitureItem(
            nombre=request.POST['nombre'],
            descripcion=request.POST['descripcion'],
            altura=int(request.POST['altura']),
            ancho=int(request.POST['ancho']),
            material=request.POST['material'],
            autor_username=request.POST.get('autor', 'Anónimo'),
            publicado=True
        )
        mueble.save()
        
        messages.success(request, f'Mueble "{mueble.nombre}" agregado exitosamente!')
        return redirect('lista_muebles')
    
    return render(request, 'dynamicpages/crear_mueble.html')
```

---

## 📋 Parte 2: Templates Mejorados (10 minutos)

### 2.1 Actualizar template base `dynamicpages/templates/dynamicpages/base.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ titulo_pagina }} - Furniture Catalog</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/dynamic-pages/">🪑 Furniture Catalog</a>
            
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/static-pages/">📄 Páginas Estáticas</a>
                <a class="nav-link" href="/dynamic-pages/crear/">✍️ Agregar Mueble</a>
                <a class="nav-link" href="/api/furniture/">🔌 API</a>
            </div>
        </div>
    </nav>
    
    {% if messages %}
        <div class="container mt-3">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        </div>
    {% endif %}
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### 2.2 Actualizar lista de muebles `dynamicpages/templates/dynamicpages/lista_muebles.html`

```html
{% extends 'dynamicpages/base.html' %}

{% block content %}
<h2>🪑 Catálogo de Muebles (MongoDB)</h2>

<a href="/dynamic-pages/crear/" class="btn btn-primary mb-3">✍️ Agregar Nuevo Mueble</a>

<div class="row">
    {% for mueble in muebles %}
        <div class="col-md-6 mb-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{{ mueble.nombre }}</h5>
                    <p class="card-text">{{ mueble.descripcion|truncatewords:15 }}</p>
                    <p><strong>Dimensiones:</strong> {{ mueble.altura }}cm x {{ mueble.ancho }}cm</p>
                    <p><strong>Material:</strong> {{ mueble.material }}</p>
                    <small class="text-muted">
                        Por {{ mueble.autor_username }} el {{ mueble.fecha_creacion|date:"d/m/Y" }}
                    </small>
                </div>
            </div>
        </div>
    {% empty %}
        <div class="col-12 text-center py-5">
            <h4 class="text-muted">No hay muebles registrados aún</h4>
            <a href="/dynamic-pages/crear/" class="btn btn-primary mt-3">✍️ Agregar el primer mueble</a>
        </div>
    {% endfor %}
</div>
{% endblock %}
```

### 2.3 Template para crear mueble `dynamicpages/templates/dynamicpages/crear_mueble.html`

```html
{% extends 'dynamicpages/base.html' %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <h2>✍️ Agregar Nuevo Mueble</h2>
        
        <form method="post" class="mt-4">
            {% csrf_token %}
            
            <div class="mb-3">
                <label class="form-label">Nombre del Mueble</label>
                <input type="text" class="form-control" name="nombre" required>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Descripción</label>
                <textarea class="form-control" name="descripcion" rows="3" required></textarea>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Altura (cm)</label>
                    <input type="number" class="form-control" name="altura" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Ancho (cm)</label>
                    <input type="number" class="form-control" name="ancho" required>
                </div>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Material</label>
                <input type="text" class="form-control" name="material" placeholder="ej: Madera de roble" required>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Tu Nombre (opcional)</label>
                <input type="text" class="form-control" name="autor" placeholder="Anónimo">
                <small class="text-muted">Deja vacío para aparecer como "Anónimo"</small>
            </div>
            
            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <a href="/dynamic-pages/" class="btn btn-secondary me-md-2">Cancelar</a>
                <button type="submit" class="btn btn-primary">📝 Guardar Mueble</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

---

## ✅ Verificación Final

### Prueba el catálogo completo:

```bash
python manage.py runserver
```

### Flujo de prueba:

1. ✅ **Ir a `http://127.0.0.1:8000/dynamic-pages/`** → Ver catálogo
2. ✅ **Hacer clic en "Agregar Nuevo Mueble"** → Llenar formulario
3. ✅ **Guardar mueble** → Se guarda en MongoDB
4. ✅ **Ver el mueble** en la lista principal

### Debe funcionar:

- ✅ Navegación simple (sin login/registro)
- ✅ Mensajes de feedback cuando se agrega un mueble
- ✅ Crear muebles directamente (sin autenticación)
- ✅ Ver todos los muebles del catálogo
- ✅ Diseño responsive con Bootstrap

---

## 🎓 Lo que Aprendiste

### Django Formularios:
- ✅ **Formularios HTML:** Campos con Bootstrap
- ✅ **POST requests:** Procesar datos del formulario
- ✅ **CSRF:** Protección contra ataques cross-site
- ✅ **Redirect:** Redirigir después de guardar
- ✅ **Messages framework:** Feedback al usuario

### MongoDB con Django:
- ✅ **MongoEngine:** Guardar documentos fácilmente
- ✅ **Sin esquema fijo:** Flexibilidad de MongoDB
- ✅ **Queries:** `filter()`, `order_by()`
- ✅ **Documentos:** Datos en formato JSON-like

### Django Templates:
- ✅ **Template inheritance:** Reutilizar código
- ✅ **Context variables:** Pasar datos dinámicos
- ✅ **Template tags:** `{% for %}`, `{% if %}`
- ✅ **Bootstrap integration:** Diseño moderno

---

## 🎯 Arquitectura Final

```
┌──────────────────────┐
│     MongoDB          │
│                      │
│  - furniture_items   │
│    └── nombre        │
│    └── descripcion   │
│    └── altura        │
│    └── ancho         │
│    └── material      │
│    └── autor_username│
└──────────────────────┘
          ↑
          │ MongoEngine
          │
┌─────────┴────────────┐
│  Django Templates    │
│                      │
│  - lista_muebles     │
│  - crear_mueble      │
└──────────────────────┘
```

**¡Tienes un catálogo de muebles funcional! 🎉**  
Con formularios, MongoDB y diseño profesional, todo sin necesidad de autenticación.

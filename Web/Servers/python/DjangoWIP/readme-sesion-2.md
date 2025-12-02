# 🎯 Ejercicio 2: Templates Dinámicos y API REST

**Tiempo estimado:** 45 minutos  
**Nivel:** Intermedio  
**Objetivo:** Agregar **base de datos**, **templates dinámicos** y **API JSON**

---

## 🚀 Lo que Vamos a Construir

Un sistema completo que demuestre **3 enfoques diferentes** en Django:
- 🎨 **Templates Dinámicos** - HTML generado desde base de datos
- 🔌 **API REST** - Datos en formato JSON
- 📄 **Comparación** con páginas estáticas del Ejercicio 1

**Concepto clave:** El mismo dato se puede servir de múltiples formas.

---

## 📋 Parte 1: Crear Modelos y Base de Datos (15 minutos)

### 1.1 Crear app para contenido dinámico
```bash
python manage.py startapp dynamicpages
```

### 1.2 Registrar apps en `settings.py`
```python
# furniture_app/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',    # Para API JSON
    'staticpages',       # Del ejercicio 1
    'dynamicpages',      # Nueva app
]
```

### 1.3 Instalar Django REST Framework y MongoEngine
```bash
pip install djangorestframework mongoengine
```

### 1.4 Crear modelo en `dynamicpages/models.py`

> **📌 Este proyecto usa MongoDB con MongoEngine** - Los modelos heredan de `Document` en lugar de `models.Model`.

```python
# dynamicpages/models.py
from mongoengine import Document, StringField, IntField, DateTimeField, BooleanField
from datetime import datetime

class FurnitureItem(Document):
    """Modelo de mueble - se guarda en MongoDB"""
    nombre = StringField(max_length=200, required=True)
    descripcion = StringField(required=True)
    altura = IntField(required=True)  # en cm
    ancho = IntField(required=True)   # en cm
    material = StringField(max_length=100, required=True)
    autor_username = StringField(required=True, default='Anónimo')
    fecha_creacion = DateTimeField(default=datetime.now)
    publicado = BooleanField(default=True)
    
    meta = {
        'collection': 'furniture_items',  # Nombre de la colección en MongoDB
        'ordering': ['-fecha_creacion']
    }
    
    def __str__(self):
        return self.nombre
```

**✨ Ventajas de MongoDB:**
- ❌ **NO necesitas migraciones** - La colección se crea automáticamente
- ✅ Esquema flexible - Puedes agregar campos sin migraciones
- ✅ Los documentos se guardan como JSON

---

## 📋 Parte 2: Templates Dinámicos (20 minutos)

### 2.1 Entender la Sintaxis de Templates Django

Django usa **Django Template Language (DTL)** con esta sintaxis:

| Sintaxis | Uso | Ejemplo |
|----------|-----|---------|
| `{{ variable }}` | **Mostrar datos** | `{{ mueble.nombre }}` |
| `{% tag %}` | **Lógica de control** | `{% for item in lista %}` |
| `{% comment %}` | **Comentarios** | `{% comment %}Nota{% endcomment %}` |
| `{{ var\|filter }}` | **Filtros** | `{{ fecha\|date:"d/m/Y" }}` |

### 2.2 Crear template base - `dynamicpages/templates/dynamicpages/base.html`
```bash
mkdir -p dynamicpages/templates/dynamicpages
```

```html
<!-- dynamicpages/templates/dynamicpages/base.html -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Furniture Catalog{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }
        .container { max-width: 800px; margin: 0 auto; background: white; 
                    padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .furniture-item { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .meta { color: #666; font-size: 0.9em; margin-top: 10px; }
        nav a { margin-right: 15px; text-decoration: none; color: #007cba; font-weight: bold; }
        nav a:hover { text-decoration: underline; }
        h1 a { color: #333; text-decoration: none; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1><a href="{% url 'lista_muebles' %}">🪑 Catálogo de Muebles</a></h1>
            <nav>
                <a href="/static-pages/">📄 Static Pages</a>
                <a href="/dynamic-pages/">🪑 Catálogo</a>
                <a href="/api/furniture/">🔌 API JSON</a>
            </nav>
        </div>
    </header>
    
    <main class="container">
        {% block content %}
        <!-- Aquí se insertará el contenido específico de cada página -->
        {% endblock %}
    </main>
</body>
</html>
```

**🔍 Explicación de Sintaxis:**
- `{% block title %}...{% endblock %}`: **Bloque que se puede sobrescribir** en templates hijos
- `{% url 'lista_muebles' %}`: **Genera URL** basándose en el nombre de la URL
- `{% block content %}...{% endblock %}`: **Área donde templates hijos insertan contenido**

### 2.3 Template para lista - `dynamicpages/templates/dynamicpages/lista_muebles.html`
```html
<!-- dynamicpages/templates/dynamicpages/lista_muebles.html -->
{% extends 'dynamicpages/base.html' %}

{% block title %}{{ titulo_pagina }}{% endblock %}

{% block content %}
<h2>🪑 Catálogo de Muebles (Desde Base de Datos)</h2>

{% for mueble in muebles %}
    <div class="furniture-item">
        <h3><a href="{% url 'detalle_mueble' mueble.id %}">{{ mueble.nombre }}</a></h3>
        <p>{{ mueble.descripcion|truncatewords:30 }}</p>
        <p><strong>Dimensiones:</strong> {{ mueble.altura }}cm x {{ mueble.ancho }}cm</p>
        <p><strong>Material:</strong> {{ mueble.material }}</p>
        <div class="meta">
            Por {{ mueble.autor_username }} el {{ mueble.fecha_creacion|date:"d/m/Y H:i" }}
            {% if mueble.publicado %}
                | ✅ Publicado
            {% else %}
                | ⏳ Borrador
            {% endif %}
        </div>
    </div>
{% empty %}
    <div class="furniture-item">
        <h3>No hay muebles aún</h3>
        <p>¡Pronto habrá contenido!</p>
    </div>
{% endfor %}

<div style="margin-top: 30px; text-align: center;">
    <small>Total de muebles: {{ muebles|length }}</small>
</div>
{% endblock %}
```

**🔍 Explicación de Sintaxis:**
- `{% extends 'base.html' %}`: **Hereda** de template base
- `{% for item in lista %}...{% empty %}...{% endfor %}`: **Bucle con caso vacío**
- `{{ var|filter }}`: **Filtros** para formatear datos
- `{% if condicion %}...{% else %}...{% endif %}`: **Condicionales**

### 2.4 Template para detalle - `dynamicpages/templates/dynamicpages/detalle_mueble.html`
```html
<!-- dynamicpages/templates/dynamicpages/detalle_mueble.html -->
{% extends 'dynamicpages/base.html' %}

{% block title %}{{ mueble.nombre }}{% endblock %}

{% block content %}
<article>
    <h2>{{ mueble.nombre }}</h2>
    <div class="meta">
        Por <strong>{{ mueble.autor_username }}</strong> el 
        {{ mueble.fecha_creacion|date:"d/m/Y H:i" }}
    </div>
    
    <div style="margin-top: 20px; line-height: 1.6;">
        <p><strong>Descripción:</strong></p>
        {{ mueble.descripcion|linebreaks }}
        
        <p><strong>Especificaciones:</strong></p>
        <ul>
            <li>Altura: {{ mueble.altura }} cm</li>
            <li>Ancho: {{ mueble.ancho }} cm</li>
            <li>Material: {{ mueble.material }}</li>
        </ul>
    </div>
    
    {% comment %}
    Los filtros más comunes:
    - |linebreaks: Convierte saltos de línea en <br> y <p>
    - |date:"formato": Formatea fechas
    - |truncatewords:N: Corta texto a N palabras
    - |length: Cuenta elementos
    {% endcomment %}
</article>

<div style="margin-top: 30px;">
    <a href="{% url 'lista_muebles' %}">← Volver al catálogo</a>
</div>
{% endblock %}
```

### 2.5 Crear vistas en `dynamicpages/views.py`
```python
# dynamicpages/views.py
from django.shortcuts import render, get_object_or_404
from .models import FurnitureItem

def lista_muebles(request):
    """Vista que consulta MongoDB y pasa datos al template"""
    # MongoEngine usa la misma sintaxis de consulta que Django ORM
    muebles = FurnitureItem.objects.filter(publicado=True).order_by('-fecha_creacion')
    
    # El contexto son los datos que se pasan al template
    contexto = {
        'muebles': muebles,
        'titulo_pagina': 'Catálogo de Muebles'
    }
    
    # render() combina el template con el contexto
    return render(request, 'dynamicpages/lista_muebles.html', contexto)

def detalle_mueble(request, mueble_id):
    """Vista que muestra un mueble específico desde MongoDB"""
    # En MongoDB el ID es un ObjectId, pero podemos usar el string
    mueble = FurnitureItem.objects.get(id=mueble_id, publicado=True)
    
    contexto = {
        'mueble': mueble
    }
    
    return render(request, 'dynamicpages/detalle_mueble.html', contexto)
```

### 2.6 Configurar URLs - `dynamicpages/urls.py`
```python
# dynamicpages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_muebles, name='lista_muebles'),
    path('mueble/<str:mueble_id>/', views.detalle_mueble, name='detalle_mueble'),
]
```

---

## 📋 Parte 3: API REST (10 minutos)

### 3.1 Crear app API
```bash
python manage.py startapp api
```

### 3.2 ¿Qué son los Serializers?

**🔄 Problema:** Los modelos Django no se pueden enviar directamente como JSON

```python
# ❌ Esto NO funciona:
mueble = FurnitureItem.objects.get(id=1)
return JsonResponse(mueble)  # Error! No puede convertir objeto a JSON
```

**✅ Solución:** Los **Serializers** convierten entre modelos Django ↔ JSON

```
Modelo Django  ←→  Serializer  ←→  JSON
    FurnitureItem  ←→  FurnitureItemSerializer  ←→  {"id": 1, "nombre": "..."}
```

### 3.3 Crear serializer - `furniture_api/serializers.py`

> **📌 NOTA:** Con MongoDB, usamos serializers regulares (no `ModelSerializer`) porque MongoEngine no es compatible con `ModelSerializer` de DRF.

```python
# furniture_api/serializers.py
from rest_framework import serializers
from dynamicpages.models import FurnitureItem

class FurnitureItemSerializer(serializers.Serializer):
    """Convierte FurnitureItem (MongoDB) ↔ JSON"""
    id = serializers.CharField(read_only=True)
    nombre = serializers.CharField(max_length=200)
    descripcion = serializers.CharField()
    altura = serializers.IntegerField()
    ancho = serializers.IntegerField()
    material = serializers.CharField(max_length=100)
    autor_username = serializers.CharField(default='Anónimo')
    fecha_creacion = serializers.DateTimeField(read_only=True)
    publicado = serializers.BooleanField(default=True)
    
    def create(self, validated_data):
        """Crear nuevo mueble en MongoDB"""
        return FurnitureItem(**validated_data).save()
    
    def update(self, instance, validated_data):
        """Actualizar mueble existente en MongoDB"""
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
```

**🔍 Explicación de Serializers:**

| **Operación** | **Código** | **Resultado** |
|---------------|------------|---------------|
| **Modelo → JSON** | `serializer.data` | `{"id": 1, "nombre": "Mesa"}` |
| **JSON → Modelo** | `serializer.save()` | Objeto FurnitureItem en BD |
| **Validación** | `serializer.is_valid()` | `True/False` + errores |

**✨ Lo que hace automáticamente:**
- ✅ **Convierte tipos**: `DateTimeField` → string ISO
- ✅ **Validación**: Campos requeridos, tipos correctos
- ✅ **Bidireccional**: Modelo → JSON y JSON → Modelo

### 3.4 Crear vistas API - `furniture_api/views.py`
```python
# furniture_api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from dynamicpages.models import FurnitureItem
from .serializers import FurnitureItemSerializer

@api_view(['GET'])
def lista_muebles(request):
    """
    API manual - Solo lista todos los muebles
    GET /api/furniture/ → Lista todos los muebles en JSON
    """
    # Obtener todos los muebles publicados
    muebles = FurnitureItem.objects.filter(publicado=True).order_by('-fecha_creacion')
    
    # Convertir a JSON usando el serializer
    serializer = FurnitureItemSerializer(muebles, many=True)
    
    # Devolver respuesta JSON
    return Response({
        'count': len(muebles),
        'results': serializer.data
    })

@api_view(['POST'])
def crear_mueble(request):
    """
    API manual - Solo crear muebles
    POST /api/furniture/create/ → Crear nuevo mueble desde JSON
    """
    serializer = FurnitureItemSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def detalle_mueble(request, pk):
    """
    API completa para un mueble específico
    GET /api/furniture/1/ → Detalle en JSON
    PUT /api/furniture/1/ → Actualizar mueble
    DELETE /api/furniture/1/ → Eliminar mueble
    """
    # En MongoDB, pk puede ser el string del ObjectId
    mueble = get_object_or_404(FurnitureItem, pk=pk, publicado=True)
    
    if request.method == 'GET':
        serializer = FurnitureItemSerializer(mueble)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = FurnitureItemSerializer(mueble, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        mueble.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def estadisticas_catalogo(request):
    """
    Endpoint personalizado - Estadísticas del catálogo
    """
    from django.contrib.auth.models import User
    
    stats = {
        'total_items': FurnitureItem.objects.count(),
        'published_items': FurnitureItem.objects.filter(publicado=True).count(),
        'draft_items': FurnitureItem.objects.filter(publicado=False).count(),
    }
    
    # Obtener el mueble más reciente
    latest = FurnitureItem.objects.filter(publicado=True).order_by('-fecha_creacion').first()
    
    if latest:
        stats['latest_item'] = {
            'nombre': latest.nombre,
            'autor': latest.autor_username,
            'fecha': latest.fecha_creacion.strftime('%Y-%m-%d')
        }
    
    return Response(stats)
```

### 3.5 Configurar URLs - `furniture_api/urls.py`
```python
# furniture_api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs explícitas - cada acción tiene su propio endpoint
    path('', views.lista_muebles, name='api_lista_muebles'),
    path('create/', views.crear_mueble, name='api_crear_mueble'),
    path('<str:pk>/', views.detalle_mueble, name='api_detalle_mueble'),
    path('stats/', views.estadisticas_catalogo, name='api_estadisticas'),
]
```

**🔍 Explicación de URLs explícitas:**
- **Acción clara en la URL**: `/` vs `/create/` - no hay confusión
- **Una función por endpoint**: Cada URL hace una cosa específica
- **Parámetros claros**: `<str:pk>` captura el ID como string (MongoDB ObjectId)
- **Fácil de entender**: Se ve inmediatamente qué hace cada endpoint

### 3.6 Actualizar URLs principales - `furniture_app/urls.py`
```python
# furniture_app/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 📄 CONTENIDO ESTÁTICO (Ejercicio 1)
    path('static-pages/', include('staticpages.urls')),
    
    # 🪑 TEMPLATES DINÁMICOS (Catálogo)
    path('dynamic-pages/', include('dynamicpages.urls')),
    
    # 🔌 API JSON
    path('api/furniture/', include('furniture_api.urls')),
]
```

---

## 🚀 Probar los 3 Enfoques

```bash
# Solo localhost
python manage.py runserver

# Para acceso desde móviles (recuerda ALLOWED_HOSTS = ['*'])
python manage.py runserver 0.0.0.0:8000
```

### 📄 Páginas Estáticas (Ejercicio 1)
- `http://127.0.0.1:8000/static-pages/` → HTML fijo

### 🪑 Templates Dinámicos 
- `http://127.0.0.1:8000/dynamic-pages/` → Catálogo desde BD
- `http://127.0.0.1:8000/dynamic-pages/mueble/1/` → Detalle desde BD

### 🔌 API JSON
- `http://127.0.0.1:8000/api/furniture/` → Lista JSON
- `http://127.0.0.1:8000/api/furniture/create/` → Crear POST JSON
- `http://127.0.0.1:8000/api/furniture/1/` → Detalle JSON
- `http://127.0.0.1:8000/api/furniture/stats/` → Estadísticas
- `http://127.0.0.1:8000/api/v1/stats/` → Estadísticas JSON

---

## 📊 Estructura Final

```
furniture_app/
├── staticpages/             # 📄 Contenido estático
├── dynamicpages/            # 🪑 Templates dinámicos (Catálogo)
│   ├── models.py            # ✅ FurnitureItem model
│   ├── views.py             # ✅ Vistas que consultan BD
│   ├── templates/dynamicpages/
│   │   ├── base.html        # ✅ Template base
│   │   ├── lista_muebles.html     # ✅ Lista de muebles
│   │   └── detalle_mueble.html   # ✅ Detalle de mueble
├── furniture_api/           # 🔌 API REST
│   ├── serializers.py       # ✅ JSON conversion
│   ├── views.py             # ✅ API views
│   └── urls.py              # ✅ API routes
└── furniture_app/
    ├── settings.py          # ✅ Apps + DRF + MongoDB configuradas
    └── urls.py              # ✅ URLs organizadas
```

---

## 🎯 Conceptos Aprendidos

### ✅ Templates Dinámicos
- **{% extends %}**: Herencia de templates
- **{{ variable }}**: Mostrar datos del contexto
- **{% for %}**: Bucles con datos de BD
- **{% if %}**: Lógica condicional
- **|filtros**: Formatear datos

### ✅ Herencia de Templates
```
base.html (estructura común)
    ↓ {% extends %}
lista_muebles.html (contenido específico)
```

### ✅ API REST
- **@api_view**: Decorador para vistas API
- **request.method**: Manejo manual de GET/POST/PUT/DELETE
- **Serializers**: Conversión automática modelo ↔ JSON con validación
- **serializer.data**: Convierte modelo Django → JSON
- **serializer.save()**: Convierte JSON validado → modelo Django
- **Response()**: Construcción manual de respuestas JSON
- **Status codes**: Control explícito de códigos HTTP

### ✅ MongoDB con Django
- **MongoEngine**: ODM para trabajar con MongoDB desde Django
- **Document**: Clase base para modelos (similar a `models.Model`)
- **No migrations**: Schema-less, no necesita migraciones
- **ObjectId**: IDs únicos de MongoDB

### ✅ Comparación de Enfoques

| Tipo | URL | Datos | Uso |
|------|-----|-------|-----|
| **Estático** | `/static-pages/` | Fijos en código | Landing pages |
| **Dinámico** | `/dynamic-pages/` | Desde BD → HTML | Apps web |
| **API** | `/api/furniture/` | Desde BD → JSON | Apps móviles |

---

## ➡️ Próximo Paso

En el **Ejercicio 3** agregaremos:
- 📝 **Formularios** para agregar muebles
- 🎨 **Bootstrap** para mejor diseño
- 💬 **Mensajes** de feedback

**¡Ahora entiendes la diferencia entre contenido estático, dinámico y APIs!** 🎉
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
# mi_blog/settings.py
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

### 1.3 Instalar Django REST Framework
```bash
pip install djangorestframework
```

### 1.4 Crear modelo en `dynamicpages/models.py`
```python
# dynamicpages/models.py
from django.db import models
from django.contrib.auth.models import User

class BlogEntry(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    publicado = models.BooleanField(default=True)
    
    def __str__(self):
        return self.titulo
```

### 1.5 Crear y aplicar migraciones
```bash
# Crear migraciones para el nuevo modelo
python manage.py makemigrations dynamicpages

# Revisar qué migraciones se van a aplicar
python manage.py showmigrations

# Aplicar migraciones
python manage.py migrate
```

---

## 📋 Parte 2: Templates Dinámicos (20 minutos)

### 2.1 Entender la Sintaxis de Templates Django

Django usa **Django Template Language (DTL)** con esta sintaxis:

| Sintaxis | Uso | Ejemplo |
|----------|-----|---------|
| `{{ variable }}` | **Mostrar datos** | `{{ blogentry.titulo }}` |
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
    <title>{% block title %}Mi Blog Django{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }
        .container { max-width: 800px; margin: 0 auto; background: white; 
                    padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .blogentry { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .meta { color: #666; font-size: 0.9em; margin-top: 10px; }
        nav a { margin-right: 15px; text-decoration: none; color: #007cba; font-weight: bold; }
        nav a:hover { text-decoration: underline; }
        h1 a { color: #333; text-decoration: none; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1><a href="{% url 'lista_blogentries' %}">🎨 Dynamic Pages - Mi Blog</a></h1>
            <nav>
                <a href="/static-pages/">📄 Static Pages</a>
                <a href="/dynamic-pages/">🎨 Dynamic Pages</a>
                <a href="/api/v1/blogentries/">🔌 API JSON</a>
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
- `{% url 'lista_blogentries' %}`: **Genera URL** basándose en el nombre de la URL
- `{% block content %}...{% endblock %}`: **Área donde templates hijos insertan contenido**

### 2.3 Template para lista - `dynamicpages/templates/dynamicpages/lista_blogentries.html`
```html
<!-- dynamicpages/templates/dynamicpages/lista_blogentries.html -->
{% extends 'dynamicpages/base.html' %}

{% block title %}{{ titulo_pagina }}{% endblock %}

{% block content %}
<h2>📝 Entradas del Blog (Desde Base de Datos)</h2>

{% for blogentry in blogentries %}
    <div class="blogentry">
        <h3><a href="{% url 'detalle_blogentry' blogentry.id %}">{{ blogentry.titulo }}</a></h3>
        <p>{{ blogentry.contenido|truncatewords:30 }}</p>
        <div class="meta">
            Por {{ blogentry.autor.username }} el {{ blogentry.fecha_creacion|date:"d/m/Y H:i" }}
            {% if blogentry.publicado %}
                | ✅ Publicado
            {% else %}
                | ⏳ Borrador
            {% endif %}
        </div>
    </div>
{% empty %}
    <div class="blogentry">
        <h3>No hay entradas aún</h3>
        <p>¡Pronto habrá contenido!</p>
    </div>
{% endfor %}

<div style="margin-top: 30px; text-align: center;">
    <small>Total de entradas: {{ blogentries|length }}</small>
</div>
{% endblock %}
```

**🔍 Explicación de Sintaxis:**
- `{% extends 'base.html' %}`: **Hereda** de template base
- `{% for item in lista %}...{% empty %}...{% endfor %}`: **Bucle con caso vacío**
- `{{ var|filter }}`: **Filtros** para formatear datos
- `{% if condicion %}...{% else %}...{% endif %}`: **Condicionales**

### 2.4 Template para detalle - `dynamicpages/templates/dynamicpages/detalle_blogentry.html`
```html
<!-- dynamicpages/templates/dynamicpages/detalle_blogentry.html -->
{% extends 'dynamicpages/base.html' %}

{% block title %}{{ blogentry.titulo }}{% endblock %}

{% block content %}
<article>
    <h2>{{ blogentry.titulo }}</h2>
    <div class="meta">
        Por <strong>{{ blogentry.autor.username }}</strong> el 
        {{ blogentry.fecha_creacion|date:"d/m/Y H:i" }}
    </div>
    
    <div style="margin-top: 20px; line-height: 1.6;">
        {{ blogentry.contenido|linebreaks }}
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
    <a href="{% url 'lista_blogentries' %}">← Volver a la lista</a>
</div>
{% endblock %}
```

### 2.5 Crear vistas en `dynamicpages/views.py`
```python
# dynamicpages/views.py
from django.shortcuts import render
from .models import BlogEntry

def lista_blogentries(request):
    """Vista que consulta BD y pasa datos al template"""
    blogentries = BlogEntry.objects.filter(publicado=True).order_by('-fecha_creacion')
    
    # El contexto son los datos que se pasan al template
    contexto = {
        'blogentries': blogentries,
        'titulo_pagina': 'Mi Blog Django'
    }
    
    # render() combina el template con el contexto
    return render(request, 'dynamicpages/lista_blogentries.html', contexto)

def detalle_blogentry(request, blogentry_id):
    """Vista que muestra una entrada específica"""
    blogentry = BlogEntry.objects.get(id=blogentry_id, publicado=True)
    
    contexto = {
        'blogentry': blogentry
    }
    
    return render(request, 'dynamicpages/detalle_blogentry.html', contexto)
```

### 2.6 Configurar URLs - `dynamicpages/urls.py`
```python
# dynamicpages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_blogentries, name='lista_blogentries'),
    path('blogentry/<int:blogentry_id>/', views.detalle_blogentry, name='detalle_blogentry'),
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
blogentry = BlogEntry.objects.get(id=1)
return JsonResponse(blogentry)  # Error! No puede convertir objeto a JSON
```

**✅ Solución:** Los **Serializers** convierten entre modelos Django ↔ JSON

```
Modelo Django  ←→  Serializer  ←→  JSON
    BlogEntry  ←→  BlogEntrySerializer  ←→  {"id": 1, "titulo": "..."}
```

### 3.3 Crear serializer - `api/serializers.py`
```python
# api/serializers.py
from rest_framework import serializers
from dynamicpages.models import BlogEntry
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """Convierte el modelo User a JSON para incluir en autor"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class BlogEntrySerializer(serializers.ModelSerializer):
    """Convierte BlogEntry ↔ JSON automáticamente"""
    autor = UserSerializer(read_only=True)  # Incluye datos del autor
    
    class Meta:
        model = BlogEntry
        fields = ['id', 'titulo', 'contenido', 'autor', 'fecha_creacion', 'publicado']
```

**🔍 Explicación de Serializers:**

| **Operación** | **Código** | **Resultado** |
|---------------|------------|---------------|
| **Modelo → JSON** | `serializer.data` | `{"id": 1, "titulo": "Mi post"}` |
| **JSON → Modelo** | `serializer.save()` | Objeto BlogEntry en BD |
| **Validación** | `serializer.is_valid()` | `True/False` + errores |

**✨ Lo que hace automáticamente:**
- ✅ **Convierte tipos**: `DateTimeField` → string ISO
- ✅ **Relaciones**: `ForeignKey` → datos del objeto relacionado  
- ✅ **Validación**: Campos requeridos, tipos correctos
- ✅ **Bidireccional**: Modelo → JSON y JSON → Modelo

### 3.4 Crear vistas API - `api/views.py`
```python
# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from dynamicpages.models import BlogEntry
from .serializers import BlogEntrySerializer

@api_view(['GET'])
def lista_blogentries(request):
    """
    API manual - Solo lista todas las entradas
    GET /api/v1/blogentries/list/ → Lista todas las entradas en JSON
    """
    # Obtener todas las entradas publicadas
    blogentries = BlogEntry.objects.filter(publicado=True).order_by('-fecha_creacion')
    
    # Convertir a JSON usando el serializer
    serializer = BlogEntrySerializer(blogentries, many=True)
    
    # Devolver respuesta JSON
    return Response({
        'count': len(blogentries),
        'results': serializer.data
    })

@api_view(['POST'])
def crear_blogentry(request):
    """
    API manual - Solo crea una nueva entrada
    POST /api/v1/blogentries/create/ → Crear nueva entrada desde JSON
    """
    # Crear nueva entrada desde JSON
    serializer = BlogEntrySerializer(data=request.data)
    
    if serializer.is_valid():
        # Asignar usuario demo automáticamente
        from django.contrib.auth.models import User
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@example.com'}
        )
        serializer.save(autor=demo_user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def detalle_blogentry(request, pk):
    """
    API manual - Operaciones sobre una entrada específica
    GET /api/v1/blogentries/1/ → Detalle en JSON
    PUT /api/v1/blogentries/1/ → Actualizar entrada
    DELETE /api/v1/blogentries/1/ → Eliminar entrada
    """
    # Buscar la entrada o devolver 404
    blogentry = get_object_or_404(BlogEntry, pk=pk, publicado=True)
    
    if request.method == 'GET':
        # Devolver detalle en JSON
        serializer = BlogEntrySerializer(blogentry)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Actualizar entrada completa
        serializer = BlogEntrySerializer(blogentry, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Eliminar entrada
        blogentry.delete()
        return Response({'message': 'Entrada eliminada correctamente'}, 
                       status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def estadisticas_blog(request):
    """
    Endpoint personalizado - Estadísticas del blog
    GET /api/v1/stats/ → Estadísticas en JSON
    """
    from django.contrib.auth.models import User
    
    stats = {
        'total_entries': BlogEntry.objects.count(),
        'published_entries': BlogEntry.objects.filter(publicado=True).count(),
        'draft_entries': BlogEntry.objects.filter(publicado=False).count(),
        'total_authors': User.objects.count(),
        'latest_entry': None
    }
    
    # Agregar última entrada si existe
    latest = BlogEntry.objects.filter(publicado=True).order_by('-fecha_creacion').first()
    if latest:
        stats['latest_entry'] = {
            'id': latest.id,
            'titulo': latest.titulo,
            'autor': latest.autor.username,
            'fecha': latest.fecha_creacion
        }
    
    return Response(stats)
```

**🔍 Explicación del Enfoque Manual:**

1. **Una función por operación**: Cada endpoint hace una cosa específica
2. **`@api_view(['GET'])`**: Solo acepta GET para listar
3. **`@api_view(['POST'])`**: Solo acepta POST para crear
4. **URLs claras**: `/list/` para listar, `/create/` para crear
5. **Sin confusión**: No mezcla operaciones múltiples con individuales
6. **Serializer explícito**: Vemos cómo se convierten datos paso a paso
7. **Status codes explícitos**: Control total de respuestas HTTP

### 3.5 Configurar URLs API - `api/urls.py`
```python
# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs explícitas y educativas - cada acción tiene su propio endpoint
    path('blogentries/list/', views.lista_blogentries, name='api_lista_blogentries'),
    path('blogentries/create/', views.crear_blogentry, name='api_crear_blogentry'),
    path('blogentries/<int:pk>/', views.detalle_blogentry, name='api_detalle_blogentry'),
    path('stats/', views.estadisticas_blog, name='api_estadisticas'),
]
```

**🔍 Explicación de URLs explícitas:**
- **Acción clara en la URL**: `/list/` vs `/create/` - no hay confusión
- **Una función por endpoint**: Cada URL hace una cosa específica
- **Parámetros claros**: `<int:pk>` captura el ID como entero
- **Fácil de entender**: Se ve inmediatamente qué hace cada endpoint

### 3.6 Actualizar URLs principales - `mi_blog/urls.py`
```python
# mi_blog/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 📄 CONTENIDO ESTÁTICO (Ejercicio 1)
    path('static-pages/', include('staticpages.urls')),
    
    # 🎨 TEMPLATES DINÁMICOS
    path('dynamic-pages/', include('dynamicpages.urls')),
    
    # 🔌 API JSON
    path('api/v1/', include('api.urls')),
]
```

---

## 📋 Crear Datos de Prueba

### Comando personalizado - `dynamicpages/management/commands/crear_posts.py`
```bash
mkdir -p dynamicpages/management/commands
touch dynamicpages/management/__init__.py
touch dynamicpages/management/commands/__init__.py
```

```python
# dynamicpages/management/commands/crear_posts.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dynamicpages.models import BlogEntry

class Command(BaseCommand):
    help = 'Crea posts de ejemplo para el blog'

    def handle(self, *args, **options):
        # Crear usuario demo
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user('demo', 'demo@example.com', 'demo123')
            self.stdout.write('✅ Usuario demo creado: demo / demo123')
        
        autor = User.objects.get(username='demo')
        
        # Crear posts de ejemplo
        posts_ejemplo = [
            {
                'titulo': 'Mi primer post dinámico',
                'contenido': 'Este post viene de la base de datos y se renderiza con templates Django.'
            },
            {
                'titulo': 'Diferencias entre estático y dinámico',
                'contenido': 'Las páginas estáticas están fijas en el código. Las dinámicas se generan desde la BD.'
            },
            {
                'titulo': 'APIs REST en Django',
                'contenido': 'Django REST Framework permite crear APIs que devuelven JSON en lugar de HTML.'
            }
        ]
        
        for post_data in posts_ejemplo:
            BlogEntry.objects.get_or_create(
                titulo=post_data['titulo'],
                defaults={
                    'contenido': post_data['contenido'],
                    'autor': autor,
                    'publicado': True
                }
            )
        
        self.stdout.write('✅ Posts de ejemplo creados!')
```

### Ejecutar comando
```bash
python manage.py crear_posts
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

### 🎨 Templates Dinámicos 
- `http://127.0.0.1:8000/dynamic-pages/` → Lista desde BD
- `http://127.0.0.1:8000/dynamic-pages/blogentry/1/` → Detalle desde BD

### 🔌 API JSON
- `http://127.0.0.1:8000/api/v1/blogentries/list/` → Lista JSON
- `http://127.0.0.1:8000/api/v1/blogentries/create/` → Crear POST JSON
- `http://127.0.0.1:8000/api/v1/blogentries/1/` → Detalle JSON
- `http://127.0.0.1:8000/api/v1/stats/` → Estadísticas JSON

---

## 📊 Estructura Final

```
mi_blog/
├── staticpages/             # 📄 Contenido estático
├── dynamicpages/            # 🎨 Templates dinámicos
│   ├── models.py            # ✅ BlogEntry model
│   ├── views.py             # ✅ Vistas que consultan BD
│   ├── templates/dynamicpages/
│   │   ├── base.html        # ✅ Template base
│   │   ├── lista_*.html     # ✅ Lista de entradas
│   │   └── detalle_*.html   # ✅ Detalle de entrada
│   └── management/commands/
│       └── crear_posts.py   # ✅ Comando personalizado
├── api/                     # 🔌 API REST
│   ├── serializers.py       # ✅ JSON conversion
│   ├── views.py             # ✅ ViewSets
│   └── urls.py              # ✅ API routes
└── mi_blog/
    ├── settings.py          # ✅ Apps + DRF configuradas
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
lista_blogentries.html (contenido específico)
```

### ✅ API REST
- **@api_view**: Decorador para vistas API
- **request.method**: Manejo manual de GET/POST/PUT/DELETE
- **Serializers**: Conversión automática modelo ↔ JSON con validación
- **serializer.data**: Convierte modelo Django → JSON
- **serializer.save()**: Convierte JSON validado → modelo Django
- **Response()**: Construcción manual de respuestas JSON
- **Status codes**: Control explícito de códigos HTTP

### ✅ Comparación de Enfoques

| Tipo | URL | Datos | Uso |
|------|-----|-------|-----|
| **Estático** | `/static-pages/` | Fijos en código | Landing pages |
| **Dinámico** | `/dynamic-pages/` | Desde BD → HTML | Apps web |
| **API** | `/api/v1/` | Desde BD → JSON | Apps móviles |

---

## ➡️ Próximo Paso

En el **Ejercicio 3** agregaremos:
- 📝 **Formularios** para crear posts
- 🔐 **Autenticación** de usuarios
- 🎨 **Bootstrap** para mejor diseño

**¡Ahora entiendes la diferencia entre contenido estático, dinámico y APIs!** 🎉
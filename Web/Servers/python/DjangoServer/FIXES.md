# 🔧 Correcciones Aplicadas - DjangoWIP

## 🐛 Problema Original

Al acceder a los endpoints de la API (como `/api/furniture/123/`), se veía un **error de template**:

```
TemplateDoesNotExist at /api/furniture/123/
rest_framework/api.html
```

Y **no aparecía la interfaz HTML bonita** de Django REST Framework (como sí aparece en DjangoSimpleServer).

---

## ✅ Causa del Problema

El código **ya usaba** `@api_view` de Django REST Framework en las vistas, pero:
- ❌ **Django REST Framework NO estaba registrado** en `INSTALLED_APPS`
- ❌ Faltaba la configuración de `REST_FRAMEWORK`
- ❌ Las vistas usaban `JsonResponse` en lugar de `Response` de DRF

Por eso Django intentaba renderizar templates de DRF pero no los encontraba.

---

## 🛠️ Cambios Realizados

### 1. `furniture_app/settings.py`

**Agregado REST Framework a INSTALLED_APPS:**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # ✅ AGREGADO
    'furniture_api',   # ✅ CORREGIDO (antes era 'furniture_app')
]
```

**Agregada configuración de REST Framework:**
```python
# 🎨 CONFIGURACIÓN DE DJANGO REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # 🎨 Interfaz HTML bonita
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}
```

**Agregado context processor necesario:**
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',  # ✅ AGREGADO
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### 2. `furniture_api/views.py`

**Agregado import de Response de DRF:**
```python
from rest_framework.response import Response
from rest_framework import status
```

**Corregida función duplicada:**
```python
# ❌ ANTES: Dos funciones con el mismo nombre
@api_view(['POST'])
def post_furniture(request):
    # ...

@api_view(['PUT'])
def post_furniture(request):  # ❌ Nombre duplicado
    # ...

# ✅ DESPUÉS: Nombres únicos
@api_view(['POST'])
def post_furniture(request):
    # ...

@api_view(['PUT'])
def put_furniture(request, id):  # ✅ Nombre correcto
    # ...
```

**Cambiado JsonResponse por Response de DRF:**
```python
# ❌ ANTES:
return JsonResponse({"height": 20, "width": 30}, status=status.HTTP_200_OK)

# ✅ DESPUÉS:
return Response({"height": 20, "width": 30}, status=status.HTTP_200_OK)
```

**Agregados docstrings descriptivos:**
```python
@api_view(['GET'])
def get_furniture(request, id):
    """
    🪑 GET - Obtener un mueble por ID
    
    Ejemplo: GET /api/furniture/123/
    """
    # ...
```

### 3. `furniture_api/urls.py`

**Agregada ruta para PUT:**
```python
urlpatterns = [
    path('furniture/<str:id>/', views.get_furniture, name="get_furniture"),
    path('furniture/<str:id>/update/', views.put_furniture, name="put_furniture"),  # ✅ NUEVO
    path('furniture/', views.post_furniture, name="post_furniture"),
]
```

### 4. `requirements.txt` (NUEVO)

```txt
Django==5.2.8
djangorestframework==3.14.0
```

---

## 🎯 Resultado

### ❌ Antes
- Error de template `TemplateDoesNotExist`
- Sin interfaz HTML interactiva
- Funciones duplicadas con mismo nombre
- `JsonResponse` básico

### ✅ Después
- ✅ Interfaz HTML bonita (Browsable API de DRF)
- ✅ Formulario interactivo para POST/PUT
- ✅ JSON formateado con colores
- ✅ Documentación inline visible
- ✅ Todos los endpoints funcionando correctamente

---

## 🚀 Endpoints Funcionando

```bash
# GET - Obtener mueble
curl http://127.0.0.1:8000/api/furniture/123/
# {"id":"123","height":20,"width":30,"type":"chair","material":"wood"}

# POST - Crear mueble
curl -X POST http://127.0.0.1:8000/api/furniture/ \
  -H "Content-Type: application/json" \
  -d '{"height": 50, "width": 100, "type": "table"}'

# PUT - Actualizar mueble
curl -X PUT http://127.0.0.1:8000/api/furniture/123/update/ \
  -H "Content-Type: application/json" \
  -d '{"height": 60, "width": 120}'
```

---

## 📝 Nota sobre MongoDB

Si planeas usar **MongoDB** en lugar de SQLite:

❌ **NO necesitas migraciones** (`makemigrations` / `migrate`)  
✅ MongoDB es schema-less, las colecciones se crean automáticamente  
✅ Usa `mongoengine.Document` en lugar de `models.Model`

Las guías (readme-sesion-1.md y readme-sesion-2.md) están escritas para SQLite.

---

**¡Ahora tienes la misma interfaz HTML bonita que en DjangoSimpleServer!** 🎨


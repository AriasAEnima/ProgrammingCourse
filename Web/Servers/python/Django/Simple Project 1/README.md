# 🚀 Simple Project 1 - Django Multi-Endpoint Server

## 🎯 **Objetivo**
Crear un servidor Django que demuestre **3 tipos de endpoints diferentes:**
1. **🌐 HTTP Básico** - Respuestas simples y manejo de métodos HTTP
2. **🔌 API JSON** - CRUD completo con respuestas JSON
3. **📄 Templates HTML** - Páginas web dinámicas

---

## 📁 **Estructura de Proyecto Esperada**

```
Simple Project 1/
├── manage.py
├── mi_servidor/                    # Proyecto principal Django
│   ├── __init__.py
│   ├── settings.py                 # ← Configurar STATIC_URL aquí
│   ├── urls.py                     # ← URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── http_basic/                     # App 1: Endpoints básicos
│   ├── __init__.py
│   ├── apps.py
│   ├── views.py                    # ← Saludo, debug, imagen
│   └── urls.py
├── api/                            # App 2: API JSON
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                   # ← Tu modelo elegido
│   ├── serializers.py              # ← DRF serializers
│   ├── views.py                    # ← CRUD endpoints
│   └── urls.py
├── web/                            # App 3: Templates HTML
│   ├── __init__.py
│   ├── apps.py
│   ├── views.py                    # ← Vistas que renderizan HTML
│   ├── urls.py
│   └── templates/
│       └── web/
│           ├── detalle.html        # ← Template para mostrar item
│           └── 404.html            # ← Template error personalizado
└── static/                         # Archivos estáticos
    └── images/
        ├── django-logo.png         # ← Imágenes para servir
        ├── python-logo.png
        └── default.png
```

---

## 🛣️ **Endpoints a Implementar**

### 1. 🌐 **http_basic/** - Endpoints Básicos

#### `GET /http_basic/saludo/<str:nombre>/`
**✅ Comportamiento:**
- **Solo GET permitido** - otros verbos → `405 Method Not Allowed`
- **Response:** `<h1>¡Hola {nombre}!</h1>`
- **Content-Type:** `text/html`

#### `ANY /http_basic/debug/<path:cualquier_cosa>/`
**✅ Comportamiento:**
- **Todos los verbos permitidos** (GET, POST, PUT, DELETE, etc.)
- **Response JSON:**
```json
{
  "method": "POST",
  "path_param": "usuarios/123/perfil",
  "headers": {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0..."
  },
  "body": "contenido del body aquí",
  "query_params": {"filtro": "activo"}
}
```

#### `GET /http_basic/imagen/<str:nombre_imagen>/`
**✅ Comportamiento:**
- **Solo GET permitido**
- **Response:** Imagen PNG/JPG desde `static/images/`
- **Content-Type:** `image/png` o `image/jpeg`

**🔍 Pista de implementación:**
```python
# views.py
from django.http import FileResponse, Http404
from django.conf import settings
import os

def servir_imagen(request, nombre_imagen):
    if request.method != 'GET':
        return HttpResponse(status=405)
    
    # Construir ruta de la imagen
    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', f'{nombre_imagen}.png')
    
    try:
        # ✨ CLAVE: FileResponse para archivos
        return FileResponse(open(ruta_imagen, 'rb'), content_type='image/png')
    except FileNotFoundError:
        raise Http404("Imagen no encontrada")
```

---

### 2. 🔌 **api/[tema]/** - CRUD JSON API

**🎯 Elige UNO de estos temas:**

| Tema | Endpoint Base | Modelo |
|------|---------------|--------|
| **📚 Libros** | `/api/libros/` | titulo, autor, año_publicacion, genero, num_paginas, isbn, precio, disponible |
| **💻 Laptops** | `/api/laptops/` | marca, modelo, procesador, ram_gb, almacenamiento_gb, tipo_disco, precio, año |
| **🎬 Películas** | `/api/peliculas/` | titulo, director, año, genero, duracion_min, calificacion, idioma_original |
| **🍕 Restaurantes** | `/api/restaurantes/` | nombre, tipo_cocina, direccion, telefono, calificacion, precio_promedio, delivery |
| **🌱 Plantas** | `/api/plantas/` | nombre, especie, tipo_planta, altura_cm, cuidados, interior_exterior, precio |

#### `GET /api/libros/` - Listar todos
**✅ Response esperado:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "titulo": "1984",
      "autor": "George Orwell",
      "año_publicacion": 1949,
      "genero": "Distopía",
      "num_paginas": 328,
      "isbn": "978-0-452-28423-4",
      "precio": 15.99,
      "disponible": true
    }
  ]
}
```

#### `POST /api/libros/` - Crear nuevo
**✅ Request esperado:**
```json
{
  "titulo": "El Quijote",
  "autor": "Cervantes",
  "año_publicacion": 1605,
  "genero": "Clásico",
  "num_paginas": 863,
  "isbn": "978-84-376-0494-7",
  "precio": 22.50,
  "disponible": true
}
```

**✅ Response éxito:** `201 Created` + objeto creado con `id`

**❌ Response error:** `400 Bad Request` + detalles de validación

#### `GET /api/libros/<int:id>/` - Ver específico
**✅ Response éxito:** `200 OK` + objeto JSON
**❌ Response error:** `404 Not Found`

#### `DELETE /api/libros/<int:id>/` - Eliminar
**✅ Response éxito:** `204 No Content` o `200 OK` + mensaje
**❌ Response error:** `404 Not Found`

---

### 3. 📄 **web/[tema]/** - Templates HTML

#### `GET /web/libros/<int:id>/` - Detalle HTML
**✅ Template esperado:**
- Título del libro como `<h1>`
- Autor, año, género en formato legible
- Precio formateado (`$15.99`)
- Estado disponibilidad (`✅ Disponible` / `❌ No disponible`)
- **CSS básico** para que se vea bien
- **Link de regreso** a API: `/api/libros/`

**❌ Error:** Template 404 personalizado + `404 Not Found`

---

## ⚙️ **Configuración Requerida**

### **settings.py**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',        # ← Para API JSON
    'http_basic',           # ← Tu app básica
    'api',                  # ← Tu app API
    'web',                  # ← Tu app web
]

# Para servir archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

### **urls.py principal**
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('http_basic/', include('http_basic.urls')),
    path('api/', include('api.urls')),
    path('web/', include('web.urls')),
]

# Solo en desarrollo para servir archivos estáticos
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
```

---

## 🧪 **Testing Esperado**

### **HTTP Básico:**
```bash
# ✅ Debe funcionar
curl http://127.0.0.1:8000/http_basic/saludo/Eduardo/
curl -X POST http://127.0.0.1:8000/http_basic/debug/cualquier/cosa/
curl -I http://127.0.0.1:8000/http_basic/imagen/django-logo/

# ❌ Debe fallar con 405
curl -X POST http://127.0.0.1:8000/http_basic/saludo/Eduardo/
```

### **API JSON:**
```bash
# ✅ CRUD completo
curl http://127.0.0.1:8000/api/libros/                     # GET todos
curl -X POST http://127.0.0.1:8000/api/libros/ -d {...}    # POST crear
curl http://127.0.0.1:8000/api/libros/1/                   # GET uno
curl -X DELETE http://127.0.0.1:8000/api/libros/1/         # DELETE
```

### **Web HTML:**
```bash
# ✅ En navegador
http://127.0.0.1:8000/web/libros/1/                        # Ver HTML
```

---

## 🚀 **Pasos de Implementación Sugeridos**

1. **🏗️ Crear proyecto:** `django-admin startproject mi_servidor`
2. **📦 Crear apps:** `python manage.py startapp http_basic api web`
3. **🔧 Configurar:** settings.py + urls.py principales
4. **🌐 HTTP básico:** Empezar con endpoints simples
5. **🔌 API JSON:** Modelo + serializers + CRUD
6. **📄 Templates:** HTML dinámico para mostrar datos
7. **🧪 Testing:** Probar todos los endpoints

**🎯 ¡Demuestra dominio completo de Django con diferentes tipos de respuestas!**

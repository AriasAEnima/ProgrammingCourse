# 🚀 Ejercicio 3: Django Web - Formularios y Autenticación

**Tiempo estimado:** 30 minutos  
**Nivel:** Intermedio  
**Objetivo:** Agregar **interactividad** al blog: crear posts y autenticación

---

## 🎯 Lo que Vamos a Agregar

- ✅ **Formularios** para crear posts
- ✅ **Autenticación** básica (login/logout)
- ✅ **Templates** con Bootstrap
- ✅ **Navegación** dinámica

**Flujo completo:** Usuario se registra → Inicia sesión → Crea posts → Ve sus posts

---

## 📋 Prerrequisitos

- ✅ Ejercicio 1 y 2 completados
- ✅ Blog funcionando en `http://127.0.0.1:8000/`

---

## 📋 Parte 1: Formularios (15 minutos)

### 1.1 Crear `blog/forms.py`
```python
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'contenido', 'publicado']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del post'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Contenido del post...'
            }),
            'publicado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'titulo': 'Título',
            'contenido': 'Contenido',
            'publicado': 'Publicar inmediatamente'
        }
```

### 1.2 Agregar vista para crear posts en `blog/views.py`
```python
# Agregar estos imports al inicio
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PostForm

# Agregar esta vista al final del archivo
@login_required
def crear_post(request):
    """Vista para crear un nuevo post"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user  # Asignar usuario actual
            post.save()
            messages.success(request, f'Post "{post.titulo}" creado exitosamente!')
            return redirect('lista_posts')
    else:
        form = PostForm()
    
    contexto = {
        'form': form,
        'titulo_pagina': 'Crear Nuevo Post'
    }
    return render(request, 'blog/crear_post.html', contexto)
```

### 1.3 Template para crear post `blog/templates/blog/crear_post.html`
```html
{% extends 'blog/base.html' %}

{% block title %}{{ titulo_pagina }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <h2>✍️ Crear Nuevo Post</h2>
        
        <form method="post" class="mt-4">
            {% csrf_token %}
            
            <div class="mb-3">
                <label for="{{ form.titulo.id_for_label }}" class="form-label">
                    {{ form.titulo.label }}
                </label>
                {{ form.titulo }}
                {% if form.titulo.errors %}
                    <div class="text-danger">{{ form.titulo.errors }}</div>
                {% endif %}
            </div>
            
            <div class="mb-3">
                <label for="{{ form.contenido.id_for_label }}" class="form-label">
                    {{ form.contenido.label }}
                </label>
                {{ form.contenido }}
                {% if form.contenido.errors %}
                    <div class="text-danger">{{ form.contenido.errors }}</div>
                {% endif %}
            </div>
            
            <div class="mb-3 form-check">
                {{ form.publicado }}
                <label class="form-check-label" for="{{ form.publicado.id_for_label }}">
                    {{ form.publicado.label }}
                </label>
            </div>
            
            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <a href="{% url 'lista_posts' %}" class="btn btn-secondary me-md-2">
                    Cancelar
                </a>
                <button type="submit" class="btn btn-primary">
                    📝 Crear Post
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

### 1.4 Agregar URL en `blog/urls.py`
```python
urlpatterns = [
    path('', views.lista_posts, name='lista_posts'),
    path('post/<int:post_id>/', views.detalle_post, name='detalle_post'),
    path('crear/', views.crear_post, name='crear_post'),  # ← Nueva URL
]
```

---

## 📋 Parte 2: Autenticación (15 minutos)

### 2.1 Vistas de autenticación en `blog/views.py`
```python
# Agregar estos imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

# Agregar estas vistas
def vista_login(request):
    """Vista para iniciar sesión"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('lista_posts')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'registration/login.html')

def vista_logout(request):
    """Vista para cerrar sesión"""
    username = request.user.username
    logout(request)
    messages.info(request, f'Hasta luego, {username}!')
    return redirect('lista_posts')

def vista_registro(request):
    """Vista para registrar nuevos usuarios"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Cuenta creada para {user.username}. ¡Ya puedes iniciar sesión!')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    contexto = {'form': form}
    return render(request, 'registration/registro.html', contexto)
```

### 2.2 URLs de autenticación en `blog/urls.py`
```python
urlpatterns = [
    path('', views.lista_posts, name='lista_posts'),
    path('post/<int:post_id>/', views.detalle_post, name='detalle_post'),
    path('crear/', views.crear_post, name='crear_post'),
    # URLs de autenticación
    path('login/', views.vista_login, name='login'),
    path('logout/', views.vista_logout, name='logout'),
    path('registro/', views.vista_registro, name='registro'),
]
```

### 2.3 Configurar redirecciones en `settings.py`
```python
# Agregar al final de mi_blog/settings.py
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
```

---

## 📋 Parte 3: Templates Mejorados (15 minutos)

### 3.1 Template base mejorado `blog/templates/blog/base.html`
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Mi Blog Django{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'lista_posts' %}">
                🐍 Mi Blog Django
            </a>
            
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <span class="navbar-text me-3">
                        Hola, <strong>{{ user.username }}</strong>!
                    </span>
                    <a class="nav-link" href="{% url 'crear_post' %}">
                        ✍️ Nuevo Post
                    </a>
                    <a class="nav-link" href="{% url 'logout' %}">
                        🚪 Salir
                    </a>
                {% else %}
                    <a class="nav-link" href="{% url 'login' %}">
                        🔑 Iniciar Sesión
                    </a>
                    <a class="nav-link" href="{% url 'registro' %}">
                        👤 Registrarse
                    </a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <!-- Mensajes -->
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
    
    <!-- Contenido -->
    <div class="container mt-4">
        {% block content %}
        {% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### 3.2 Lista mejorada `blog/templates/blog/lista_posts.html`
```html
{% extends 'blog/base.html' %}

{% block title %}{{ titulo_pagina }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>📝 Posts Recientes</h2>
            {% if user.is_authenticated %}
                <a href="{% url 'crear_post' %}" class="btn btn-primary">
                    ✍️ Nuevo Post
                </a>
            {% endif %}
        </div>

        {% for post in posts %}
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">
                        <a href="{% url 'detalle_post' post.id %}" class="text-decoration-none">
                            {{ post.titulo }}
                        </a>
                    </h5>
                    <p class="card-text">{{ post.contenido|truncatewords:25 }}</p>
                    <small class="text-muted">
                        Por <strong>{{ post.autor.username }}</strong> 
                        el {{ post.fecha_creacion|date:"d/m/Y H:i" }}
                    </small>
                </div>
            </div>
        {% empty %}
            <div class="text-center py-5">
                <h4 class="text-muted">No hay posts aún</h4>
                {% if user.is_authenticated %}
                    <a href="{% url 'crear_post' %}" class="btn btn-primary mt-3">
                        ✍️ Crear el primer post
                    </a>
                {% else %}
                    <p class="text-muted">
                        <a href="{% url 'registro' %}">Regístrate</a> para crear posts
                    </p>
                {% endif %}
            </div>
        {% endfor %}
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h6>📊 Estadísticas</h6>
            </div>
            <div class="card-body">
                <p>Total de posts: <strong>{{ posts|length }}</strong></p>
                {% if user.is_authenticated %}
                    <p>Tus posts: <strong>{{ posts|length }}</strong></p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 3.3 Template de login `blog/templates/registration/login.html`
```html
{% extends 'blog/base.html' %}

{% block title %}Iniciar Sesión{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h4 class="mb-0">🔑 Iniciar Sesión</h4>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="username" class="form-label">Usuario</label>
                        <input type="text" class="form-control" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Contraseña</label>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary">
                            🔑 Iniciar Sesión
                        </button>
                    </div>
                </form>
                
                <div class="text-center mt-3">
                    <p class="mb-0">
                        ¿No tienes cuenta? 
                        <a href="{% url 'registro' %}">Regístrate aquí</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 3.4 Template de registro `blog/templates/registration/registro.html`
```html
{% extends 'blog/base.html' %}

{% block title %}Registrarse{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h4 class="mb-0">👤 Crear Cuenta</h4>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="mb-3">
                        <label for="{{ form.username.id_for_label }}" class="form-label">
                            Usuario
                        </label>
                        {{ form.username }}
                        {% if form.username.errors %}
                            <div class="text-danger">{{ form.username.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.password1.id_for_label }}" class="form-label">
                            Contraseña
                        </label>
                        {{ form.password1 }}
                        {% if form.password1.errors %}
                            <div class="text-danger">{{ form.password1.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.password2.id_for_label }}" class="form-label">
                            Confirmar Contraseña
                        </label>
                        {{ form.password2 }}
                        {% if form.password2.errors %}
                            <div class="text-danger">{{ form.password2.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="d-grid">
                        <button type="submit" class="btn btn-success">
                            👤 Crear Cuenta
                        </button>
                    </div>
                </form>
                
                <div class="text-center mt-3">
                    <p class="mb-0">
                        ¿Ya tienes cuenta? 
                        <a href="{% url 'login' %}">Inicia sesión aquí</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## ✅ Verificación Final

### Prueba el blog completo:
```bash
python manage.py runserver
```

### Flujo de prueba:
1. ✅ **Ir a `http://127.0.0.1:8000/`** → Ver posts existentes
2. ✅ **Hacer clic en "Registrarse"** → Crear cuenta nueva
3. ✅ **Iniciar sesión** con la cuenta creada
4. ✅ **Hacer clic en "Nuevo Post"** → Crear post
5. ✅ **Ver el post** en la lista principal
6. ✅ **Cerrar sesión** → Verificar que el navbar cambia

### Debe funcionar:
- ✅ Navegación dinámica (cambia si estás autenticado)
- ✅ Mensajes de feedback (éxito, error, info)
- ✅ Crear posts (solo usuarios autenticados)
- ✅ Registro e inicio de sesión
- ✅ Diseño responsive con Bootstrap

---

## 🎓 Lo que Aprendiste

### Django Formularios:
- ✅ **ModelForm:** Genera formularios automáticamente desde modelos
- ✅ **Widgets:** Personalizar campos HTML
- ✅ **Validación:** Django valida datos automáticamente
- ✅ **CSRF:** Protección contra ataques cross-site

### Django Autenticación:
- ✅ **User model:** Sistema de usuarios integrado
- ✅ **Login/Logout:** Funciones built-in de Django
- ✅ **@login_required:** Proteger vistas
- ✅ **UserCreationForm:** Registro automático

### Django Templates:
- ✅ **Template inheritance:** Evitar repetición de código
- ✅ **Context variables:** Datos dinámicos
- ✅ **Template tags:** {% if user.is_authenticated %}
- ✅ **Messages framework:** Feedback al usuario

**¡Tienes un blog completamente funcional! 🎉 Con autenticación, formularios y diseño profesional.**

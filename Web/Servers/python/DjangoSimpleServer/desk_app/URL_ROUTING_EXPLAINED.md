# 🛣️ Cómo Funciona el URL Routing en Django

## 🤔 Tu Pregunta

```python
path('<str:desk_id>', views.get_desk_by_id, name='api_get_desk'),
path('<str:desk_id>', views.update_desk, name='api_update_desk'),
path('<str:desk_id>', views.delete_desk, name='api_delete_desk'),
```

**"¿Cómo es que esto funciona si es el mismo path?"**

## ❌ La Respuesta Corta: NO FUNCIONA

Django **NO diferencia por método HTTP** en el URL routing. Solo busca por **patrón de URL**.

### Qué Pasa Realmente

```python
# Django procesa las URLs en orden:

1. Request: GET /api/desk/123
   → Encuentra el primer path('<str:desk_id>')
   → Llama a views.get_desk_by_id ✅
   → Los demás paths NUNCA se evalúan

2. Request: PUT /api/desk/123
   → Encuentra el primer path('<str:desk_id>')
   → Llama a views.get_desk_by_id ❌
   → get_desk_by_id solo acepta GET
   → Retorna: 405 Method Not Allowed
   → views.update_desk NUNCA se ejecuta

3. Request: DELETE /api/desk/123
   → Encuentra el primer path('<str:desk_id>')
   → Llama a views.get_desk_by_id ❌
   → Retorna: 405 Method Not Allowed
   → views.delete_desk NUNCA se ejecuta
```

## 🔍 Proceso de URL Matching en Django

Django sigue este proceso:

```python
# urls.py
urlpatterns = [
    path('desk/', views.desk_list),
    path('desk/<str:desk_id>', views.desk_detail),
    path('desk/<str:desk_id>', views.another_view),  # ❌ Nunca se alcanza
]

# Cuando llega una request:
1. Django recorre urlpatterns en orden (de arriba a abajo)
2. Compara el patrón de URL con cada path
3. En el PRIMER match, llama a la vista
4. Las demás paths con el mismo patrón se IGNORAN
```

### Ejemplo Visual

```
Request: GET /api/desk/123

Django:
  ✓ ¿Coincide con 'desk/'? NO
  ✓ ¿Coincide con 'desk/<str:desk_id>'? SÍ ✓
    → Llama a views.desk_detail
    → DETIENE la búsqueda
    
  ✗ Nunca evalúa los siguientes paths
```

## ✅ Soluciones

### Solución 1: Una Vista por Path (Recomendado)

Una vista maneja múltiples métodos HTTP:

```python
# urls.py
urlpatterns = [
    path('', views.desk_list, name='desk_list'),           # GET, POST
    path('<str:desk_id>', views.desk_detail, name='desk_detail'),  # GET, PUT, PATCH, DELETE
]

# views.py
@api_view(['GET', 'POST'])
def desk_list(request):
    if request.method == 'GET':
        # Listar todas las mesas
        return Response(...)
    elif request.method == 'POST':
        # Crear nueva mesa
        return Response(...)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def desk_detail(request, desk_id):
    if request.method == 'GET':
        # Obtener una mesa
        return Response(...)
    elif request.method in ['PUT', 'PATCH']:
        # Actualizar mesa
        return Response(...)
    elif request.method == 'DELETE':
        # Eliminar mesa
        return Response(...)
```

**Ventajas:**
- ✅ Funciona correctamente
- ✅ RESTful (un recurso = un path)
- ✅ Menos URLs
- ✅ Estándar de Django

**Desventajas:**
- ⚠️ Funciones más largas (pero organizadas con if/elif)

### Solución 2: URLs Diferentes para Cada Acción

Usar paths diferentes para cada operación:

```python
# urls.py
urlpatterns = [
    path('', views.list_desks, name='list'),                    # GET
    path('create', views.create_desk, name='create'),           # POST
    path('<str:desk_id>', views.get_desk, name='get'),          # GET
    path('<str:desk_id>/update', views.update_desk, name='update'),  # PUT
    path('<str:desk_id>/delete', views.delete_desk, name='delete'),  # DELETE
]

# views.py
@api_view(['GET'])
def list_desks(request):
    return Response(...)

@api_view(['POST'])
def create_desk(request):
    return Response(...)

@api_view(['GET'])
def get_desk(request, desk_id):
    return Response(...)

@api_view(['PUT', 'PATCH'])
def update_desk(request, desk_id):
    return Response(...)

@api_view(['DELETE'])
def delete_desk(request, desk_id):
    return Response(...)
```

**Ventajas:**
- ✅ Funciones pequeñas y separadas
- ✅ Cada función hace una cosa

**Desventajas:**
- ❌ NO es RESTful estándar
- ❌ Más URLs
- ❌ URLs menos limpias (`/desk/123/update` vs `/desk/123`)

### Solución 3: ViewSets (Django REST Framework)

Usa ViewSets que manejan automáticamente el routing:

```python
# views.py
from rest_framework import viewsets

class DeskViewSet(viewsets.ModelViewSet):
    queryset = Desk.objects.all()
    serializer_class = DeskSerializer

# urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('desk', views.DeskViewSet)

urlpatterns = router.urls
```

**Esto crea automáticamente:**
```
GET    /desk/          → list()
POST   /desk/          → create()
GET    /desk/{id}/     → retrieve()
PUT    /desk/{id}/     → update()
PATCH  /desk/{id}/     → partial_update()
DELETE /desk/{id}/     → destroy()
```

**Ventajas:**
- ✅ Menos código
- ✅ Totalmente RESTful
- ✅ Automático

**Desventajas:**
- ⚠️ Menos control granular
- ⚠️ Requiere aprender ViewSets

## 📊 Comparación de Soluciones

| Característica | Una Vista/Path | URLs Diferentes | ViewSets |
|----------------|----------------|-----------------|----------|
| RESTful | ✅ | ❌ | ✅ |
| Código limpio | ✅ | ⚠️ | ✅ |
| Fácil de entender | ✅ | ✅ | ⚠️ |
| URLs limpias | ✅ | ❌ | ✅ |
| Control granular | ✅ | ✅ | ⚠️ |
| **Recomendado** | **SÍ** | No | Para APIs grandes |

## 🎯 Nuestra Implementación (Solución 1)

```python
# urls.py - Solo 2 paths
urlpatterns = [
    path('', views.desk_list, name='desk_list'),
    path('<str:desk_id>', views.desk_detail, name='desk_detail'),
]
```

```python
# views.py - 2 funciones principales

@api_view(['GET', 'POST'])
def desk_list(request):
    """Maneja la colección de mesas"""
    if request.method == 'GET':
        # GET /api/desk/ → Listar todas
        ...
    elif request.method == 'POST':
        # POST /api/desk/ → Crear nueva
        ...

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def desk_detail(request, desk_id):
    """Maneja una mesa individual"""
    if request.method == 'GET':
        # GET /api/desk/123 → Obtener
        ...
    elif request.method in ['PUT', 'PATCH']:
        # PUT/PATCH /api/desk/123 → Actualizar
        ...
    elif request.method == 'DELETE':
        # DELETE /api/desk/123 → Eliminar
        ...
```

## 🧪 Prueba Práctica

### Configuración INCORRECTA (No funciona)

```python
urlpatterns = [
    path('<str:id>', get_view),     # Solo acepta GET
    path('<str:id>', post_view),    # ❌ Nunca se ejecuta
    path('<str:id>', delete_view),  # ❌ Nunca se ejecuta
]
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/desk/123
# Resultado: 405 Method Not Allowed
# Porque llama a get_view que solo acepta GET
```

### Configuración CORRECTA (Funciona)

```python
urlpatterns = [
    path('<str:id>', detail_view),  # Acepta GET, POST, PUT, DELETE
]

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def detail_view(request, id):
    if request.method == 'POST':
        # Maneja POST
        ...
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/desk/123
# Resultado: 200 OK
# Porque detail_view acepta POST y lo maneja
```

## 💡 Regla de Oro

```
🚫 NO: Múltiples paths con el mismo patrón
✅ SÍ: Un path, una vista que maneja múltiples métodos HTTP
```

## 🔗 Recursos Adicionales

- [Django URL dispatcher](https://docs.djangoproject.com/en/stable/topics/http/urls/)
- [DRF ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [RESTful API Design](https://restfulapi.net/)

## 📝 Resumen

1. **Django URL routing NO diferencia por método HTTP**
2. **Solo importa el patrón de la URL**
3. **Usa el primer path que coincida**
4. **Una vista puede manejar múltiples métodos HTTP**
5. **Usa `@api_view(['GET', 'POST', ...])` para especificar métodos**
6. **Dentro de la vista, usa `if request.method == 'GET':`**

✅ **Resultado:** APIs RESTful limpias y funcionales


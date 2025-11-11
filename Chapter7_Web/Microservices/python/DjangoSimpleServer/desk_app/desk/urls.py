from django.urls import path
from . import views

"""
URLs RESTful para el API de mesas:

⚠️ IMPORTANTE: Django NO diferencia por método HTTP en el routing.
   Solo importa el PATRÓN de la URL.
   Por eso usamos SOLO 2 paths, y cada vista maneja múltiples métodos HTTP.

Funcionamiento:
1. Django recibe una request (ej: GET /api/desk/123)
2. Compara con los patterns en orden
3. Encuentra el primer match (ej: '<str:desk_id>')
4. Llama a esa vista (ej: views.desk_detail)
5. La vista mira request.method y delega a la función correcta

GET    /api/desk/        → desk_list()   → _handle_list_desks()
POST   /api/desk/        → desk_list()   → _handle_create_desk()
GET    /api/desk/<id>    → desk_detail() → _handle_get_desk()
PUT    /api/desk/<id>    → desk_detail() → _handle_update_desk()
PATCH  /api/desk/<id>    → desk_detail() → _handle_update_desk()
DELETE /api/desk/<id>    → desk_detail() → _handle_delete_desk()
"""

urlpatterns = [
    # Colección: /api/desk/
    # desk_list maneja GET (listar) y POST (crear)
    path('', views.desk_list, name='desk_list'),
    
    # Recurso individual: /api/desk/<id>
    # desk_detail maneja GET, PUT, PATCH y DELETE
    path('<str:desk_id>', views.desk_detail, name='desk_detail'),
]
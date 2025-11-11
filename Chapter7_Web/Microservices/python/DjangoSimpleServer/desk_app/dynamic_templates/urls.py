from django.urls import path
from . import views

urlpatterns = [
    path('desk/<str:desk_id>/', views.get_desk, name='template_get_desk'),
    path('', views.get_desks , name='template_get_all_desks')
]
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

def lista_muebles_v2(request):
    """Vista que consulta MongoDB y muestra muebles"""
    muebles = FurnitureItem.objects.filter(publicado=True).order_by('-fecha_creacion')
    
    contexto = {
        'muebles': muebles,
        'titulo_pagina': 'Catálogo de Muebles'
    }
    
    return render(request, 'dynamicpages/new_list_version.html', contexto)

def detalle_mueble(request, id):
    """Vista que muestra un mueble específico"""
    mueble = FurnitureItem.objects.get(id=id, publicado=True)
    
    contexto = {
        'mueble': mueble
    }
    
    return render(request, 'dynamicpages/detalle_mueble.html', contexto)

def crear_mueble(request):
    """Vista para crear un nuevo mueble en MongoDB (sin autenticación)"""
    print(f"Method: {request.method}")
    if request.method == 'POST':
        mueble = FurnitureItem(
            nombre=request.POST['nombre'],
            descripcion=request.POST['descripcion'],
            altura=int(request.POST['altura']),
            ancho=int(request.POST['ancho']),
            material=request.POST['material'],
            autor_username=request.POST.get('autor', 'Anónimo'),  # Sin auth
            publicado=True
        )
        mueble.save()
        
        messages.success(request, f'Mueble "{mueble.nombre}" agregado exitosamente!')
        return redirect('lista_muebles')
    else:
        return render(request, 'dynamicpages/crear_mueble.html')

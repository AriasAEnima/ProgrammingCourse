
from django.shortcuts import render
from django.contrib.auth.models import User
# Create your views here.
from django.shortcuts import render
from .models import BlogEntry

def lista_blogentries(request):
    """Vista que muestra todas las entradas del blog publicadas"""
    blogentries = BlogEntry.objects.filter(publicado=True).order_by('-fecha_creacion')
    
    contexto = {
        'blogentries': blogentries,
        'titulo_pagina': 'Mi Blog Django'
    }
    
    return render(request, 'dynamicpages/lista_blogentries.html', contexto)

def detalle_blogentry(request, blogentry_id):
    """Vista que muestra una entrada específica del blog"""
    blogentry = BlogEntry.objects.get(id=blogentry_id, publicado=True)
    
    contexto = {
        'blogentry': blogentry
    }
    
    return render(request, 'dynamicpages/detalle_blogentry.html', contexto)
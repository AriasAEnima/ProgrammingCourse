#!/usr/bin/env python
"""
Script para poblar la base de datos MongoDB con datos de ejemplo
Uso: python seed_db.py
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desk_app.settings')
django.setup()

from desk.models import Desk

def seed_database():
    """
    Puebla la base de datos con mesas de ejemplo
    """
    # Limpiar la colección existente (opcional)
    print("🗑️  Limpiando colección existente...")
    count = Desk.objects.count()
    if count > 0:
        response = input(f"Se encontraron {count} mesas. ¿Desea eliminarlas? (s/n): ")
        if response.lower() == 's':
            Desk.objects.delete()
            print(f"✅ Se eliminaron {count} mesas")
        else:
            print("⏭️  Conservando mesas existentes")
    
    # Datos de ejemplo
    desks_data = [
        {"name": "Mesa Venture", "width": 125, "height": 225},
        {"name": "Mesa Koto", "width": 200, "height": 223},
        {"name": "Mesa Amatista", "width": 200, "height": 300},
        {"name": "Mesa Ejecutiva", "width": 180, "height": 90},
        {"name": "Mesa Redonda", "width": 150, "height": 150},
    ]
    
    print("\n📝 Creando mesas...")
    
    for desk_data in desks_data:
        try:
            desk = Desk(**desk_data)
            desk.save()
            print(f"✅ Mesa creada: {desk.name} (ID: {desk.id})")
        except Exception as e:
            print(f"❌ Error al crear mesa {desk_data['name']}: {str(e)}")
    
    # Mostrar resumen
    print(f"\n🎉 Proceso completado. Total de mesas en la base de datos: {Desk.objects.count()}")
    
    # Mostrar todas las mesas
    print("\n📋 Mesas en la base de datos:")
    for desk in Desk.objects.all():
        print(f"  - {desk.name}: {desk.width}cm x {desk.height}cm (ID: {desk.id})")

if __name__ == "__main__":
    print("=" * 60)
    print("🌱 Script de Población de Base de Datos - Mesas")
    print("=" * 60)
    
    try:
        seed_database()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


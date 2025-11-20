#!/usr/bin/env python3
"""
Ejemplo básico de procesamiento de imágenes.

Este script demuestra cómo:
1. Cargar una imagen desde disco
2. Aplicar un filtro simple
3. Guardar el resultado

Es el ejemplo más simple para entender el flujo básico.
"""

import os
from PIL import Image
from filters import BlurFilter


def main():
    """
    Función principal que ejecuta el procesamiento básico.
    """
    print("📸 Procesador Simple de Imágenes")
    print("=" * 60)
    
    # 1. Definir rutas
    # Usamos rutas relativas para que el código sea portable
    input_path = "images/sample_4k.jpg"
    output_path = "output/blurred_sample.jpg"
    
    # 2. Verificar que la imagen existe
    if not os.path.exists(input_path):
        print(f"❌ Error: No se encontró la imagen en '{input_path}'")
        print("\n💡 Solución:")
        print("   1. Crea la carpeta 'images/'")
        print("   2. Coloca una imagen llamada 'sample.jpg' en ella")
        print("   3. O usa cualquier imagen JPG/PNG que tengas")
        return
    
    print(f"\n1️⃣  Cargando imagen desde: {input_path}")
    
    # 3. Cargar la imagen usando PIL
    # Image.open() devuelve un objeto Image que podemos manipular
    try:
        image = Image.open(input_path)
        print(f"   ✅ Imagen cargada exitosamente")
        print(f"   📏 Tamaño: {image.size[0]}x{image.size[1]} píxeles")
        print(f"   🎨 Modo: {image.mode}")  # RGB, RGBA, L (grayscale), etc.
    except Exception as e:
        print(f"   ❌ Error al cargar imagen: {e}")
        return
    
    # 4. Crear el filtro
    print(f"\n2️⃣  Creando filtro de desenfoque...")
    blur_filter = BlurFilter(radius=5)
    print(f"   ✅ Filtro creado: {blur_filter}")
    
    # 5. Aplicar el filtro
    print(f"\n3️⃣  Aplicando filtro a la imagen...")
    try:
        # El método apply() devuelve una NUEVA imagen
        # La imagen original NO se modifica (inmutabilidad)
        result = blur_filter.apply(image)
        print(f"   ✅ Filtro aplicado exitosamente")
    except Exception as e:
        print(f"   ❌ Error al aplicar filtro: {e}")
        return
    
    # 6. Crear directorio de salida si no existe
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\n   📁 Directorio '{output_dir}/' creado")
    
    # 7. Guardar la imagen procesada
    print(f"\n4️⃣  Guardando resultado en: {output_path}")
    try:
        result.save(output_path, quality=95)
        print(f"   ✅ Imagen guardada exitosamente")
    except Exception as e:
        print(f"   ❌ Error al guardar imagen: {e}")
        return
    
    # 8. Resumen final
    print("\n" + "=" * 60)
    print("✨ Procesamiento completado con éxito!")
    print(f"📂 Revisa el resultado en: {output_path}")
    print("=" * 60)


# Información adicional sobre el flujo
def show_flow_diagram():
    """
    Muestra un diagrama del flujo de procesamiento.
    """
    print("\n🔄 Flujo de Procesamiento:")
    print("""
    ┌─────────────────┐
    │ Imagen Original │
    │  (sample.jpg)   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Aplicar Filtro │
    │   (BlurFilter)  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Imagen Procesada│
    │ (blurred_...)   │
    └─────────────────┘
    """)


if __name__ == "__main__":
    # Mostrar diagrama de flujo
    show_flow_diagram()
    
    # Ejecutar procesamiento
    main()
    
    # Consejos adicionales
    print("\n💡 Próximos pasos:")
    print("   1. Prueba con diferentes valores de 'radius' (1-10)")
    print("   2. Cambia BlurFilter por BrightnessFilter")
    print("   3. Experimenta con tus propias imágenes")
    print("   4. Ejecuta 'demo_all_filters.py' para ver todos los filtros")


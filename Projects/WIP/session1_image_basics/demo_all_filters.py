#!/usr/bin/env python3
"""
Demo de todos los filtros disponibles.

Este script:
1. Carga una imagen de prueba
2. Aplica cada filtro disponible
3. Guarda múltiples versiones en la carpeta output/
4. Muestra un resumen de los resultados

Es útil para:
- Ver todos los filtros en acción
- Comparar resultados
- Entender el efecto de cada filtro
"""

import os
import time
from PIL import Image
from filters import BlurFilter, BrightnessFilter, EdgesFilter, GrayScaleFilter, BaseFilter


def ensure_directory(path):
    """
    Crea un directorio si no existe.
    
    Args:
        path (str): Ruta del directorio
    """
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"   📁 Directorio '{path}/' creado")


def process_with_filter(image , filter_obj : BaseFilter, output_path):
    """
    Procesa una imagen con un filtro y mide el tiempo.
    
    Args:
        image (PIL.Image.Image): Imagen de entrada
        filter_obj (BaseFilter): Filtro a aplicar
        output_path (str): Ruta donde guardar el resultado
        
    Returns:
        float: Tiempo de procesamiento en segundos
    """
    start_time = time.time()
    
    # Aplicar filtro
    result = filter_obj.apply(image)
    
    # Guardar resultado
    result.save(output_path, quality=95)
    
    elapsed_time = time.time() - start_time
    return elapsed_time


def main():
    """
    Función principal que ejecuta el demo de todos los filtros.
    """
    print("🎨 Demo de Todos los Filtros")
    print("=" * 60)
    
    # Configuración
    input_path = "images/Clocktower_Panorama_20080622_20mb.jpg"
    output_dir = "output"
    
    # Verificar que la imagen existe
    if not os.path.exists(input_path):
        print(f"\n❌ Error: No se encontró la imagen en '{input_path}'")
        print("\n💡 Por favor:")
        print("   1. Crea la carpeta 'images/'")
        print("   2. Coloca una imagen llamada 'sample.jpg' en ella")
        return
    
    # Crear directorio de salida
    ensure_directory(output_dir)
    
    # Cargar imagen original
    print(f"\n📥 Cargando imagen: {input_path}")
    try:
        original_image = Image.open(input_path)
        width, height = original_image.size
        print(f"   ✅ Imagen cargada: {width}x{height} píxeles")
        print(f"   🎨 Modo de color: {original_image.mode}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Definir filtros a aplicar
    filters_to_apply = [
        # (Filtro, Nombre descriptivo, Nombre del archivo)
        (BlurFilter(radius=2), "Blur Suave", "01_blur_light.jpg"),
        (BlurFilter(radius=5), "Blur Medio", "02_blur_medium.jpg"),
        (BlurFilter(radius=10), "Blur Intenso", "03_blur_heavy.jpg"),
        (BrightnessFilter(factor=0.5), "Oscura 50%", "04_dark.jpg"),
        (BrightnessFilter(factor=1.5), "Brillante 150%", "05_bright.jpg"),
        (BrightnessFilter(factor=2.0), "Muy Brillante 200%", "06_very_bright.jpg"),
        (EdgesFilter(), "Detección de Bordes", "07_edges.jpg"),
        (GrayScaleFilter(), "Filtro a grises", "gray_scale.jpg")
    ]
    
    print(f"\n🔄 Procesando {len(filters_to_apply)} variaciones...")
    print("-" * 60)
    
    # Procesar cada filtro
    results = []
    for i, (filter_obj, description, filename) in enumerate(filters_to_apply, 1):
        output_path = os.path.join(output_dir, filename)
        
        print(f"\n{i}. {description}")
        print(f"   Filtro: {filter_obj}")
        
        try:
            processing_time = process_with_filter(
                original_image,
                filter_obj,
                output_path
            )
            
            print(f"   ✅ Guardado: {output_path}")
            print(f"   ⏱️  Tiempo: {processing_time:.3f} segundos")
            
            results.append({
                'description': description,
                'filename': filename,
                'time': processing_time,
                'status': 'success'
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'description': description,
                'filename': filename,
                'time': 0,
                'status': 'failed'
            })
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PROCESAMIENTO")
    print("=" * 60)
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']
    
    print(f"\n✅ Exitosos: {len(successful)}/{len(results)}")
    if failed:
        print(f"❌ Fallidos: {len(failed)}/{len(results)}")
    
    # Estadísticas de tiempo
    if successful:
        total_time = sum(r['time'] for r in successful)
        avg_time = total_time / len(successful)
        
        print(f"\n⏱️  Tiempo total: {total_time:.3f} segundos")
        print(f"⏱️  Tiempo promedio: {avg_time:.3f} segundos por filtro")
    
    # Lista de archivos generados
    print(f"\n📁 Archivos generados en '{output_dir}/':")
    for r in successful:
        print(f"   • {r['filename']} ({r['description']})")
    
    print("\n" + "=" * 60)
    print("✨ Demo completado!")
    print(f"📂 Revisa las imágenes en la carpeta '{output_dir}/'")
    print("=" * 60)
    
    # Consejos
    print("\n💡 Consejos:")
    print("   • Compara las imágenes para entender cada filtro")
    print("   • Experimenta cambiando los parámetros en el código")
    print("   • Prueba con diferentes imágenes de entrada")
    print("   • En la próxima sesión veremos cómo combinar filtros")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Demo de FilterPipeline - Cadena de filtros.

Este script demuestra cómo:
1. Crear un pipeline con múltiples filtros
2. Aplicar el pipeline a una imagen
3. Ver estadísticas de cada filtro
4. Guardar imágenes intermedias (opcional)
"""

import os
import sys

# Agregar directorios al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
from core import FilterPipeline
from filters import BlurFilter, BrightnessFilter, EdgesFilter, GrayscaleFilter


def main():
    print("🔗 Demo: FilterPipeline")
    print("=" * 70)
    
    # Verificar imagen
    input_path = "images/sample.jpg"
    if not os.path.exists(input_path):
        print(f"❌ No se encontró la imagen: {input_path}")
        print("💡 Coloca una imagen llamada 'sample.jpg' en la carpeta images/")
        return
    
    # Cargar imagen
    print(f"\n📥 Cargando imagen: {input_path}")
    image = Image.open(input_path)
    print(f"   Tamaño: {image.size[0]}x{image.size[1]} píxeles")
    
    # ========================================================================
    # Ejemplo 1: Pipeline Básico
    # ========================================================================
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Pipeline Básico")
    print("=" * 70)
    
    print("\n🔧 Creando pipeline:")
    print("   1. Blur (radius=3)")
    print("   2. Brightness (factor=1.3)")
    print("   3. Edges")
    
    pipeline1 = FilterPipeline([
        EdgesFilter(),
        BlurFilter(radius=3),
        BrightnessFilter(factor=1.3)
    ])
    
    print(f"\n✅ Pipeline creado: {pipeline1}")
    
    print("\n🔄 Aplicando pipeline...")
    result1, stats1 = pipeline1.apply(image)
    
    # Mostrar estadísticas
    print(f"\n📊 Estadísticas:")
    print(f"   Tiempo total: {stats1['total_time']:.3f}s")
    print(f"   Filtros exitosos: {stats1['successful']}/{stats1['total_filters']}")
    
    print(f"\n⏱️  Detalles por filtro:")
    for f in stats1['filters']:
        status_icon = '✅' if f['status'] == 'success' else '❌'
        print(f"   {status_icon} {f['name']}: {f['time']:.3f}s")
    
    # Guardar resultado
    output1 = "output/pipeline_basic.jpg"
    os.makedirs("output", exist_ok=True)
    result1.save(output1)
    print(f"\n💾 Guardado: {output1}")
    
    # ========================================================================
    # Ejemplo 2: Pipeline con Escala de Grises
    # ========================================================================
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Pipeline 'Sketch Effect'")
    print("=" * 70)
    
    print("\n🎨 Creando pipeline estilo 'dibujo a lápiz':")
    print("   1. Grayscale (convertir a blanco y negro)")
    print("   2. Brightness (aumentar 20%)")
    print("   3. Edges (detectar contornos)")
    
    pipeline2 = FilterPipeline([
        GrayscaleFilter(),
        BrightnessFilter(factor=1.2),
        EdgesFilter()
    ])
    
    print("\n🔄 Aplicando pipeline...")
    result2, stats2 = pipeline2.apply(image)
    
    print(f"\n📊 Tiempo total: {stats2['total_time']:.3f}s")
    
    output2 = "output/pipeline_sketch.jpg"
    result2.save(output2)
    print(f"💾 Guardado: {output2}")
    
    # ========================================================================
    # Ejemplo 3: Pipeline con Imágenes Intermedias
    # ========================================================================
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Guardar Imágenes Intermedias")
    print("=" * 70)
    
    print("\n💡 Útil para ver el efecto de cada filtro paso a paso")
    
    pipeline3 = FilterPipeline([
        BlurFilter(radius=5),
        BrightnessFilter(factor=1.5),
        GrayscaleFilter()
    ], save_intermediate=True)
    
    intermediate_dir = "output/intermediate"
    print(f"\n🔄 Aplicando pipeline (guardando intermedias en {intermediate_dir})...")
    result3, stats3 = pipeline3.apply(image, output_dir=intermediate_dir)
    
    print(f"\n✅ Imágenes intermedias guardadas:")
    for i, f in enumerate(stats3['filters']):
        filename = f"step_{i:02d}_{f['name']}.jpg"
        print(f"   {i+1}. {filename}")
    
    # ========================================================================
    # Ejemplo 4: Modificar Pipeline Dinámicamente
    # ========================================================================
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Modificar Pipeline en Runtime")
    print("=" * 70)
    
    print("\n🔧 Creando pipeline inicial:")
    pipeline4 = FilterPipeline([
        BlurFilter(radius=2),
        BrightnessFilter(factor=1.3)
    ])
    print(f"   Filtros: {pipeline4.get_filter_names()}")
    
    print("\n➕ Añadiendo filtro de edges...")
    pipeline4.add_filter(EdgesFilter())
    print(f"   Filtros: {pipeline4.get_filter_names()}")
    
    print("\n🗑️  Eliminando primer filtro (Blur)...")
    removed = pipeline4.remove_filter(0)
    print(f"   Filtro eliminado: {removed}")
    print(f"   Filtros restantes: {pipeline4.get_filter_names()}")
    
    # Aplicar pipeline modificado
    print("\n🔄 Aplicando pipeline modificado...")
    result4, stats4 = pipeline4.apply(image)
    
    output4 = "output/pipeline_modified.jpg"
    result4.save(output4)
    print(f"💾 Guardado: {output4}")
    
    # ========================================================================
    # Resumen Final
    # ========================================================================
    print("\n" + "=" * 70)
    print("✨ DEMO COMPLETADO")
    print("=" * 70)
    
    print("\n📁 Archivos generados:")
    print("   • output/pipeline_basic.jpg      (blur + brightness + edges)")
    print("   • output/pipeline_sketch.jpg     (grayscale + brightness + edges)")
    print("   • output/pipeline_modified.jpg   (brightness + edges)")
    print("   • output/intermediate/           (pasos intermedios)")
    
    print("\n💡 Próximos pasos:")
    print("   1. Experimenta creando tus propios pipelines")
    print("   2. Prueba con diferentes combinaciones de filtros")
    print("   3. Ejecuta 'python demos/demo_factory.py' para ver el Factory")
    print("   4. Ejecuta 'python demos/demo_batch.py' para procesamiento en lote")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Script de verificación y solución de problemas de procesamiento
Verifica por qué las imágenes no se procesan
"""

import subprocess
import os
import sys

def run_cmd(cmd, show_output=True):
    """Ejecutar comando"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if show_output and result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(result.stderr)
        return result.returncode == 0, result.stdout
    except Exception as e:
        print(f"Error: {e}")
        return False, ""

def check_section(title):
    print(f"\n{'='*70}")
    print(f"🔍 {title}")
    print('='*70)

def main():
    print("="*70)
    print("DIAGNÓSTICO: ¿Por qué no se procesan las imágenes?")
    print("="*70)
    
    # 1. Verificar que los pods estén corriendo
    check_section("1. ¿Están los pods corriendo?")
    
    print("Workers:")
    success, output = run_cmd("kubectl get pods -l app=image-worker")
    worker_count = len([l for l in output.split('\n') if 'Running' in l])
    
    if worker_count == 0:
        print("❌ PROBLEMA: No hay workers corriendo")
        print("SOLUCIÓN: kubectl apply -f worker-deployment.yaml")
        return
    print(f"✅ {worker_count} workers corriendo")
    
    print("\nAPI:")
    success, output = run_cmd("kubectl get pods -l app=image-api")
    api_running = 'Running' in output
    
    if not api_running:
        print("❌ PROBLEMA: API no está corriendo")
        return
    print("✅ API corriendo")
    
    print("\nRedis:")
    success, output = run_cmd("kubectl get pods -l app=redis")
    redis_running = 'Running' in output
    
    if not redis_running:
        print("❌ PROBLEMA: Redis no está corriendo")
        return
    print("✅ Redis corriendo")
    
    # 2. Verificar directorios locales
    check_section("2. ¿Existen los directorios locales?")
    
    static_dir = "/Users/eduardo.arias/dev/other/ProgrammingCourse/Chapter-Threads/Projects/static"
    processed_dir = f"{static_dir}/processed"
    
    if not os.path.exists(static_dir):
        print(f"❌ PROBLEMA: {static_dir} NO EXISTE")
        print("\nSOLUCIÓN: Crear directorios")
        print(f"  mkdir -p {processed_dir}")
        
        print("\n🔧 ¿Quieres que los cree ahora? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            os.makedirs(processed_dir, exist_ok=True)
            print(f"✅ Directorios creados")
            
            # Copiar una imagen de ejemplo
            sample_sources = [
                "/Users/eduardo.arias/dev/other/ProgrammingCourse/Projects/WIP/session1_image_basics/images/sample.jpg",
                "/Users/eduardo.arias/dev/other/ProgrammingCourse/Projects/WIP/session7_kubernetes/images/sample.jpg"
            ]
            
            for source in sample_sources:
                if os.path.exists(source):
                    import shutil
                    dest = f"{static_dir}/sample.jpg"
                    shutil.copy(source, dest)
                    print(f"✅ Imagen de ejemplo copiada a {dest}")
                    break
        else:
            print("Directorios no creados, saliendo...")
            return
    else:
        print(f"✅ {static_dir} existe")
        
        # Listar contenido
        files = os.listdir(static_dir)
        print(f"   Archivos: {len([f for f in files if os.path.isfile(os.path.join(static_dir, f))])}")
        
        if os.path.exists(processed_dir):
            processed_files = os.listdir(processed_dir)
            print(f"   Procesadas: {len(processed_files)}")
            if processed_files:
                print(f"   Últimas 5:")
                for f in processed_files[-5:]:
                    print(f"     - {f}")
    
    # 3. Verificar Redis tiene tareas
    check_section("3. ¿Hay tareas en Redis?")
    
    success, output = run_cmd(
        "kubectl exec deployment/redis-deployment -- redis-cli LLEN tasks:pending",
        show_output=False
    )
    
    if success:
        pending = int(output.strip() or 0)
        print(f"Tareas pendientes: {pending}")
        
        if pending == 0:
            print("⚠️  No hay tareas pendientes")
            print("Esto es normal si ya se procesaron o no se han enviado")
    
    success, output = run_cmd(
        "kubectl exec deployment/redis-deployment -- redis-cli LLEN tasks:processing",
        show_output=False
    )
    if success:
        processing = int(output.strip() or 0)
        print(f"Tareas procesando: {processing}")
    
    success, output = run_cmd(
        "kubectl exec deployment/redis-deployment -- redis-cli LLEN tasks:completed",
        show_output=False
    )
    if success:
        completed = int(output.strip() or 0)
        print(f"Tareas completadas: {completed}")
        
        if completed > 0:
            print(f"✅ Se han procesado {completed} tareas!")
    
    # 4. Verificar logs de workers
    check_section("4. ¿Qué dicen los logs de los workers?")
    
    print("Últimas 20 líneas de logs de workers:")
    run_cmd("kubectl logs -l app=image-worker --tail=20")
    
    # 5. Verificar logs del API
    check_section("5. ¿Qué dice el API?")
    
    print("Últimas 20 líneas de logs del API:")
    run_cmd("kubectl logs -l app=image-api --tail=20")
    
    # 6. Probar conectividad
    check_section("6. ¿Pueden los workers conectarse a Redis?")
    
    # Obtener nombre de un pod worker
    success, output = run_cmd("kubectl get pods -l app=image-worker -o name --no-headers", show_output=False)
    if success and output.strip():
        worker_pod = output.strip().split('\n')[0].replace('pod/', '')
        print(f"Probando desde: {worker_pod}")
        
        success, output = run_cmd(
            f"kubectl exec {worker_pod} -- redis-cli -h redis ping",
            show_output=False
        )
        
        if success and 'PONG' in output:
            print("✅ Worker puede conectarse a Redis")
        else:
            print("❌ Worker NO puede conectarse a Redis")
            print("SOLUCIÓN: Verificar que Redis service existe")
    
    # Resumen
    print("\n" + "="*70)
    print("📋 RESUMEN Y ACCIONES")
    print("="*70)
    
    print("\n🔧 Para verificar procesamiento en tiempo real:")
    print("  # Terminal 1: Ver tareas en Redis")
    print("  watch -n 2 'kubectl exec deployment/redis-deployment -- redis-cli LLEN tasks:pending'")
    print("\n  # Terminal 2: Ver logs de workers")
    print("  kubectl logs -f -l app=image-worker")
    print("\n  # Terminal 3: Enviar tareas")
    print("  python3 demo.py")
    
    print("\n🐛 Para debugging:")
    print("  # Ver dentro de un worker")
    print(f"  kubectl exec -it {worker_pod if 'worker_pod' in locals() else '<worker-pod>'} -- /bin/bash")
    print("  # Ver estructura de directorios")
    print("  ls -la /app/static")
    print("  ls -la /app/static/processed")
    
    print("\n📂 Directorio de salida:")
    print(f"  {processed_dir}")
    print(f"  ls -lt {processed_dir} | head -10")

if __name__ == "__main__":
    main()


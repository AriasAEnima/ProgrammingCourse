#!/usr/bin/env python3
"""
KUBERNETES AUTO-SCALING DEMO
Cross-platform demo script for the Kubernetes class
"""

import subprocess
import time
import sys
import os
import platform

def run_cmd(cmd, description="", show_header=True):
    """Run command and show output with cross-platform support"""
    if description and show_header:
        print(f"\n> {description}")
        print("=" * 50)
    
    print(f"$ {cmd}")
    try:
        # Cross-platform shell configuration
        is_windows = platform.system() == "Windows"
        shell_cmd = cmd
        
        # Use utf-8 encoding to avoid Windows cp1252 issues
        result = subprocess.run(
            shell_cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'  # Ignore problematic characters
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def wait_for_pods(label, timeout=60):
    """Wait for pods to be ready"""
    print(f"\nWaiting for pods with label {label} to be ready...")
    cmd = f"kubectl wait --for=condition=ready pod -l {label} --timeout={timeout}s"
    return run_cmd(cmd)

def check_python_dependencies():
    """Check if required Python packages are available"""
    try:
        import requests
        from concurrent.futures import ThreadPoolExecutor
        return True
    except ImportError as e:
        print(f"⚠️ Missing Python dependency: {e}")
        print("Para stress test completo, instala: pip install requests")
        return False

def send_heavy_task_simple():
    """Fallback stress test using curl (cross-platform)"""
    is_windows = platform.system() == "Windows"
    
    # Prepare curl command based on platform
    if is_windows:
        # Windows PowerShell curl (Invoke-WebRequest alias)
        curl_cmd = '''powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/api/process-batch/distributed/' -Method POST -ContentType 'application/json' -Body '{\\\"filters\\\":[\\\"resize\\\",\\\"blur\\\"],\\\"count\\\":2}' -TimeoutSec 10 } catch { Write-Host 'Request failed' }"'''
    else:
        # Unix/Linux/Mac curl
        curl_cmd = "curl -X POST 'http://localhost:8000/api/process-batch/distributed/' -H 'Content-Type: application/json' -d '{\"filters\":[\"resize\",\"blur\"],\"count\":2}' --max-time 10"
    
    try:
        result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            print("✅ Heavy task sent via curl")
            return True
        else:
            print(f"❌ Curl failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Curl error: {e}")
        return False

def main():
    # Detect platform
    current_platform = platform.system()
    platform_info = f"{current_platform} {platform.release()}"
    
    print("KUBERNETES AUTO-SCALING DEMO")
    print("================================")
    print(f"Plataforma detectada: {platform_info}")
    print("Este demo funciona en Windows, Linux y Mac")
    print("")
    
    # Check if kubectl is available
    if not run_cmd("kubectl version --client", "Checking kubectl"):
        print("ERROR: kubectl no está instalado o no está en PATH")
        print("Instala kubectl desde: https://kubernetes.io/docs/tasks/tools/")
        sys.exit(1)
    
    # Check cluster connection
    if not run_cmd("kubectl cluster-info", "Checking cluster connection"):
        print("❌ No hay conexión a un cluster de Kubernetes")
        print("Opciones:")
        print("  - minikube start")
        print("  - kind create cluster") 
        print("  - Docker Desktop → Enable Kubernetes")
        sys.exit(1)
    
    # Check Docker images - cross-platform approach
    print("\nVerificando imágenes Docker optimizadas...")
    # Cross-platform: use docker images with filter instead of grep
    result = subprocess.run("docker images projects*", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    
    # Check for final API image
    if "projects-api-final" not in result.stdout:
        print("WARNING: No se encontró projects-api-final:latest")
        print("SOLUTION: Necesitas ejecutar: python build.py")
    
    # Check for final worker image  
    if "projects-worker-final" not in result.stdout:
        print("WARNING: No se encontró projects-worker-final:latest")
        print("SOLUTION: Necesitas ejecutar: python build.py")
    
    print("\n" + "="*60)
    print("INICIANDO DEMO - AUTO-SCALING EN KUBERNETES")
    print("="*60)
    print("NOTA: Usamos imágenes FINALES del proyecto:")
    print("   - API: projects-api-final:latest (Django + Debian + OpenCV)")
    print("   - Worker: projects-worker-final:latest (Python + Debian + OpenCV)")
    print("   - Objetivo: Ver AUTO-SCALING funcionando")
    print("="*60)
    
    # Deploy Redis
    run_cmd("kubectl apply -f redis-deployment.yaml", "1️⃣ Deploying Redis")
    
    # Deploy API  
    run_cmd("kubectl apply -f api-deployment.yaml", "2️⃣ Deploying API")
    
    # Deploy Workers + HPA
    run_cmd("kubectl apply -f worker-deployment.yaml", "3️⃣ Deploying Workers + HPA")
    
    # Install metrics server automatically
    print("\n🔧 Installing metrics server...")
    run_cmd("kubectl apply -f metrics-server.yaml", "Installing metrics server (local file)")
    
    # Wait for pods
    print("\n4️⃣ Waiting for all pods to be ready...")
    wait_for_pods("app=redis")
    wait_for_pods("app=image-api") 
    wait_for_pods("app=image-worker")
    
    # Show current status
    run_cmd("kubectl get pods", "5️⃣ Current Pod Status")
    run_cmd("kubectl get hpa", "HPA Status")
    
    # Give metrics server time to collect data
    print("\n⏳ Waiting for metrics server to collect data...")
    print("Esperando hasta que HPA tenga métricas reales (no <unknown>)...")
    
    # Wait until HPA shows real metrics (not <unknown>)
    for attempt in range(30):  # Max 5 minutes
        result = subprocess.run(
            "kubectl get hpa --no-headers", 
            shell=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.stdout and "<unknown>" not in result.stdout:
            print(f"✅ Métricas disponibles después de {attempt*10} segundos")
            break
        
        print(f"⏱️ Intento {attempt+1}/30: Esperando métricas... (aún <unknown>)")
        time.sleep(10)
    else:
        print("⚠️ Timeout esperando métricas, continuando de todos modos...")
    
    # Auto-configurar HPA para escalado más agresivo
    print("\n🔧 Auto-configurando HPA para escalado visible...")
    print("Ajustando CPU target a 15% para que escale más fácilmente...")
    
    patch_result = subprocess.run(
        "kubectl patch hpa worker-hpa --type='json' -p='[{\"op\": \"replace\", \"path\": \"/spec/metrics/0/resource/target/averageUtilization\", \"value\": 15}]'",
        shell=True,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    
    if patch_result.returncode == 0:
        print("✅ HPA configurado con CPU target = 15%")
        print("   Esto hará que escale cuando CPU > 15m (muy sensible)")
    else:
        print("⚠️ No se pudo ajustar HPA, usando configuración actual")
    
    time.sleep(2)
    
    # Show current metrics
    run_cmd("kubectl get hpa", "📊 Métricas actuales antes del stress test")
    
    # Purge Redis queue before starting stress test
    print("\n🧹 Purging Redis queue to ensure clean state...")
    try:
        purge_result = subprocess.run(
            "kubectl exec deployment/redis-deployment -- redis-cli FLUSHALL",
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if purge_result.returncode == 0:
            print("✅ Redis queue purged successfully")
        else:
            print("⚠️ Redis purge warning:", purge_result.stderr.strip())
    except Exception as e:
        print(f"⚠️ Could not purge Redis: {e}")
    
    # Wait for workers to re-register after purge
    print("⏳ Waiting for workers to re-register after purge...")
    for attempt in range(12):  # Max 2 minutes
        try:
            workers_check = subprocess.run(
                "kubectl exec deployment/redis-deployment -- redis-cli HLEN workers",
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            worker_count = int(workers_check.stdout.strip() or 0)
            if worker_count > 0:
                print(f"✅ {worker_count} workers re-registered after purge")
                break
            print(f"⏱️ Attempt {attempt+1}/12: {worker_count} workers registered...")
            time.sleep(10)
        except:
            time.sleep(10)
    else:
        print("⚠️ No workers registered after purge, continuing anyway...")
    
    print("\n" + "="*60)
    print("🔥 STRESS TEST PHASE")
    print("="*60)
    
    # Setup port forwarding
    print("\n6️⃣ Setting up port forwarding...")
    print("Iniciando port-forward en background...")
    
    # Start port forwarding in background
    try:
        port_forward_process = subprocess.Popen(
            ["kubectl", "port-forward", "service/api-service", "8000:8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)
        print("✅ Port-forward iniciado")
    except Exception as e:
        print(f"⚠️ Port-forward error: {e}")
    
    print("\n7️⃣ Generando carga CPU real con procesamiento de imágenes...")
    time.sleep(5)  # Wait for API to be ready
    
    # Check if we have Python dependencies for advanced stress test
    has_dependencies = check_python_dependencies()
    
    if has_dependencies:
        # Advanced stress test with requests and threading
        print("🖼️ Enviando MUCHAS tareas pesadas para forzar auto-scaling (método avanzado)...")
        print("   - Objetivo: Saturar los 2 workers iniciales y forzar escalado")
        print("   - Tareas: 100 (cada una con 4 imágenes grandes)")
        print("   - Tiempo estimado: 3-5 minutos\n")
        import requests
        from concurrent.futures import ThreadPoolExecutor
        
        def send_heavy_task(task_num):
            """Send heavy image processing task"""
            payload = {
                "filters": ["resize", "blur", "sharpen", "edges", "blur", "sharpen"],  # 6 filtros
                "filter_params": {
                    "resize": {"width": 3072, "height": 3072},  # 3K imágenes
                    "blur": {"radius": 8.0},  # Más blur
                    "sharpen": {"factor": 2.5}
                },
                "count": 4  # 4 imágenes por tarea
            }
            try:
                response = requests.post(
                    "http://localhost:8000/api/process-batch/distributed/",
                    json=payload,
                    timeout=15  # Más timeout para tareas pesadas
                )
                if response.status_code == 200:
                    task_id = response.json().get('task_id', 'unknown')[:8]
                    if task_num % 10 == 0:  # Solo mostrar cada 10 tareas
                        print(f"✅ Tarea {task_num}: {task_id} encolada")
                    return True
                else:
                    print(f"❌ Tarea {task_num}: HTTP {response.status_code}")
                    return False
            except Exception as e:
                if task_num % 10 == 0:
                    print(f"⚠️ Tarea {task_num}: {str(e)[:50]}")
                return False
        
        # Send MANY heavy tasks to trigger scaling
        NUM_TASKS = 100  # 100 tareas pesadas
        print(f"📤 Enviando {NUM_TASKS} tareas en oleadas...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(send_heavy_task, i) for i in range(NUM_TASKS)]
            success_count = sum(1 for f in futures if f.result())
            print(f"\n📊 {success_count}/{NUM_TASKS} tareas pesadas enviadas correctamente")
            
        print(f"\n💡 Con {success_count} tareas pesadas en cola:")
        print(f"   - Cada worker procesará ~{success_count/2} tareas")
        print(f"   - Esto debería saturar los 2 workers iniciales")
        print(f"   - CPU debería subir > 15% → Trigger de auto-scaling")
    else:
        # Fallback stress test using curl
        print("🖼️ Enviando tareas pesadas de procesamiento (método básico con curl)...")
        print("   Recomendación: Instala 'requests' para mejor stress test")
        print("   pip install requests")
        success_count = 0
        for i in range(50):  # 50 tareas (antes era 10)
            if send_heavy_task_simple():
                success_count += 1
            if i % 10 == 0:
                print(f"   Progreso: {i}/50 tareas enviadas...")
            time.sleep(0.3)  # Más rápido
        print(f"📊 {success_count}/50 tareas pesadas enviadas via curl")
    
    print("\n8️⃣ Verificando auto-scaling (escalado + descalado)...")
    print("Monitoreando durante 4 minutos (~16 checks de 15s)")
    print("Fases esperadas:")
    print("  📈 0-1 min: Escalado inicial (2 → 4+ pods)")
    print("  ⚡ 1-2 min: Escalado máximo bajo carga")
    print("  ⏱️  2-3 min: Estabilización mientras procesa")
    print("  📉 3-4 min: Descalado gradual al terminar tareas\n")
    
    for i in range(16):  # 16 checks = 4 minutos
        elapsed_min = (i * 15) / 60
        print(f"\n{'='*60}")
        print(f"⏱️  Check {i+1}/16 ({elapsed_min:.1f} min)")
        print('='*60)
        
        # Mostrar HPA status
        run_cmd("kubectl get hpa worker-hpa", show_header=False)
        
        # Mostrar métricas de CPU
        cpu_result = subprocess.run(
            "kubectl top pods -l app=image-worker --no-headers",
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if cpu_result.stdout.strip():
            print("\n📊 CPU por pod:")
            for line in cpu_result.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 2:
                    pod_name = parts[0].split('-')[-1][:8]  # Últimos 8 chars
                    cpu = parts[1]
                    mem = parts[2] if len(parts) > 2 else 'N/A'
                    print(f"   Worker-{pod_name}: CPU={cpu:>6}, MEM={mem:>8}")
        
        # Cross-platform pod count
        is_windows = platform.system() == "Windows"
        if is_windows:
            pods_count = subprocess.run("kubectl get pods -l app=image-worker --no-headers | find /c /v \"\"", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        else:
            pods_count = subprocess.run("kubectl get pods -l app=image-worker --no-headers | wc -l", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        current_pods = int(pods_count.stdout.strip() or 0)
        
        # Contar pods Running
        running_result = subprocess.run(
            "kubectl get pods -l app=image-worker --no-headers",
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        running_pods = len([l for l in running_result.stdout.split('\n') if 'Running' in l])
        
        print(f"\n🎯 Réplicas: {current_pods} total, {running_pods} Running")
        
        # Explicar qué está pasando según la fase
        if i < 4:
            print(f"📈 Fase: ESCALADO INICIAL")
            print(f"   Esperado: Ver aumento de pods (2 → 4+)")
            print(f"   Razón: Alta carga CPU por tareas en cola")
        elif i < 8:
            print(f"⚡ Fase: CARGA MÁXIMA")
            print(f"   Esperado: Pods estables en máximo o cerca")
            print(f"   Razón: Procesando tareas activamente")
        elif i < 12:
            print(f"⏱️  Fase: ESTABILIZACIÓN")
            print(f"   Esperado: CPU empieza a bajar")
            print(f"   Razón: Menos tareas en cola")
        else:
            print(f"📉 Fase: DESCALADO")
            print(f"   Esperado: Reducción gradual de pods")
            print(f"   Razón: Carga baja, volviendo a mínimo")
        
        time.sleep(15)  # Check cada 15 segundos
    
    # Final status
    print("\n" + "="*60)
    print("📊 ESTADO FINAL DEL SISTEMA")
    print("="*60)
    
    run_cmd("kubectl get hpa worker-hpa", "HPA Final Status")
    run_cmd("kubectl get pods -l app=image-worker", "Workers Final State")
    
    print("\n📈 Historial de eventos de auto-scaling:")
    events_result = subprocess.run(
        "kubectl describe hpa worker-hpa | grep -A 20 Events",
        shell=True,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    if events_result.stdout and "Events:" in events_result.stdout:
        print(events_result.stdout)
    else:
        print("No hay eventos de scaling registrados")
        print("Posibles razones:")
        print("  - Carga insuficiente para trigger")
        print("  - Metrics server no disponible")
        print("  - HPA configurado con threshold muy alto")
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETADO")
    print("="*60)
    print("\n📋 RESUMEN:")
    print("  • Cluster verificado")
    print("  • Redis, API y Workers desplegados")
    print("  • HPA auto-configurado (CPU target: 15%)")
    print("  • 100 tareas pesadas enviadas")
    print("  • Auto-scaling monitoreado durante 4 minutos")
    print("")
    print("💡 PARA STRESS TEST ADICIONAL:")
    print("   python stress_test.py 5 15  # 5 minutos, 15 tareas por batch")
    print("")
    print("¿Quieres limpiar los recursos? (y/n): ", end="")
    cleanup = input().strip().lower()
    
    if cleanup == 'y':
        print("\n🧹 Cleaning up...")
        run_cmd("kubectl delete -f .", "Removing all K8s resources")
        print("✅ Cleanup completado")
    else:
        print("\n📝 Para limpiar manualmente más tarde:")
        print("  kubectl delete -f k8s/")

if __name__ == "__main__":
    # Change to k8s directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    main()
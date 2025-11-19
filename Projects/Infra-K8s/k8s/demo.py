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
        print("🖼️ Enviando 10 tareas pesadas de procesamiento (método avanzado)...")
        import requests
        from concurrent.futures import ThreadPoolExecutor
        
        def send_heavy_task():
            """Send heavy image processing task"""
            payload = {
                "filters": ["resize", "blur", "sharpen", "edges"],
                "filter_params": {
                    "resize": {"width": 2048, "height": 2048},
                    "blur": {"radius": 5.0},
                    "sharpen": {"factor": 2.0}
                },
                "count": 2
            }
            try:
                response = requests.post(
                    "http://localhost:8000/api/process-batch/distributed/",
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    task_id = response.json().get('task_id', 'unknown')[:8]
                    print(f"✅ Heavy task queued: {task_id}")
                    return True
                else:
                    print(f"❌ HTTP {response.status_code}: {response.text[:100]}")
                    return False
            except Exception as e:
                print(f"❌ Task error: {e}")
                return False
        
        # Send multiple heavy tasks to trigger scaling
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(send_heavy_task) for _ in range(20)]
            success_count = sum(1 for f in futures if f.result())
            print(f"📊 {success_count}/20 tareas pesadas enviadas")
    else:
        # Fallback stress test using curl
        print("🖼️ Enviando tareas pesadas de procesamiento (método básico con curl)...")
        success_count = 0
        for i in range(10):  # Increased for better scaling
            if send_heavy_task_simple():
                success_count += 1
            time.sleep(0.5)  # Faster delivery
        print(f"📊 {success_count}/10 tareas pesadas enviadas via curl")
    
    print("\n8️⃣ Verificando auto-scaling (escalado + descalado)...")
    for i in range(8):  # Aumentamos a 8 checks para ver el descalado
        print(f"⏱️ Check {i+1}/8:")
        run_cmd("kubectl get hpa", f"Check {i+1}/8 - Auto-scaling status")
        
        # Cross-platform pod count
        is_windows = platform.system() == "Windows"
        if is_windows:
            # Windows doesn't have wc -l, use findstr
            pods_count = subprocess.run("kubectl get pods -l app=image-worker --no-headers | find /c /v \"\"", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        else:
            # Unix/Linux/Mac has wc -l
            pods_count = subprocess.run("kubectl get pods -l app=image-worker --no-headers | wc -l", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        current_pods = int(pods_count.stdout.strip() or 0)
        print(f"  Pods workers: {current_pods}")
        
        # Explicar qué está pasando
        if i < 3:
            print("  📈 Fase: Escalado - Debería ver aumento de pods")
        elif i < 6:
            print("  ⏱️ Fase: Estabilización - CPU debería bajar")
        else:
            print("  📉 Fase: Descalado - Debería ver reducción de pods")
        
        time.sleep(15)  # Aumentamos un poco el tiempo entre checks
    
    # Final status
    run_cmd("kubectl get hpa", "9️⃣ Final HPA Status")
    run_cmd("kubectl get pods", "Final Pod Count")
    run_cmd("kubectl describe hpa worker-hpa", "HPA Details")
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETADO")
    print("="*60)
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
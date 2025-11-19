#!/usr/bin/env python3
"""
🔥 STRESS TEST UNIVERSAL - KUBERNETES AUTO-SCALING
Script único para generar carga y verificar auto-scaling
Funciona en Windows, Mac y Linux
"""
import subprocess
import sys
import time
import platform
from concurrent.futures import ThreadPoolExecutor

def check_requirements():
    """Check if requests is available for advanced testing"""
    try:
        import requests
        return True
    except ImportError:
        print("⚠️ Para stress test avanzado, instala: pip install requests")
        return False

def send_heavy_task_advanced():
    """Send heavy task using requests (advanced method)"""
    import requests
    
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
            print(f"✅ Heavy task sent: {task_id}")
            return True
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def send_heavy_task_curl():
    """Send heavy task using curl (fallback method)"""
    is_windows = platform.system() == "Windows"
    
    if is_windows:
        # PowerShell Invoke-WebRequest
        curl_cmd = '''powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/api/process-batch/distributed/' -Method POST -ContentType 'application/json' -Body '{\\\"filters\\\":[\\\"resize\\\",\\\"blur\\\"],\\\"count\\\":2}' -TimeoutSec 10 } catch { Write-Host 'Request failed' }"'''
    else:
        # Unix curl
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

def monitor_hpa():
    """Monitor HPA status with cross-platform pod counting"""
    is_windows = platform.system() == "Windows"
    
    # Get HPA status
    hpa_result = subprocess.run(
        "kubectl get hpa --no-headers", 
        shell=True, capture_output=True, text=True,
        encoding='utf-8', errors='ignore'
    )
    
    if hpa_result.stdout:
        parts = hpa_result.stdout.split()
        if len(parts) >= 6:
            targets = parts[2]  # CPU/Memory targets
            replicas = parts[5]  # Current replicas
            print(f"📊 HPA: {targets} | Replicas: {replicas}")
    
    # Count worker pods (cross-platform)
    if is_windows:
        pods_cmd = "kubectl get pods -l app=image-worker --no-headers | find /c /v \"\""
    else:
        pods_cmd = "kubectl get pods -l app=image-worker --no-headers | wc -l"
    
    pods_result = subprocess.run(pods_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    worker_count = pods_result.stdout.strip() or "0"
    print(f"👥 Worker pods: {worker_count}")

def stress_test(duration_minutes=5, tasks_per_batch=10):
    """Run stress test for specified duration"""
    print(f"🔥 STRESS TEST - {duration_minutes} minutos")
    print("=" * 50)
    
    has_requests = check_requirements()
    
    if has_requests:
        print("🚀 Usando método avanzado (requests + threading)")
        send_task = send_heavy_task_advanced
        max_workers = 5
    else:
        print("🚀 Usando método básico (curl)")
        send_task = send_heavy_task_curl
        max_workers = 3
        tasks_per_batch = min(tasks_per_batch, 5)  # Reduce load for curl method
    
    end_time = time.time() + (duration_minutes * 60)
    total_sent = 0
    batch_count = 0
    
    while time.time() < end_time:
        batch_count += 1
        print(f"\n📦 Batch {batch_count}:")
        
        # Send tasks in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(send_task) for _ in range(tasks_per_batch)]
            success_count = sum(1 for f in futures if f.result())
            total_sent += success_count
        
        print(f"✅ Sent {success_count}/{tasks_per_batch} tasks (Total: {total_sent})")
        
        # Monitor current status
        monitor_hpa()
        
        # Wait before next batch
        remaining_time = end_time - time.time()
        if remaining_time > 30:
            print("⏳ Waiting 30 seconds...")
            time.sleep(30)
        elif remaining_time > 0:
            time.sleep(remaining_time)
    
    print(f"\n🎯 TOTAL ENVIADO: {total_sent} tareas")
    
    # Final monitoring
    print("\n📊 ESTADO FINAL:")
    monitor_hpa()
    subprocess.run("kubectl get pods", shell=True)

def main():
    print("🔥 STRESS TEST UNIVERSAL PARA KUBERNETES")
    print("🌍 Funciona en Windows, Mac y Linux")
    print("=" * 50)
    
    # Parse arguments
    duration = 5
    tasks = 10
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("⚠️ Duración debe ser un número (minutos)")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            tasks = int(sys.argv[2])
        except ValueError:
            print("⚠️ Tareas por batch debe ser un número")
            sys.exit(1)
    
    print(f"⏱️ Duración: {duration} minutos")
    print(f"📦 Tareas por batch: {tasks}")
    
    # Check if kubectl works
    try:
        subprocess.run("kubectl version --client", shell=True, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ kubectl no está disponible")
        sys.exit(1)
    
    # Check if API is accessible
    test_cmd = "curl -f http://localhost:8000/api/health/ --max-time 5" if platform.system() != "Windows" else "powershell -Command \"Invoke-WebRequest -Uri http://localhost:8000/api/health/ -TimeoutSec 5\""
    
    try:
        subprocess.run(test_cmd, shell=True, capture_output=True, check=True)
        print("✅ API accessible")
    except subprocess.CalledProcessError:
        print("❌ API no accesible. ¿Está corriendo kubectl port-forward service/api-service 8000:8000?")
        sys.exit(1)
    
    # Run stress test
    stress_test(duration, tasks)
    
    print("\n" + "=" * 50)
    print("✅ STRESS TEST COMPLETADO")
    print("💡 Para limpiar: kubectl delete -f .")

if __name__ == "__main__":
    main()
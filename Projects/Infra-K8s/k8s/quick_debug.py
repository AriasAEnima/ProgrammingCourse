#!/usr/bin/env python3
"""
Diagnóstico rápido: ¿Por qué no se procesan imágenes?
"""

import subprocess
import sys

def run(cmd):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n$ {cmd}")
    print("-" * 60)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.returncode == 0, result.stdout

print("="*70)
print("DIAGNÓSTICO RÁPIDO: Procesamiento de Imágenes")
print("="*70)

# 1. Ver HPA
print("\n1️⃣ Estado del HPA:")
run("kubectl get hpa")

# 2. Verificar Redis
print("\n2️⃣ ¿Redis está corriendo?")
run("kubectl get pods -l app=redis")

# 3. Verificar API
print("\n3️⃣ ¿API está corriendo?")
run("kubectl get pods -l app=image-api")

# 4. Ver tareas en Redis
print("\n4️⃣ Tareas en Redis:")
success, _ = run("kubectl exec deployment/redis-deployment -- redis-cli LLEN tasks:pending")
success, _ = run("kubectl exec deployment/redis-deployment -- redis-cli LLEN tasks:processing")
success, _ = run("kubectl exec deployment/redis-deployment -- redis-cli LLEN tasks:completed")

# 5. Ver workers registrados
print("\n5️⃣ Workers registrados en Redis:")
run("kubectl exec deployment/redis-deployment -- redis-cli HGETALL workers")

# 6. Logs del worker
print("\n6️⃣ Últimas 30 líneas de logs del worker:")
run("kubectl logs worker-deployment-66fb74cbf4-pwvm5 --tail=30")

# 7. Ver si hay errores
print("\n7️⃣ Buscar errores en logs:")
run("kubectl logs worker-deployment-66fb74cbf4-pwvm5 --tail=100 | grep -i 'error\\|exception\\|traceback\\|failed'")

# 8. Ver dentro del pod
print("\n8️⃣ Estructura de directorios dentro del pod:")
run("kubectl exec worker-deployment-66fb74cbf4-pwvm5 -- ls -la /app/static/")
run("kubectl exec worker-deployment-66fb74cbf4-pwvm5 -- ls -la /app/static/processed/")

# 9. Ver port-forward activo
print("\n9️⃣ ¿Hay port-forward activo?")
result = subprocess.run("ps aux | grep 'port-forward' | grep -v grep", shell=True, capture_output=True, text=True)
if result.stdout.strip():
    print("✅ Port-forward activo:")
    print(result.stdout)
else:
    print("❌ No hay port-forward activo")
    print("SOLUCIÓN: kubectl port-forward svc/api-service 8000:8000 &")

print("\n" + "="*70)
print("RECOMENDACIONES:")
print("="*70)

print("\n🔍 Para ver si el worker está procesando en tiempo real:")
print("   kubectl logs -f worker-deployment-66fb74cbf4-pwvm5")

print("\n🔍 Para enviar una tarea de prueba manualmente:")
print("   kubectl port-forward svc/api-service 8000:8000 &")
print('   curl -X POST http://localhost:8000/api/process-batch/distributed/ \\')
print('     -H "Content-Type: application/json" \\')
print('     -d \'{"filters":["blur"],"count":1}\'')

print("\n🔍 Para verificar conexión worker → Redis:")
print("   kubectl exec worker-deployment-66fb74cbf4-pwvm5 -- redis-cli -h redis ping")


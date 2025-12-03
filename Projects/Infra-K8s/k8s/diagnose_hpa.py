#!/usr/bin/env python3
"""
Script de diagnóstico para HPA (Horizontal Pod Autoscaler)
Identifica por qué el auto-scaling no funciona
"""

import subprocess
import sys
import time

def run_cmd(cmd, show_output=True):
    """Ejecutar comando y retornar resultado"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if show_output:
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"Error: {e}")
        return False, "", str(e)

def check_section(title):
    """Imprimir encabezado de sección"""
    print(f"\n{'='*70}")
    print(f"🔍 {title}")
    print('='*70)

def main():
    print("="*70)
    print("DIAGNÓSTICO DE HPA - ¿Por qué no escala?")
    print("="*70)
    
    # 1. Verificar Metrics Server
    check_section("1. ¿Está instalado el Metrics Server?")
    success, stdout, _ = run_cmd("kubectl get deployment metrics-server -n kube-system")
    if not success:
        print("❌ PROBLEMA: Metrics Server NO está instalado")
        print("SOLUCIÓN:")
        print("  kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml")
        print("  O si es local: kubectl apply -f metrics-server.yaml")
        return
    else:
        print("✅ Metrics Server está instalado")
    
    # 2. Verificar que Metrics Server funciona
    check_section("2. ¿Funciona kubectl top?")
    success, stdout, _ = run_cmd("kubectl top nodes", show_output=False)
    if not success or "error" in stdout.lower():
        print("❌ PROBLEMA: kubectl top nodes NO funciona")
        print("Metrics Server puede no estar listo o configurado correctamente")
        print("\nSOLUCIÓN:")
        print("  # Verificar logs del metrics server:")
        print("  kubectl logs -n kube-system deployment/metrics-server")
        print("\n  # Para desarrollo local, agregar flag:")
        print("  kubectl patch deployment metrics-server -n kube-system --type='json' \\")
        print("    -p='[{\"op\": \"add\", \"path\": \"/spec/template/spec/containers/0/args/-\", \"value\": \"--kubelet-insecure-tls\"}]'")
    else:
        print("✅ kubectl top nodes funciona")
        print(stdout)
    
    # 3. Verificar métricas de pods
    check_section("3. ¿Hay métricas de pods disponibles?")
    success, stdout, _ = run_cmd("kubectl top pods -l app=image-worker", show_output=False)
    if not success or "error" in stdout.lower() or not stdout.strip():
        print("❌ PROBLEMA: No hay métricas de pods")
        print("Puede ser que:")
        print("  - Los pods no están corriendo")
        print("  - Metrics Server necesita más tiempo")
        print("  - Los resources.requests no están definidos")
    else:
        print("✅ Métricas de pods disponibles:")
        print(stdout)
    
    # 4. Verificar HPA existe
    check_section("4. ¿Existe el HPA?")
    success, stdout, _ = run_cmd("kubectl get hpa")
    if not success or not stdout.strip() or "No resources" in stdout:
        print("❌ PROBLEMA: HPA no está creado")
        print("SOLUCIÓN:")
        print("  kubectl apply -f worker-deployment.yaml")
        return
    else:
        print("✅ HPA existe")
    
    # 5. Verificar estado del HPA
    check_section("5. ¿Qué dice el HPA?")
    success, stdout, _ = run_cmd("kubectl get hpa worker-hpa -o wide")
    
    if "<unknown>" in stdout:
        print("❌ PROBLEMA: HPA muestra <unknown>")
        print("Esto significa que no puede obtener métricas")
        print("\nCAUSAS POSIBLES:")
        print("  1. Metrics Server no está funcionando")
        print("  2. Los pods no tienen resources.requests definidos")
        print("  3. Los pods apenas se crearon (espera 1-2 minutos)")
        print("\nVERIFICAR:")
        run_cmd("kubectl describe hpa worker-hpa | tail -20")
    else:
        print("✅ HPA tiene métricas")
    
    # 6. Verificar configuración del HPA
    check_section("6. Configuración del HPA")
    success, stdout, _ = run_cmd("kubectl get hpa worker-hpa -o yaml", show_output=False)
    
    # Extraer valores importantes
    import re
    
    min_replicas = re.search(r'minReplicas:\s*(\d+)', stdout)
    max_replicas = re.search(r'maxReplicas:\s*(\d+)', stdout)
    cpu_target = re.search(r'averageUtilization:\s*(\d+)', stdout)
    
    print(f"Min Replicas: {min_replicas.group(1) if min_replicas else 'N/A'}")
    print(f"Max Replicas: {max_replicas.group(1) if max_replicas else 'N/A'}")
    print(f"CPU Target: {cpu_target.group(1) if cpu_target else 'N/A'}%")
    
    if cpu_target and int(cpu_target.group(1)) < 50:
        print(f"\n⚠️  ADVERTENCIA: CPU target ({cpu_target.group(1)}%) es muy bajo")
        print("   Con target bajo, se necesita MUY poca carga para escalar")
        print("   Esto puede causar que NO escale si las tareas son muy rápidas")
    
    # 7. Verificar pods actuales
    check_section("7. Estado actual de los pods")
    success, stdout, _ = run_cmd("kubectl get pods -l app=image-worker")
    
    # Contar pods
    pod_count = len([line for line in stdout.split('\n') if 'image-worker' in line])
    print(f"\n📊 Pods actuales: {pod_count}")
    
    # 8. Verificar CPU actual vs target
    check_section("8. CPU Actual vs Target")
    success, stdout, _ = run_cmd("kubectl top pods -l app=image-worker", show_output=False)
    
    if success and stdout.strip():
        print("CPU actual de cada pod:")
        print(stdout)
        
        # Calcular promedio
        cpu_values = []
        for line in stdout.split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    cpu = parts[1].replace('m', '')
                    try:
                        cpu_values.append(int(cpu))
                    except:
                        pass
        
        if cpu_values:
            avg_cpu = sum(cpu_values) / len(cpu_values)
            print(f"\n📊 CPU Promedio: {avg_cpu:.0f}m (millicores)")
            
            if cpu_target:
                target = int(cpu_target.group(1))
                # requests es 100m según el deployment
                target_millicores = target * 100 / 100  # (target% * requests) / 100
                print(f"📊 CPU Target: {target}% de 100m = {target:.0f}m")
                
                if avg_cpu < target:
                    print(f"\n❌ PROBLEMA ENCONTRADO:")
                    print(f"   CPU actual ({avg_cpu:.0f}m) < Target ({target:.0f}m)")
                    print(f"   ¡Por eso NO está escalando!")
                    print(f"\n💡 SOLUCIONES:")
                    print(f"   1. Enviar MÁS tareas simultáneamente")
                    print(f"   2. Hacer tareas MÁS pesadas (más filtros, imágenes más grandes)")
                    print(f"   3. REDUCIR el CPU target a 20% o menos")
                else:
                    print(f"\n✅ CPU está por encima del target, debería estar escalando")
    
    # 9. Verificar eventos del HPA
    check_section("9. Eventos recientes del HPA")
    success, stdout, _ = run_cmd("kubectl describe hpa worker-hpa | grep -A 10 Events")
    if not stdout or "No events" in stdout:
        print("⚠️  No hay eventos de scaling")
        print("Esto significa que el HPA no ha intentado escalar")
    
    # 10. Verificar que Redis está corriendo
    check_section("10. ¿Está Redis funcionando?")
    success, stdout, _ = run_cmd("kubectl get pods -l app=redis")
    if "Running" in stdout:
        print("✅ Redis está corriendo")
    else:
        print("❌ Redis puede tener problemas")
    
    # RESUMEN Y RECOMENDACIONES
    print("\n" + "="*70)
    print("📋 RESUMEN Y RECOMENDACIONES")
    print("="*70)
    
    print("\n🔧 OPCIONES PARA FORZAR ESCALADO:")
    print("\n1️⃣  REDUCIR el CPU target (más fácil de alcanzar):")
    print("   kubectl patch hpa worker-hpa --patch '{\"spec\":{\"metrics\":[{\"type\":\"Resource\",\"resource\":{\"name\":\"cpu\",\"target\":{\"type\":\"Utilization\",\"averageUtilization\":20}}}]}}'")
    
    print("\n2️⃣  AUMENTAR la carga (más tareas simultáneas):")
    print("   # En lugar de 10-20 tareas, enviar 100-200")
    print("   # Modificar demo.py línea 288: range(200)")
    
    print("\n3️⃣  HACER tareas MÁS pesadas:")
    print("   # Imágenes más grandes: 4096x4096")
    print("   # Más filtros: 6-8 filtros en pipeline")
    
    print("\n4️⃣  REDUCIR resources.requests (hace target más fácil):")
    print("   # En worker-deployment.yaml, cambiar:")
    print("   # cpu: \"100m\" → \"50m\"")
    
    print("\n5️⃣  MONITOREAR en tiempo real:")
    print("   # Terminal 1:")
    print("   watch kubectl get hpa")
    print("   # Terminal 2:")
    print("   watch kubectl top pods -l app=image-worker")
    print("   # Terminal 3:")
    print("   python demo.py")
    
    print("\n" + "="*70)
    print("✅ Diagnóstico completado")
    print("="*70)

if __name__ == "__main__":
    main()


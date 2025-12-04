# Kubernetes Auto-Scaling Demo

Demo de auto-scaling en Kubernetes con procesamiento distribuido de imágenes.

## 📚 ¿Qué es HPA?

**HPA** = **Horizontal Pod Autoscaler**

Es un componente de Kubernetes que **automáticamente** ajusta el número de pods (réplicas) de un Deployment basándose en métricas como:
- CPU utilization (uso de CPU)
- Memory utilization (uso de memoria)
- Métricas custom (ej: longitud de cola)

**Ejemplo en este demo:**
- **Min replicas**: 1 worker
- **Max replicas**: 10 workers
- **Target CPU**: 15% (escala si CPU > 15%)
- **Resultado**: Cuando hay carga, Kubernetes crea más workers automáticamente. Cuando baja la carga, los elimina.

## 📁 Archivos del Demo

### Esenciales (Kubernetes)
- `demo.py` - **Script principal del demo**
- `redis-deployment.yaml` - Redis como cola de tareas
- `api-deployment.yaml` - API Django
- `worker-deployment.yaml` - Workers para Mac/Linux
- `worker-deployment-windows.yaml` - Workers para Windows
- `metrics-server.yaml` - Metrics Server para HPA

### Opcionales
- `stress_test.py` - Stress test personalizado (avanzado)
- `PLATFORM_NOTES.md` - Notas técnicas de la plataforma

## 🚀 Quick Start

### ⚠️ Primera Vez (Construir imágenes Docker)

Si las imágenes Docker NO existen, construirlas primero:

```bash
# Desde la carpeta padre
cd Projects/Infra-K8s
python build.py

# Verificar que se crearon
docker images | grep projects
# Debes ver: projects-api-final:latest y projects-worker-final:latest
```

### Windows

```bash
# 1. Configurar ruta en worker-deployment-windows.yaml (una sola vez)
# Editar líneas 41-46 con TU usuario y ruta

# 2. Ejecutar demo
cd Projects/Infra-K8s/k8s
python demo.py
```

### Mac/Linux

```bash
cd Projects/Infra-K8s/k8s
python demo.py
```

## 📂 Estructura Requerida en Windows

```
C:\Users\TU_USUARIO\...\Infra-K8s\static\
├── images\              ← Imágenes de entrada aquí
│   ├── sample.jpg
│   └── sample_4k.jpg
└── processed\           ← Imágenes procesadas van aquí
```

## ⚙️ Configuración

El `demo.py` automáticamente:
- ✅ Detecta tu plataforma (Windows/Mac/Linux)
- ✅ Usa el deployment correcto
- ✅ Configura HPA para auto-scaling (CPU target: 15%)
- ✅ Envía 100 tareas pesadas
- ✅ Monitorea escalado durante 4 minutos

## 📊 Qué Esperar

```
Workers: 1 → 2 → 4 → 6 → 8+  (escalado)
         ↓ (después de procesar)
Workers: 8 → 6 → 4 → 2 → 1  (descalado)
```

Duración: ~5-7 minutos

## 📈 Monitorear Auto-Scaling en Tiempo Real

### Ver estado del HPA
```bash
# Estado actual del HPA (réplicas, CPU%, targets)
kubectl get hpa

# Output ejemplo:
# NAME         REFERENCE              TARGETS   MINPODS  MAXPODS  REPLICAS
# worker-hpa   Deployment/worker...   45%/15%   1        10       4

# Ver en tiempo real (actualiza cada 2 segundos)
watch -n 2 kubectl get hpa

# Detalles completos del HPA
kubectl describe hpa worker-hpa
```

### Ver réplicas de workers
```bash
# Ver pods actuales
kubectl get pods -l app=image-worker

# Ver en tiempo real
kubectl get pods -l app=image-worker -w

# Contar réplicas
kubectl get deployment worker-deployment
```

### Ver métricas de CPU/Memory
```bash
# Métricas de todos los workers
kubectl top pods -l app=image-worker

# Ver en tiempo real
watch -n 2 'kubectl top pods -l app=image-worker'
```

### Ver eventos de escalado
```bash
# Ver últimos eventos de scaling
kubectl describe hpa worker-hpa | grep -A 10 Events

# Output ejemplo:
#   Normal  SuccessfulRescale  2m   HPA  New size: 4; reason: cpu > target
#   Normal  SuccessfulRescale  5m   HPA  New size: 2; reason: All metrics below target
```

### Dashboard completo (en una terminal)
```bash
# Comando combinado que muestra todo
watch -n 2 'echo "=== HPA ===" && kubectl get hpa && echo && echo "=== WORKERS ===" && kubectl get pods -l app=image-worker && echo && echo "=== METRICS ===" && kubectl top pods -l app=image-worker'
```

## 🐛 Troubleshooting

```bash
# Ver estado
kubectl get pods -n default
kubectl get hpa

# Ver logs
kubectl logs -l app=image-worker --tail=50

# Verificar volúmenes (Windows)
kubectl exec <worker-pod> -- ls -la /app/static/images/

# Ver tareas en Redis
kubectl exec deployment/redis-deployment -- redis-cli LLEN tasks:completed
```

## 📖 Más Información

Ver documentación completa en `../README.md` del proyecto.


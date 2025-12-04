# 🖼️ Kubernetes Auto-Scaling Demo

Demo de **auto-scaling automático** en Kubernetes con procesamiento distribuido de imágenes.

## 🎯 ¿Qué hace este demo?

Muestra **auto-scaling real** de workers en Kubernetes:
- 📈 **Scale UP**: Cuando hay carga, Kubernetes crea más workers automáticamente
- 📉 **Scale DOWN**: Cuando baja la carga, elimina workers gradualmente
- 📊 **Basado en métricas reales**: CPU y memoria de los pods

## 🚀 Quick Start

### 1️⃣ Construir imágenes Docker (solo primera vez)

```bash
cd Projects/Infra-K8s
python build.py

# Verificar que se crearon
docker images | grep projects
# Debes ver:
#   projects-api-final:latest
#   projects-worker-final:latest
```

### 2️⃣ Ejecutar el demo

**Windows:**
```bash
cd k8s
python demo.py
```

**Mac/Linux:**
```bash
cd k8s
python demo.py
```

### 3️⃣ Ver resultados

El demo muestra automáticamente durante 4 minutos:
- ✅ Pods escalando (1 → 2 → 4 → 6+)
- ✅ Métricas de CPU/Memory
- ✅ Estado del HPA
- ✅ Descalado gradual al final

## 📋 Archivos Necesarios

### Esenciales
```
Infra-K8s/
├── build.py                        # Construir imágenes (una vez)
├── k8s/
│   ├── demo.py                     # ⭐ DEMO PRINCIPAL
│   ├── redis-deployment.yaml       # Redis
│   ├── api-deployment.yaml         # API
│   ├── worker-deployment.yaml      # Workers (Mac/Linux)
│   ├── worker-deployment-windows.yaml  # Workers (Windows)
│   ├── metrics-server.yaml         # Metrics Server
│   └── README.md                   # Documentación del demo
│
├── docker/                         # Dockerfiles
├── django_image_server/            # Django API
├── image_api/                      # Endpoints
├── distributed/                    # Redis queue
├── workers/                        # Worker code
├── static/images/                  # Imágenes de entrada
└── static/processed/               # Imágenes procesadas
```

### Opcionales
- `stress_test.py` - Stress test personalizado (avanzado)

## 📚 ¿Qué es HPA?

**HPA = Horizontal Pod Autoscaler**

Ajusta automáticamente el número de pods basándose en:
- CPU utilization (uso de CPU)
- Memory utilization (uso de memoria)

**Ejemplo:**
- Min: 1 worker
- Max: 10 workers  
- Target CPU: 30%
- **Resultado**: Si CPU > 30%, Kubernetes crea más workers automáticamente

## 📊 Arquitectura

```
Cliente → API Service → Redis Queue → Workers (auto-scaling)
                                         ↓
                                        HPA
                                         ↓
                                   Metrics Server
```

## 🐛 Troubleshooting

### Demo no escala pods

```bash
# Ver estado del HPA
kubectl get hpa

# Si muestra <unknown>, instalar Metrics Server:
kubectl apply -f metrics-server.yaml

# Ver métricas de pods
kubectl top pods
```

### No se procesan imágenes (Windows)

```bash
# 1. Verificar que exista el directorio con subdirectorios
dir C:\Users\TU_USUARIO\...\Infra-K8s\static\images

# Estructura requerida:
# static/
# ├── images/       ← Imágenes aquí
# └── processed/    ← Salida aquí

# 2. Actualizar ruta en worker-deployment-windows.yaml (líneas 41-46)
# 3. Reiniciar workers
kubectl delete pod -l app=image-worker
```

### Ver logs de workers

```bash
kubectl logs -l app=image-worker --tail=50
kubectl logs -f -l app=image-worker  # Seguir en tiempo real
```

## 📖 Documentación Detallada

Ver `k8s/README.md` para:
- Monitoreo en tiempo real
- Comandos kubectl útiles
- Troubleshooting avanzado

---

**🎯 Un solo comando: `python demo.py` y funciona!** 🚀

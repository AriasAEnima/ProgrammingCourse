# 🚀 CLASE KUBERNETES - PLAN DETALLADO (45min)

## 🎯 **OBJETIVO:**
> "De Docker Compose a Kubernetes: AUTO-SCALING REAL"

---

## ⏰ **TIMELINE DETALLADO:**

### **SEGMENTO 1: K8s Intro (10min)**

#### **Min 0-3: Hook + Problem** 
```bash
# Mostrar limitación actual
docker-compose ps
# → Solo 2 workers fijos! 😤
```

**Pregunta clave:** *"¿Qué pasa si llegan 1000 requests?"*

#### **Min 3-7: K8s Core Concepts**
```
Docker Compose → Kubernetes
├── service:     → Pod (container + resources)
├── replicas: 2  → Deployment (template + scaling)  
└── ports:       → Service (load balancer)
                 → HPA (AUTO-SCALING!) ⭐
```

#### **Min 7-10: Architecture Comparison**
```
ANTES (Docker):           DESPUÉS (K8s):
┌─────────────┐          ┌──────────────┐
│ API         │          │ API Pod      │
│ Worker 1    │    →     │ Worker Pods  │ ← AUTO-SCALE!
│ Worker 2    │          │ (1-10 pods)  │
│ Redis       │          │ Redis Pod    │
└─────────────┘          └──────────────┘
```

---

### **SEGMENTO 2: Hands-On Migration (15min)**

#### **Min 10-12: Setup (Windows/Linux/Mac)**
```powershell
# Windows: 
cd k8s
minikube start
# O usar Docker Desktop → Enable Kubernetes

# Verificar conexión:
kubectl cluster-info
```

#### **Min 12-15: Deploy Redis**
```powershell
# Mostrar archivo (Windows: type, Linux/Mac: cat)
type redis-deployment.yaml

# Deploy
kubectl apply -f redis-deployment.yaml
kubectl get pods -w  # Watch creation
```

#### **Min 15-20: Deploy API**
```powershell
# Mostrar diferencias vs docker-compose
type api-deployment.yaml

kubectl apply -f api-deployment.yaml
kubectl get services
```

#### **Min 20-25: Deploy Workers + HPA**
```powershell
# ⭐ LA MAGIA: HPA
type worker-deployment.yaml

kubectl apply -f worker-deployment.yaml
kubectl get hpa  # ← ¡AUTO-SCALING CONFIG!
```

---

### **SEGMENTO 3: AUTO-SCALING DEMO (15min)**

#### **Min 25-27: Status Check**
```bash
kubectl get pods
kubectl get hpa
# Mostrar: 2/2 workers, CPU: 0%
```

#### **Min 27-32: Generate Load**
```powershell
# Port-forward para acceso local (en terminal separada)
kubectl port-forward service/api-service 8000:8000

# En otra terminal - 🔥 STRESS TEST
python ../burst_stress.py 50
```

#### **Min 32-37: Watch Magic Happen**
```powershell
# En otra terminal (Windows/Linux/Mac):
kubectl get hpa -w
kubectl get pods -w

# Estudiantes ven:
# CPU: 0% → 85% → Scaling: 2→4→6→8 pods! 🚀
```

#### **Min 37-40: Analysis**
```bash
kubectl describe hpa worker-hpa
kubectl top pods  # Resource usage
```

---

### **SEGMENTO 4: Wrap-up (5min)**

#### **Min 40-43: Key Learnings**
✅ **Docker vs K8s:** Fijo vs Dinámico
✅ **HPA:** CPU/Memory triggers  
✅ **Real Auto-scaling:** 1→10 pods automático
✅ **Production Ready:** Lo que usan Netflix, Google, etc.

#### **Min 43-45: Next Steps**
```powershell
# Cleanup (Windows/Linux/Mac)
kubectl delete -f .
minikube stop
```

**Homework:** "Agregar scaling por queue length (custom metrics)"

---

## 🛠️ **ARCHIVOS PREPARADOS:**

```
k8s/
├── api-deployment.yaml     ← API + Service
├── worker-deployment.yaml  ← Workers + HPA ⭐  
├── redis-deployment.yaml   ← Redis
├── demo.py                 ← Demo automático (Python/Cross-platform)
└── KUBERNETES_CLASS_PLAN.md ← Este plan
```

## 🎯 **COMANDOS CRÍTICOS (Windows/Linux/Mac):**

```powershell
# Setup rápido
minikube start

# Deploy todo
cd k8s
kubectl apply -f .

# Ver auto-scaling 
kubectl get hpa -w

# Generar carga (en otra terminal)
python burst_stress.py 50

# Cleanup
kubectl delete -f .
```

## 💡 **BACKUP PLANS:**

**Si K8s no funciona:**
- **Windows:** Docker Desktop → Settings → Kubernetes → Enable
- **Browser:** Play-with-Kubernetes (lab.play-with-k8s.com)
- **Fallback:** Mostrar videos de auto-scaling
- **Theory:** Focus en YAML analysis

**Si demo falla:**
- **Pre-grabado:** Video de auto-scaling real
- **Manual scaling:** `kubectl scale deployment worker-deployment --replicas=8`
- **Demo script:** `python k8s/demo.py` (step-by-step)

---

## 🏆 **RESULTADO ESPERADO:**

**Estudiantes salen sabiendo:**
1. ✅ Diferencia Docker vs K8s
2. ✅ Cómo convertir docker-compose a K8s
3. ✅ Qué es HPA y cómo configurarlo  
4. ✅ Auto-scaling REAL en acción

**"¡Por fin vimos auto-scaling de verdad!"** 🚀✨
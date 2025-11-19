# 🌐 DÍA 3 - JUEVES: "Distributed Workers + Docker"

**Duración**: 45min seguimiento + 1h autónoma | **Objetivo**: Workers locales → Workers distribuidos en containers

---

## 🎯 **OBJETIVOS DEL DÍA**

### **🧠 CONCEPTUAL:**
- Evolucionar de **workers locales** a **workers distribuidos**
- Implementar **service discovery** y **load balancing**
- Aplicar **fault tolerance** en sistemas distribuidos
- Usar **Docker** para containerización y escalabilidad

### **🛠️ TÉCNICO:**
- **Dockerizar workers** independientes
- **Redis queue** para distributed task management
- **Worker registry** con health checks
- **Horizontal scaling** automático

### **📊 MÉTRICAS DE ÉXITO:**
- **3+ workers** ejecutándose en containers separados
- **Load balancing** distribuye tareas equitativamente
- **Fault tolerance**: sistema funciona si 1 worker falla
- **<30s recovery** cuando worker se reconecta

---

## ⏰ **AGENDA - 45 MINUTOS SEGUIMIENTO**

### **🔥 WARM-UP (5 min)**
```bash
# Verificar estado actual del día 2
cd Chapter-Threads/Projects
python manage.py runserver 8000 &

# Test multiprocessing actual (baseline)
curl -X POST http://localhost:8000/api/process-batch/multiprocessing/ \
     -H "Content-Type: application/json" \
     -d '{"filters": ["sharpen"], "filter_params": {"sharpen": {"intensity": 2}}}'
```

### **⚡ IMPLEMENTACIÓN CORE (25 min)**

#### **1. Setup Redis + Docker (8 min)**
- Instalar Redis localmente
- Crear `Dockerfile.worker` para workers independientes
- Test básico de Redis connection

#### **2. Distributed Task Queue (10 min)**  
- Implementar `redis_queue.py` para distributed tasks
- Migrar workers para usar Redis en lugar de local queues
- Test de comunicación API → Redis → Workers

#### **3. Worker Registry (7 min)**
- Sistema de **service discovery** para workers
- **Health checks** automáticos cada 30s
- **Worker registration** al iniciar

### **🧪 DEMO FINAL (10 min)**
```bash
# Levantar sistema distribuido completo
docker-compose up -d

# Test con 3 workers simultáneos
curl -X POST http://localhost:8000/api/process-batch/distributed/ \
     -H "Content-Type: application/json" \
     -d '{"filters": ["sharpen", "edges"], "filter_params": {"sharpen": {"intensity": 3}, "edges": {"threshold1": 50, "threshold2": 150}}}'

# Simular fallo de worker
docker stop project_worker_2

# Verificar fault tolerance
curl -X GET http://localhost:8000/api/workers/status/
```

### **🔄 TRABAJO AUTÓNOMO (5 min)**
```
"PARA LA SIGUIENTE HORA:

1. Completar docker-compose.yml con 3 workers
2. Implementar load balancer inteligente (least-busy)
3. Health monitoring dashboard
4. Stress test con múltiples workers

¡Mañana integramos CI/CD para automatizar todo!"
```

---

## ⏰ **CRONOGRAMA DETALLADO (45 MIN)**

### **📚 MINUTOS 0-10: REVIEW + DISTRIBUTED SETUP**

#### **Minuto 0-3: Review días anteriores**
```
"¡Buenos días! Resumen rápido:

DÍA 1: Threading para I/O-bound (resize, blur)
DÍA 2: Multiprocessing para CPU-bound (sharpen, edges)

HOY: ¿Qué pasa si necesitamos ESCALAR?
- Más throughput que un solo servidor
- Fault tolerance si un worker crashea
- Distribución geográfica de workers"
```

#### **Minuto 3-7: Plantear el problema distribuido**
```
"PROBLEMA: Un solo servidor tiene límites:
- CPU cores limitados
- Memoria limitada  
- Si el servidor falla, TODO se cae

SOLUCIÓN: Múltiples workers independientes
- Workers en containers separados
- Comunicación vía Redis (message queue)
- Load balancer distribuye trabajo"
```

#### **Minuto 7-10: Verificar estado actual + instalar Redis**
```bash
# Verificar workers locales funcionando
python -c "
from image_api.processors import ImageProcessor
processor = ImageProcessor()
print('Local workers OK:', processor.test_multiprocessing_performance is not None)
"

# Instalar Redis
# macOS: brew install redis
# Ubuntu: sudo apt install redis-server
# Windows: Via WSL o Docker

redis-cli ping  # Debe responder: PONG
```

---

### **🛠️ MINUTOS 10-25: IMPLEMENTACIÓN DISTRIBUIDA**

#### **Minuto 10-13: Crear Dockerfile para workers**
```bash
# Crear Dockerfile.worker
cat > docker/Dockerfile.worker << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "workers/distributed_worker.py"]
EOF
```

**Explicar mientras escriben:**
```
"Cada worker será un container independiente.
Ventajas:
- Aislamiento (un worker crashea, otros siguen)
- Escalabilidad (más containers = más throughput)
- Portabilidad (deploy en cualquier servidor)"
```

#### **Minuto 13-18: Implementar Redis Queue**
```python
# distributed/redis_queue.py
import redis
import json
import uuid

class DistributedTaskQueue:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def enqueue_task(self, task_data):
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'data': task_data,
            'status': 'pending',
            'created_at': time.time()
        }
        self.redis_client.lpush('image_tasks', json.dumps(task))
        return task_id
    
    def get_task(self):
        # Worker poll para tareas
        task_json = self.redis_client.brpop('image_tasks', timeout=5)
        if task_json:
            return json.loads(task_json[1])
        return None
```

**Demostrar:**
```bash
# Test Redis básico
python -c "
from distributed.redis_queue import DistributedTaskQueue
queue = DistributedTaskQueue()
task_id = queue.enqueue_task({'test': 'data'})
print('Task enqueued:', task_id)
"
```

#### **Minuto 18-22: Worker Registry + Health Checks**
```python
# distributed/worker_registry.py
class WorkerRegistry:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=1)
    
    def register_worker(self, worker_id, capabilities):
        worker_data = {
            'id': worker_id,
            'capabilities': capabilities,
            'last_heartbeat': time.time(),
            'status': 'active',
            'tasks_completed': 0
        }
        self.redis_client.hset('workers', worker_id, json.dumps(worker_data))
    
    def heartbeat(self, worker_id):
        # Worker envía heartbeat cada 30s
        worker_data = self.get_worker(worker_id)
        if worker_data:
            worker_data['last_heartbeat'] = time.time()
            self.redis_client.hset('workers', worker_id, json.dumps(worker_data))
    
    def get_active_workers(self):
        # Workers con heartbeat en últimos 60s
        current_time = time.time()
        active = []
        for worker_id, data_json in self.redis_client.hgetall('workers').items():
            data = json.loads(data_json)
            if current_time - data['last_heartbeat'] < 60:
                active.append(data)
        return active
```

#### **Minuto 22-25: Demo integración completa**
```bash
# API envía tarea a Redis
curl -X POST http://localhost:8000/api/process-batch/distributed/ \
     -H "Content-Type: application/json" \
     -d '{"filters": ["sharpen"], "filter_params": {"sharpen": {"intensity": 2}}}'

# Ver tareas en Redis
redis-cli LLEN image_tasks

# Ver workers registrados  
redis-cli HGETALL workers
```

---

### **🎯 MINUTOS 25-40: DOCKER ORCHESTRATION**

#### **Minuto 25-30: Docker Compose Setup**
```yaml
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
  
  worker-1:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    depends_on:
      - redis
    environment:
      - WORKER_ID=worker-1
      - REDIS_URL=redis://redis:6379
  
  worker-2:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    depends_on:
      - redis
    environment:
      - WORKER_ID=worker-2
      - REDIS_URL=redis://redis:6379
  
  worker-3:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    depends_on:
      - redis
    environment:
      - WORKER_ID=worker-3
      - REDIS_URL=redis://redis:6379
```

#### **Minuto 30-35: Levantar sistema distribuido**
```bash
# Build y start de todo el sistema
docker-compose up -d

# Verificar que todos los containers estén running
docker-compose ps

# Ver logs de workers
docker-compose logs worker-1
docker-compose logs worker-2
docker-compose logs worker-3
```

**Explicar:**
```
"¡Ahora tenemos un sistema VERDADERAMENTE distribuido!
- 1 Redis (message queue)
- 1 API (entry point)  
- 3 Workers (processing power)

Cada worker puede estar en un servidor diferente."
```

#### **Minuto 35-40: Test fault tolerance**
```bash
# Test normal con 3 workers
curl -X POST http://localhost:8000/api/process-batch/distributed/ \
     -H "Content-Type: application/json" \
     -d '{"filters": ["sharpen", "edges"], "filter_params": {"sharpen": {"intensity": 3}, "edges": {"threshold1": 50, "threshold2": 150}}}'

# Simular fallo de worker
docker-compose stop worker-2

# Test con worker caído
curl -X POST http://localhost:8000/api/process-batch/distributed/ \
     -H "Content-Type: application/json" \
     -d '{"filters": ["sharpen"], "filter_params": {"sharpen": {"intensity": 2}}}'

# Verificar que sistema sigue funcionando
curl http://localhost:8000/api/workers/status/

# Recuperar worker
docker-compose start worker-2
```

**Analizar resultados:**
```
"¿Qué observaron?
- Con 3 workers: distribución equitativa
- Con worker caído: otros 2 toman la carga  
- Worker recuperado: se reintegra automáticamente

¡Esto es FAULT TOLERANCE real!"
```

---

### **🚀 MINUTOS 40-45: WRAP-UP**

#### **Minuto 40-43: Síntesis y conceptos clave**
```
"CONCEPTOS CLAVE DEL DÍA:

1. ESCALABILIDAD HORIZONTAL:
   Más workers = más throughput

2. FAULT TOLERANCE:
   Sistema funciona aunque fallen componentes

3. SERVICE DISCOVERY:
   Workers se registran/des-registran automáticamente

4. MESSAGE QUEUES:
   Comunicación asíncrona y confiable

5. CONTAINERIZACIÓN:
   Aislamiento y portabilidad"
```

#### **Minuto 43-45: Preview mañana (Día 4)**
```
"MAÑANA - DÍA 4: CI/CD + DEMO FINAL

Pregunta: ¿Cómo automatizar deploy de todo este sistema?

Solución: GitHub Actions
- Build automático de containers
- Tests automatizados  
- Deploy a producción
- Rollback si algo falla

¡DEMO FINAL del proyecto completo!"
```

---

## 🎯 **COMANDOS CLAVE PARA HOY**

### **1. Levantar sistema distribuido:**
```bash
docker-compose up -d
```

### **2. Test distributed processing:**
```bash
curl -X POST http://localhost:8000/api/process-batch/distributed/ -H "Content-Type: application/json" -d '{"filters": ["sharpen", "edges"], "filter_params": {"sharpen": {"intensity": 3}, "edges": {"threshold1": 50, "threshold2": 150}}}'
```

### **3. Ver estado de workers:**
```bash
curl http://localhost:8000/api/workers/status/
```

### **4. Simular fallo de worker:**
```bash
docker-compose stop worker-2
```

### **5. Monitoring Redis:**
```bash
redis-cli LLEN image_tasks
redis-cli HGETALL workers
```

---

## 📊 **MÉTRICAS ESPERADAS HOY**

| Métrica | Valor esperado | Cómo medir |
|---------|----------------|------------|
| **Workers activos** | 3/3 | `curl /api/workers/status/` |
| **Fault tolerance** | 2/3 workers suficientes | Stop 1 worker, test continúa |
| **Load balancing** | Distribución ~33% cada worker | Logs de workers |
| **Recovery time** | <30s | Stop/start worker, medir heartbeat |

---

## 🎓 **TAKEAWAYS CLAVE**

1. **Horizontal scaling** > Vertical scaling
2. **Message queues** permiten comunicación async confiable  
3. **Service discovery** automatiza gestión de workers
4. **Containers** proporcionan aislamiento y portabilidad
5. **Fault tolerance** requiere diseño desde el inicio

**¡Hoy construimos un sistema distribuido real y resiliente!** 🚀
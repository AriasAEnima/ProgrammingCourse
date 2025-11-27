# Sesión 5: Monitoring - QUICKSTART ⚡

## ✅ Todo Verificado y Funcionando

## 🚀 Setup en 3 Pasos

### 1. Iniciar Redis
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
docker exec redis redis-cli ping  # Debe responder: PONG
```

### 2. Instalar dependencias
```bash
cd session5_monitoring
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Ejecutar demos
```bash
# Demo 1: Worker Registry con heartbeats
python demos/demo_worker_registry.py

# Demo 2: Auto-recovery y Dead Letter Queue
python demos/demo_auto_recovery.py

# Demo 3: Sistema completo (3 workers en paralelo)
python demos/demo_monitored_system.py
```

## 🎯 Qué esperar

### Demo 1 (Worker Registry)
- Registra 3 workers
- Envía heartbeats
- Detecta workers muertos
- Limpia workers inactivos

### Demo 2 (Auto-Recovery)
- Simula fallos en tareas
- Reintentos automáticos (3 máx)
- Dead Letter Queue para tareas fallidas
- Re-intento manual desde DLQ

### Demo 3 (Sistema Completo)
- 🚀 Procesa 10 imágenes con diferentes filtros
- 👷 3 workers en paralelo
- 💓 Heartbeats cada 10s
- 🛑 Graceful shutdown
- ⚡ Completado en < 1 segundo

## 🧹 Limpieza

```bash
docker stop redis && docker rm redis
deactivate  # Salir del venv
```

## 📊 Resultados Verificados

✅ Todos los demos probados y funcionando  
✅ 10 imágenes procesadas exitosamente  
✅ Workers coordinados correctamente  
✅ Reintentos automáticos operativos  
✅ Graceful shutdown funcional  

**¡Sistema 100% operativo!** 🎉


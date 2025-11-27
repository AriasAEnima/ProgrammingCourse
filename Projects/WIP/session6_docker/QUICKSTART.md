# Sesión 6: Docker y Containerización - QUICKSTART 🐳

## 🚀 Quick Start

```bash
# 1. Build e iniciar servicios
cd Projects/WIP/session6_docker
docker-compose up -d --build

# 2. Verificar que estén corriendo
docker-compose ps

# 3. Enviar tareas (requiere redis y Pillow en el host)
python3 demos/demo_send_tasks.py

# 4. Ver logs en tiempo real
docker-compose logs -f

# 5. Ejecutar test completo
python3 demos/demo_full_test.py

# 6. Detener
docker-compose down
```

## 📦 Lo que incluye

- **Redis**: Cola de tareas distribuida con persistencia
- **3 Workers**: Procesadores de imágenes en paralelo
- **Multi-stage Dockerfile**: Imágenes optimizadas (~150MB)
- **Health checks**: Monitoreo automático de servicios
- **3 Demos**: send_tasks, monitor, full_test

## 🎯 Resultados Esperados

Test completo: **10 imágenes procesadas en ~0.5 segundos** ⚡

Ver `README.md` completo para documentación detallada.


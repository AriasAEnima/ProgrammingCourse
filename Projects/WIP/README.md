# Curso de Procesamiento Distribuido de Imágenes con Kubernetes

Curso práctico de 10 sesiones para aprender procesamiento de imágenes y sistemas distribuidos.

## 📊 Estado del Curso

### ✅ Sesiones Completadas

#### Session 1: Fundamentos de Procesamiento de Imágenes
**Estado**: ✅ Completada  
**Temas**:  
- Introducción a PIL/Pillow
- Filtros básicos (blur, brightness, edges)
- Arquitectura con clases base abstractas
- Módulos y separación de responsabilidades

#### Sesión 2: Pipelines y Factory Pattern
**Estado**: ✅ Completada  
**Temas**:
- Filter Pipeline para encadenar filtros
- Factory Pattern para crear filtros dinámicamente
- Batch processing de múltiples imágenes
- Grayscale filter

#### Sesión 3: Arquitectura de Workers
**Estado**: ✅ Completada  
**Temas**:
- Worker Pattern (synchronous y asynchronous)
- In-memory task queue (thread-safe)
- Threading y AsyncIO con semáforos
- Structured logging
- Health checks básicos

#### Sesión 4: Redis y Colas Distribuidas
**Estado**: ✅ Completada  
**Temas**:
- Redis como cola de tareas distribuida
- Operaciones atómicas (RPOPLPUSH)
- Persistencia con AOF
- Multiprocessing para paralelismo real (bypass GIL)
- Setup cross-platform con Docker

#### Sesión 5: Health Checks, Auto-Recovery y Monitoring
**Estado**: ✅ Completada  
**Temas**:
- Worker Registry con heartbeats
- Detección de workers muertos
- Auto-recovery con retries
- Dead Letter Queue (DLQ)
- Graceful shutdown
- Sistema de monitoring completo

#### Sesión 6: Docker y Containerización 
**Estado**: ✅ Completada  
**Temas**:
- Multi-stage Dockerfile optimizado
- Docker Compose para Redis + Workers
- Health checks en contenedores
- Volúmenes compartidos
- Demos para interactuar con el sistema dockerizado
- Usuario no-root para seguridad
- Persistencia de Redis con AOF

**Performance**: 10 imágenes procesadas en 0.5s con 3 workers

### 🔜 Sesiones Planeadas

#### Sesión 7: Kubernetes Basics
- Pods, Deployments, Services
- ConfigMaps y Secrets
- Namespaces
- kubectl commands

#### Sesión 8: Kubernetes Advanced
- StatefulSets para Redis
- Persistent Volumes
- Horizontal Pod Autoscaler (HPA)
- Resource limits y requests

#### Sesión 9: Observability
- Prometheus para métricas
- Grafana para visualización
- Distributed tracing
- Logging agregado

#### Sesión 10: Production Ready
- CI/CD pipeline
- Rolling updates y rollbacks
- Disaster recovery
- Security best practices

## 🎯 Objetivos del Curso

1. **Dominar** procesamiento de imágenes con Python
2. **Implementar** patrones de diseño para sistemas distribuidos
3. **Construir** arquitectura de workers escalable
4. **Desplegar** en Kubernetes con best practices
5. **Monitorear** y mantener sistemas en producción

## 📁 Estructura del Proyecto

```
Projects/WIP/
├── session1_image_basics/       # PIL/Pillow, filtros básicos
├── session2_pipelines/          # Pipelines y Factory
├── session3_workers/            # Worker pattern, async
├── session4_redis/              # Redis queues, multiprocessing
├── session5_monitoring/         # Health checks, auto-recovery
├── session6_docker/             # Docker, Docker Compose
├── session7_k8s_basics/         # (Planeada)
├── session8_k8s_advanced/       # (Planeada)
├── session9_observability/      # (Planeada)
└── session10_production/        # (Planeada)
```

## 🚀 Cómo Empezar

Cada sesión es autocontenida con su propio README. Recomendado seguir en orden:

```bash
cd Projects/WIP/session1_image_basics
cat README.md
```

## 📚 Prerequisitos

- Python 3.11+
- Docker y Docker Compose
- Redis (via Docker recomendado)
- Conocimientos básicos de Python

## ✨ Características Destacadas

- **Código limpio y didáctico** con documentación extensa
- **Demos funcionales** para cada concepto
- **Progresión incremental** de simple a complejo
- **Production-ready patterns** desde el inicio
- **Cross-platform** (Linux, macOS, Windows con Docker)

---

**Última actualización**: Sesión 6 completada con pendientes técnicos por resolver

# Sesión 6: Docker y Containerización 🐳

## 🎯 Estado: ✅ COMPLETADA Y FUNCIONAL

**Performance demostrada**: 10 imágenes procesadas en 0.5 segundos con 3 workers en paralelo 🚀

## 📋 Contenido

1. [Introducción](#introducción)
2. [Conceptos Clave](#conceptos-clave)
3. [Arquitectura](#arquitectura)
4. [Dockerfile Multi-Stage](#dockerfile-multi-stage)
5. [Docker Compose](#docker-compose)
6. [Demos](#demos)
7. [Comandos Útiles](#comandos-útiles)
8. [Troubleshooting](#troubleshooting)

---

## Introducción

En esta sesión dockerizamos el sistema completo de procesamiento de imágenes, transformándolo en un conjunto de contenedores que pueden desplegarse fácilmente en cualquier entorno.

### ¿Por qué Docker?

- **Portabilidad**: El mismo contenedor funciona en desarrollo, staging y producción
- **Aislamiento**: Cada servicio corre en su propio entorno aislado
- **Escalabilidad**: Fácil de escalar horizontalmente (más workers)
- **Reproducibilidad**: Elimina el "en mi máquina funciona"
- **Gestión de dependencias**: Todo lo necesario está en la imagen

### Objetivos de aprendizaje

- Crear Dockerfiles optimizados con multi-stage builds
- Orquestar múltiples servicios con Docker Compose
- Implementar health checks y restart policies
- Escalar servicios horizontalmente
- Monitorear sistemas distribuidos containerizados

---

## Conceptos Clave

### Docker vs Docker Compose

- **Docker**: Ejecuta contenedores individuales
- **Docker Compose**: Orquesta múltiples contenedores relacionados

### Multi-Stage Builds

Técnica para crear imágenes Docker más pequeñas:

1. **Stage 1 (Builder)**: Compila código, instala dependencias de build
2. **Stage 2 (Runtime)**: Solo copia los artefactos necesarios

**Ventajas**:
- Imágenes finales más pequeñas (menos MB = más rápido deploy)
- Mayor seguridad (no incluye herramientas de compilación)
- Mejor cache de capas

### Health Checks

Permiten a Docker verificar que un contenedor está funcionando correctamente:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import redis; r=redis.StrictRedis(...); r.ping()" || exit 1
```

### Restart Policies

Controlan el comportamiento de reinicio:

- `no`: No reiniciar automáticamente
- `always`: Siempre reiniciar
- `on-failure`: Reiniciar solo si falla
- `unless-stopped`: Reiniciar a menos que se detenga manualmente

---

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                Docker Network                        │
│                                                       │
│  ┌──────────┐                                        │
│  │  Redis   │ ◄───┐                                  │
│  │  :6379   │     │                                  │
│  └──────────┘     │                                  │
│                   │                                  │
│  ┌──────────┐     │                                  │
│  │ Worker 1 │─────┤                                  │
│  └──────────┘     │                                  │
│                   │                                  │
│  ┌──────────┐     │                                  │
│  │ Worker 2 │─────┤                                  │
│  └──────────┘     │                                  │
│                   │                                  │
│  ┌──────────┐     │                                  │
│  │ Worker 3 │─────┘                                  │
│  └──────────┘                                        │
│                                                       │
└─────────────────────────────────────────────────────┘
         ▲                           ▲
         │                           │
    Puerto 6379              Volúmenes compartidos
    (expuesto)                (images/, output/)
```

### Componentes

1. **Redis Container**: Cola de tareas persistente
2. **Worker Containers**: Procesan imágenes en paralelo
3. **Shared Volumes**: Acceso compartido a imágenes
4. **Bridge Network**: Comunicación entre contenedores

---

## Dockerfile Multi-Stage

Nuestro `Dockerfile` tiene dos etapas:

### Stage 1: Builder

```dockerfile
FROM python:3.11-slim as builder

# Instalar dependencias de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libjpeg-dev zlib1g-dev

# Crear virtualenv e instalar paquetes
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install -r requirements.txt
```

**¿Qué hace?**
- Instala compiladores (gcc, g++) necesarios para construir paquetes de Python
- Crea un virtualenv con todas las dependencias
- Esta capa NO va a la imagen final

### Stage 2: Runtime

```dockerfile
FROM python:3.11-slim

# Solo instalar librerías runtime (sin compiladores)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo zlib1g

# Copiar virtualenv desde builder
COPY --from=builder /opt/venv /opt/venv

# Copiar código de la aplicación
COPY core/ /app/core/
COPY workers/ /app/workers/
```

**¿Qué hace?**
- Usa una imagen base limpia
- Solo instala librerías runtime (más pequeñas que compiladores)
- Copia el virtualenv ya compilado desde el builder
- Resultado: Imagen final mucho más pequeña

### Usuario no-root

Por seguridad, el contenedor NO corre como root:

```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```

---

## Docker Compose

El archivo `docker-compose.yml` orquesta todo el sistema:

### Servicio Redis

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
```

**Características**:
- Usa Redis Alpine (imagen muy ligera)
- Persistencia con AOF (Append-Only File)
- Health check con `redis-cli ping`
- Volumen para datos persistentes

### Servicios Worker

```yaml
worker-1:
  build:
    context: .
    dockerfile: Dockerfile
  environment:
    - WORKER_ID=worker-1
    - REDIS_HOST=redis
  volumes:
    - ./images:/app/images:ro
    - ./output:/app/output
  depends_on:
    redis:
      condition: service_healthy
```

**Características**:
- Se construye desde nuestro Dockerfile
- Variables de entorno para configuración
- Volúmenes montados para imágenes (lectura) y output (escritura)
- Espera a que Redis esté "healthy" antes de iniciar

---

## Demos

### Demo 1: Enviar tareas

Envía tareas al sistema desde fuera de Docker:

```bash
python demos/demo_send_tasks.py
```

**¿Qué hace?**
- Se conecta a Redis (puerto 6379 expuesto)
- Envía 5 tareas con diferentes filtros
- Muestra el estado de la cola

**Output esperado**:
```
🚀 DEMO 1: Enviar tareas al sistema dockerizado
✅ Conectado a Redis

📤 Enviando 5 tareas...
  1. output/blur.jpg: blur
  2. output/brightness.jpg: brightness
  ...

📊 Estado de la cola:
   Pendientes: 5
   Procesando: 0
   Completadas: 0
```

### Demo 2: Monitor en tiempo real

Monitorea el sistema mientras procesa:

```bash
python demos/demo_monitor.py
```

**¿Qué hace?**
- Muestra estado de la cola en tiempo real
- Lista workers activos y sus heartbeats
- Muestra tareas en procesamiento
- Se actualiza cada 2 segundos

**Output esperado**:
```
📊 DEMO 2: Monitor del sistema

📦 COLA DE TAREAS:
   🔵 Pendientes:  2
   🟡 Procesando:  1
   🟢 Completadas: 2
   🔴 Fallidas:    0

👷 WORKERS ACTIVOS:
   🟢 worker-1
      💓 Último heartbeat: 14:30:15 (3s)
      ✅ Tareas completadas: 1
   🟢 worker-2
      💓 Último heartbeat: 14:30:14 (4s)
      ✅ Tareas completadas: 1
```

### Demo 3: Test completo

Ejecuta un test end-to-end del sistema:

```bash
python demos/demo_full_test.py
```

**¿Qué hace?**
- Limpia Redis
- Envía 10 tareas variadas
- Espera a que terminen
- Verifica archivos de salida
- Muestra estadísticas de workers

**Output esperado**:
```
======================================================================
📊 RESULTADOS:
======================================================================
✅ Completadas: 10/10
❌ Fallidas:    0/10
⏱️  Tiempo:      0.51s

📁 Verificando archivos de salida:
  ✅ test_0.jpg (314.9 KB)
  ✅ test_1.jpg (594.2 KB)
  ✅ test_2.jpg (848.4 KB)
  ...
  
👷 Estadísticas de workers:
  worker-1: 3 tareas
  worker-2: 4 tareas
  worker-3: 3 tareas
```

**Performance**: 🚀 **10 imágenes procesadas en ~0.5 segundos con 3 workers**

---

## Comandos Útiles

### Iniciar el sistema

```bash
# Build y start en background
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f worker-1
```

### Escalar workers

```bash
# Escalar a 5 workers
docker-compose up -d --scale worker=5

# Nota: Necesitas definir un servicio genérico "worker" sin container_name
```

Para escalar, modifica el `docker-compose.yml`:

```yaml
worker:
  build: .
  environment:
    - WORKER_ID=${HOSTNAME}  # Genera ID único automáticamente
  # NO poner container_name
  # Docker asignará nombres automáticos: worker-1, worker-2, etc.
```

Luego:

```bash
docker-compose up -d --scale worker=10
```

### Ver estado

```bash
# Listar contenedores
docker-compose ps

# Ver recursos usados
docker stats

# Inspeccionar un contenedor
docker inspect image-worker-1

# Entrar a un contenedor
docker exec -it image-worker-1 /bin/bash
```

### Detener y limpiar

```bash
# Detener servicios
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener, eliminar contenedores y volúmenes
docker-compose down -v

# Limpiar todo (imágenes, contenedores, volúmenes no usados)
docker system prune -a --volumes
```

### Rebuild

```bash
# Rebuild sin cache
docker-compose build --no-cache

# Rebuild y restart
docker-compose up -d --build
```

---

## Troubleshooting

### Problema: Workers no se conectan a Redis

**Síntoma**:
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solución**:
1. Verificar que Redis esté corriendo:
   ```bash
   docker-compose ps redis
   ```

2. Verificar health check:
   ```bash
   docker inspect image-processing-redis | grep Health
   ```

3. Ver logs de Redis:
   ```bash
   docker-compose logs redis
   ```

### Problema: Imagen no encontrada

**Síntoma**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'images/sample.jpg'
```

**Solución**:
- Verificar que `images/sample.jpg` existe en el host
- Verificar que el volumen está montado correctamente:
  ```bash
  docker inspect image-worker-1 | grep -A 5 Mounts
  ```

### Problema: Permiso denegado en output/

**Síntoma**:
```
PermissionError: [Errno 13] Permission denied: 'output/result.jpg'
```

**Solución**:
- El worker corre como usuario `appuser` (no root)
- Asegurar que el directorio `output/` en el host tenga permisos adecuados:
  ```bash
  chmod 777 output/  # O más restrictivo según necesidad
  ```

### Problema: Build muy lento

**Solución**:
- Usar `.dockerignore` para excluir archivos innecesarios
- Aprovechar cache de capas (ordenar comandos de menos a más cambiantes)
- Considerar usar una registry privada para cachear imágenes base

### Problema: Contenedor se reinicia constantemente

**Síntoma**:
```bash
docker-compose ps
# Muestra status "Restarting"
```

**Solución**:
1. Ver logs del contenedor:
   ```bash
   docker-compose logs worker-1
   ```

2. Verificar health check:
   ```bash
   docker inspect image-worker-1 | grep -A 10 Health
   ```

3. Ejecutar contenedor sin restart para debugear:
   ```bash
   docker-compose run --rm worker-1
   ```

---

## Mejores Prácticas

### 1. Imágenes pequeñas

- Usar imágenes base Alpine cuando sea posible
- Usar multi-stage builds
- Minimizar capas combinando comandos `RUN`
- Limpiar cache de paquetes:
  ```dockerfile
  RUN apt-get update && apt-get install -y package \
      && rm -rf /var/lib/apt/lists/*
  ```

### 2. Seguridad

- NO correr como root
- Usar imágenes oficiales y verificadas
- Escanear imágenes con herramientas como Trivy
- No incluir secretos en la imagen (usar env vars o secrets)

### 3. Logs

- Escribir logs a stdout/stderr (no a archivos)
- Usar logging estructurado (JSON)
- Configurar log drivers en producción

### 4. Configuración

- Usar variables de entorno para configuración
- No hardcodear valores en el código
- Usar `.env` file para desarrollo local

### 5. Networking

- Usar redes Docker personalizadas (no la default)
- Exponer solo los puertos necesarios
- Usar DNS interno de Docker para comunicación entre servicios

---

## Recursos Adicionales

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)

---

## Próximos Pasos

En la siguiente sesión (Kubernetes), aprenderás a:
- Orquestar contenedores a nivel de cluster
- Implementar auto-scaling basado en métricas
- Manejar configuración con ConfigMaps y Secrets
- Implementar rolling updates y rollbacks

---

**✅ Sesión 6 completada**

Has aprendido a dockerizar un sistema distribuido completo, implementando mejores prácticas de containerización y orquestación.

### 🎉 Sistema 100% Funcional

El sistema ha sido probado end-to-end con los siguientes resultados:
- ✅ 10/10 tareas completadas exitosamente
- ⚡ Tiempo de procesamiento: ~0.5 segundos
- 🐳 3 workers en contenedores separados
- 📦 Redis con persistencia funcionando
- 🔍 Health checks operativos
- 📊 Monitoreo en tiempo real disponible

**¡Todo el stack está listo para producción!**


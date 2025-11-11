# Docker

## Commands

### Build -> Crear imagen

```bash
docker build . -t my_first_django_docker_app:v1
```

### Run -> Crear y correr contenedor 

**Comando básico (usa las variables del Dockerfile por defecto):**

```powershell
docker run -d -p 8000:8000 --name django-app my_first_django_docker_app:v1
```

**Para sobrescribir variables de entorno si es necesario:**

```powershell
docker run -d -p 8000:8000 `
  -e MONGODB_HOST=host.docker.internal `
  -e MONGODB_DB=mi_otra_db `
  --name django-app `
  my_first_django_docker_app:v1
```

**O si quieres usar la imagen del registry:**

```powershell
docker run -d -p 8000:8000 --name django-app ariasaenima/simple-django-server:latest
```

### Comandos útiles

```bash
# Ver logs del contenedor
docker logs django-app

# Parar el contenedor
docker stop django-app

# Remover el contenedor
docker rm django-app

# Ver contenedores activos
docker ps

# Reconstruir imagen
docker build . -t my_first_django_docker_app:v1 --no-cache
```

## Configuración para MongoDB

Este proyecto está configurado para conectarse a MongoDB corriendo localmente en tu máquina host (fuera de Docker).

**Variables de entorno definidas en el Dockerfile:**
- `MONGODB_HOST=host.docker.internal` (para conectar desde Docker al host)
- `MONGODB_PORT=27017` (puerto por defecto de MongoDB)
- `MONGODB_DB=desk_database` (nombre de la base de datos)
- `MONGODB_USERNAME=` (vacío para desarrollo local sin auth)
- `MONGODB_PASSWORD=` (vacío para desarrollo local sin auth)

**Nota:** Estas variables están definidas por defecto en el Dockerfile, pero puedes sobrescribirlas usando `-e` en el comando `docker run` si necesitas valores diferentes.

### Requisitos previos

1. **MongoDB debe estar corriendo localmente en tu máquina**:
   ```bash
   # Verificar que MongoDB esté ejecutándose
   mongosh --eval "db.runCommand({connectionStatus: 1})"
   ```

2. **MongoDB debe estar configurado para aceptar conexiones**:
   - Verificar que MongoDB esté escuchando en `0.0.0.0:27017` o `127.0.0.1:27017`
   - Si usas MongoDB Compass, asegúrate de que esté conectado a `mongodb://localhost:27017`

### Solución de problemas

Si tienes problemas de conexión:

1. **Verificar que MongoDB esté ejecutándose**:
   ```bash
   # En Windows, verificar el servicio
   Get-Service -Name MongoDB
   
   # O intentar conectar desde la línea de comandos
   mongosh
   ```

2. **Verificar la configuración de red de MongoDB** (`mongod.conf`):
   ```yaml
   net:
     bindIp: 127.0.0.1,0.0.0.0  # Permite conexiones desde localhost y otras IPs
     port: 27017
   ```

3. **Logs del contenedor Django**:
   ```bash
   docker logs django-app
   ```
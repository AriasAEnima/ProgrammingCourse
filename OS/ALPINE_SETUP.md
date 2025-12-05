# 🏔️ Configuración para Alpine Linux

Alpine Linux es una distribución minimalista muy común en contenedores Docker. Requiere configuración específica para los scripts de este capítulo.

## 🔧 Configuración Inicial

### 1. Instalar Herramientas Básicas
```bash
# Actualizar repositorios
apk update

# Instalar bash (requerido para algunos scripts)
apk add bash

# Instalar herramientas útiles
apk add coreutils findutils grep sed gawk curl git

# Para desarrollo/debugging
apk add nano vim less tree

# Para systemd timers (si está disponible)
apk add systemd
```

### 2. Cambiar Shell por Defecto (Opcional)
```bash
# Ver shells disponibles
cat /etc/shells

# Cambiar a bash para el usuario actual
chsh -s /bin/bash

# O usar bash explícitamente
bash
```

## 🐚 Diferencias Importantes de Alpine

### Shell por Defecto
- **Alpine**: BusyBox ash (`/bin/sh`)
- **Otros**: bash (`/bin/bash`)

### Comandos Limitados
Alpine usa **BusyBox** que tiene versiones limitadas de comandos estándar:

| Comando | Alpine (BusyBox) | Completo |
|---------|------------------|----------|
| `find` | Limitado | `apk add findutils` |
| `grep` | Básico | `apk add grep` |
| `sed` | Básico | `apk add sed` |
| `awk` | No incluido | `apk add gawk` |
| `ps` | Limitado | `apk add procps` |

### Sistema de Servicios
- **Alpine**: OpenRC (no systemd)
- **Otros**: systemd

## 📝 Ajustes para Scripts

### 1. Shebang Compatible
```bash
#!/bin/sh                    # ✅ Siempre disponible
#!/bin/bash                  # ❌ Requiere instalación
```

### 2. Sintaxis Compatible
```bash
# ✅ Compatible con Alpine
VAR=`comando`               # Substitución tradicional
[ -f archivo ]              # Tests POSIX

# ❌ Puede no funcionar
VAR=$(comando)              # Requiere bash
[[ -f archivo ]]            # Extensión bash
```

### 3. Comandos Alternativos
```bash
# Verificar si comando existe antes de usar
if command -v bash >/dev/null; then
    bash script.sh
else
    sh script.sh
fi

# Usar alternativas BusyBox
ps aux                      # En lugar de ps -ef
du -sh                      # En lugar de du -h
```

## 🔄 Servicios en Alpine (OpenRC)

### Comandos Básicos
```bash
# Listar servicios
rc-status

# Iniciar servicio
rc-service nombre start

# Habilitar servicio
rc-update add nombre default

# Estado de servicio
rc-service nombre status
```

### Cron en Alpine
```bash
# Instalar cron
apk add dcron

# Habilitar cron
rc-update add dcron default
rc-service dcron start

# Usar crontab normalmente
crontab -e
```

## 🐳 Contexto Docker

Si estás en un contenedor Alpine:

### Dockerfile Típico
```dockerfile
FROM alpine:latest

# Instalar herramientas
RUN apk update && apk add --no-cache \
    bash \
    coreutils \
    findutils \
    grep \
    sed \
    curl

# Copiar scripts
COPY scripts/ /opt/scripts/
RUN chmod +x /opt/scripts/*.sh

# Usar bash por defecto
CMD ["/bin/bash"]
```

### Variables de Entorno
```bash
# Añadir al .profile o .bashrc
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export EDITOR=nano
export PAGER=less
```

## 🛠️ Scripts Adaptados para Alpine

### Script de Instalación Automática
```bash
#!/bin/sh
# setup_alpine.sh - Configurar Alpine para Chapter-OS

echo "🏔️ Configurando Alpine Linux para Chapter-OS..."

# Actualizar sistema
apk update

# Instalar herramientas esenciales
apk add --no-cache \
    bash \
    coreutils \
    findutils \
    grep \
    sed \
    gawk \
    curl \
    git \
    nano \
    tree \
    dcron

# Configurar cron
rc-update add dcron default 2>/dev/null || true
rc-service dcron start 2>/dev/null || true

# Crear enlace para compatibility
ln -sf /bin/bash /usr/local/bin/bash 2>/dev/null || true

echo "✅ Alpine configurado correctamente"
echo "💡 Tip: Ejecuta 'bash' para cambiar al shell bash"
```

## 🔍 Diagnóstico de Alpine

### Verificar Sistema
```bash
# Versión de Alpine
cat /etc/alpine-release

# Repositorios configurados
cat /etc/apk/repositories

# Paquetes instalados
apk list --installed

# Servicios disponibles
rc-status --list
```

### Solución de Problemas
```bash
# Si un script falla, verificar:
1. ¿Está bash instalado?
   which bash || apk add bash

2. ¿Están los comandos disponibles?
   which find || apk add findutils
   which grep || apk add grep

3. ¿Es compatible el shebang?
   head -1 script.sh

4. ¿Funciona con sh?
   sh script.sh
```

## 📚 Recursos Específicos

- [Alpine Linux Wiki](https://wiki.alpinelinux.org/)
- [Alpine Packages](https://pkgs.alpinelinux.org/)
- [BusyBox Commands](https://busybox.net/downloads/BusyBox.html)
- [OpenRC Documentation](https://github.com/OpenRC/openrc)

---

**Nota**: Si prefieres un entorno más estándar, considera usar Ubuntu o Debian en lugar de Alpine para desarrollo.

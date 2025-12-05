#!/bin/sh

# Script de Configuracion para Alpine Linux
# Descripcion: Configura Alpine Linux para ejecutar los scripts de Chapter-OS
# Uso: ./setup_alpine.sh

SCRIPT_NAME=$(basename "$0")

# Colores (compatibles con sh basico)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funcion de logging simple
log() {
    local level="$1"
    shift
    local message="$*"
    
    case "$level" in
        INFO)
            printf "${BLUE}[INFO]${NC} %s\n" "$message"
            ;;
        SUCCESS)
            printf "${GREEN}[SUCCESS]${NC} %s\n" "$message"
            ;;
        WARNING)
            printf "${YELLOW}[WARNING]${NC} %s\n" "$message"
            ;;
        ERROR)
            printf "${RED}[ERROR]${NC} %s\n" "$message" >&2
            ;;
        HEADER)
            printf "\n${CYAN}=== %s ===${NC}\n" "$message"
            ;;
    esac
}

# Verificar si estamos en Alpine
check_alpine() {
    if [ ! -f /etc/alpine-release ]; then
        log ERROR "Este script es solo para Alpine Linux"
        log INFO "Sistema detectado: $(uname -a)"
        exit 1
    fi
    
    local version=$(cat /etc/alpine-release)
    log SUCCESS "Alpine Linux detectado: v$version"
}

# Verificar permisos
check_permissions() {
    if [ "$(id -u)" -ne 0 ]; then
        log WARNING "No tienes permisos de root"
        log INFO "Algunas instalaciones pueden fallar"
        log INFO "Ejecuta: sudo $0"
        read -p "¿Continuar sin sudo? (y/N): " continue_without_sudo
        if [ "$continue_without_sudo" != "y" ] && [ "$continue_without_sudo" != "Y" ]; then
            exit 1
        fi
    else
        log SUCCESS "Ejecutando con permisos de root"
    fi
}

# Actualizar repositorios
update_repositories() {
    log HEADER "Actualizando Repositorios"
    
    if apk update; then
        log SUCCESS "Repositorios actualizados"
    else
        log ERROR "Error al actualizar repositorios"
        return 1
    fi
}

# Instalar herramientas esenciales
install_essential_tools() {
    log HEADER "Instalando Herramientas Esenciales"
    
    local packages="bash coreutils findutils grep sed gawk curl git nano tree"
    
    log INFO "Instalando: $packages"
    
    if apk add --no-cache $packages; then
        log SUCCESS "Herramientas esenciales instaladas"
    else
        log ERROR "Error al instalar algunas herramientas"
        return 1
    fi
    
    # Verificar instalaciones
    log INFO "Verificando instalaciones:"
    for cmd in bash find grep sed awk curl git nano tree; do
        if command -v "$cmd" >/dev/null 2>&1; then
            log SUCCESS "  $cmd instalado"
        else
            log WARNING "  $cmd no disponible"
        fi
    done
}

# Configurar cron
setup_cron() {
    log HEADER "Configurando Cron"
    
    # Instalar dcron
    if apk add --no-cache dcron; then
        log SUCCESS "dcron instalado"
    else
        log ERROR "Error al instalar dcron"
        return 1
    fi
    
    # Habilitar servicio (solo si tenemos permisos)
    if [ "$(id -u)" -eq 0 ]; then
        if rc-update add dcron default; then
            log SUCCESS "dcron habilitado para el inicio"
        fi
        
        if rc-service dcron start; then
            log SUCCESS "dcron iniciado"
        fi
    else
        log WARNING "Sin permisos de root - dcron no se puede habilitar automáticamente"
        log INFO "Ejecuta manualmente:"
        log INFO "  sudo rc-update add dcron default"
        log INFO "  sudo rc-service dcron start"
    fi
}

# Crear enlaces de compatibilidad
create_compatibility_links() {
    log HEADER "Creando Enlaces de Compatibilidad"
    
    # Crear directorio si no existe
    mkdir -p /usr/local/bin 2>/dev/null || true
    
    # Enlace para bash
    if [ -f /bin/bash ] && [ ! -f /usr/local/bin/bash ]; then
        if ln -sf /bin/bash /usr/local/bin/bash 2>/dev/null; then
            log SUCCESS "Enlace creado: /usr/local/bin/bash"
        fi
    fi
}

# Configurar variables de entorno
setup_environment() {
    log HEADER "Configurando Variables de Entorno"
    
    local profile_file="$HOME/.profile"
    
    # Crear .profile si no existe
    if [ ! -f "$profile_file" ]; then
        touch "$profile_file"
    fi
    
    # Agregar configuraciones si no existen
    if ! grep -q "Chapter-OS Configuration" "$profile_file"; then
        cat >> "$profile_file" << 'EOF'

# Chapter-OS Configuration for Alpine Linux
export EDITOR=nano
export PAGER=less
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Alias útiles
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'

# Función para cambiar a bash fácilmente
tobash() {
    if command -v bash >/dev/null 2>&1; then
        exec bash
    else
        echo "bash no está instalado"
    fi
}
EOF
        log SUCCESS "Configuración agregada a $profile_file"
    else
        log INFO "Variables de entorno ya configuradas"
    fi
}

# Limpiar scripts problemáticos
fix_scripts() {
    log HEADER "Limpiando Scripts"
    
    # Buscar archivos .sh en el proyecto
    local script_count=0
    
    for script in Session*/*.sh *.sh; do
        if [ -f "$script" ]; then
            # Limpiar terminaciones de línea
            if tr -d '\r' < "$script" > "${script}.tmp" && mv "${script}.tmp" "$script"; then
                chmod +x "$script"
                script_count=$((script_count + 1))
            fi
        fi
    done
    
    if [ $script_count -gt 0 ]; then
        log SUCCESS "$script_count scripts limpiados y hechos ejecutables"
    else
        log INFO "No se encontraron scripts para limpiar"
    fi
}

# Test de funcionalidad
run_tests() {
    log HEADER "Ejecutando Pruebas"
    
    local tests_passed=0
    local tests_total=0
    
    # Test 1: bash disponible
    tests_total=$((tests_total + 1))
    if command -v bash >/dev/null 2>&1; then
        log SUCCESS "✓ bash disponible"
        tests_passed=$((tests_passed + 1))
    else
        log ERROR "✗ bash no disponible"
    fi
    
    # Test 2: cron disponible
    tests_total=$((tests_total + 1))
    if command -v crontab >/dev/null 2>&1; then
        log SUCCESS "✓ crontab disponible"
        tests_passed=$((tests_passed + 1))
    else
        log ERROR "✗ crontab no disponible"
    fi
    
    # Test 3: herramientas básicas
    tests_total=$((tests_total + 1))
    local missing_tools=""
    for tool in find grep sed awk; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools="$missing_tools $tool"
        fi
    done
    
    if [ -z "$missing_tools" ]; then
        log SUCCESS "✓ Herramientas básicas disponibles"
        tests_passed=$((tests_passed + 1))
    else
        log ERROR "✗ Herramientas faltantes:$missing_tools"
    fi
    
    # Test 4: script de prueba
    tests_total=$((tests_total + 1))
    if [ -f "Session1-CommandLine/01_hello_command.sh" ]; then
        if sh Session1-CommandLine/01_hello_command.sh >/dev/null 2>&1; then
            log SUCCESS "✓ Scripts funcionan correctamente"
            tests_passed=$((tests_passed + 1))
        else
            log ERROR "✗ Error ejecutando scripts"
        fi
    else
        log WARNING "✓ Script de prueba no encontrado (saltando)"
        tests_passed=$((tests_passed + 1))
    fi
    
    log INFO "Pruebas completadas: $tests_passed/$tests_total pasaron"
    
    if [ $tests_passed -eq $tests_total ]; then
        return 0
    else
        return 1
    fi
}

# Mostrar resumen final
show_summary() {
    log HEADER "Resumen de Configuración"
    
    cat << EOF

${GREEN}✅ Alpine Linux configurado para Chapter-OS${NC}

${BLUE}Herramientas instaladas:${NC}
  - bash (shell avanzado)
  - coreutils (comandos estándar)
  - findutils (find, xargs)
  - grep, sed, awk (procesamiento de texto)
  - curl, git (descarga y control de versiones)
  - nano, tree (editor y visualización)
  - dcron (tareas programadas)

${BLUE}Configuración aplicada:${NC}
  - Variables de entorno en ~/.profile
  - Enlaces de compatibilidad
  - Scripts limpiados y ejecutables

${BLUE}Próximos pasos:${NC}
  1. Recarga tu perfil: source ~/.profile
  2. Cambia a bash: bash o tobash
  3. Prueba los scripts: ./Session1-CommandLine/01_hello_command.sh

${BLUE}Comandos útiles:${NC}
  tobash                    # Cambiar a bash
  apk search paquete        # Buscar paquetes
  rc-status                 # Ver servicios
  crontab -e                # Editar tareas programadas

EOF
}

# Función principal
main() {
    log HEADER "Configuración de Alpine Linux para Chapter-OS"
    
    # Verificaciones iniciales
    check_alpine
    check_permissions
    
    # Configuración paso a paso
    update_repositories || exit 1
    install_essential_tools || exit 1
    setup_cron
    create_compatibility_links
    setup_environment
    fix_scripts
    
    # Verificar que todo funciona
    if run_tests; then
        show_summary
        log SUCCESS "¡Configuración completada exitosamente!"
    else
        log WARNING "Configuración completada con algunas advertencias"
        log INFO "Revisa los errores arriba y corrige si es necesario"
    fi
}

# Ejecutar función principal
if [ "${0##*/}" = "setup_alpine.sh" ]; then
    main "$@"
fi

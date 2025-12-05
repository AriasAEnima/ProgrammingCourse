#!/bin/bash

# 🖥️ Monitor de Información del Sistema
# Descripción: Script para mostrar información detallada del sistema
# Uso: ./03_system_info.sh [opción]

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para encabezados
print_header() {
    echo -e "\n${CYAN}=====================================${NC}"
    echo -e "${YELLOW}🔍 $1${NC}"
    echo -e "${CYAN}=====================================${NC}"
}

# Información básica del sistema
show_basic_info() {
    print_header "INFORMACIÓN BÁSICA DEL SISTEMA"
    
    echo -e "${GREEN}🖥️  Sistema Operativo:${NC} $(uname -s)"
    echo -e "${GREEN}📡 Nombre del Host:${NC} $(hostname)"
    echo -e "${GREEN}👤 Usuario Actual:${NC} $(whoami)"
    echo -e "${GREEN}🏠 Directorio Home:${NC} $HOME"
    echo -e "${GREEN}⚡ Shell Actual:${NC} $SHELL"
    echo -e "${GREEN}📅 Fecha y Hora:${NC} $(date)"
    echo -e "${GREEN}⏰ Uptime:${NC} $(uptime)"
}

# Información de hardware
show_hardware_info() {
    print_header "INFORMACIÓN DE HARDWARE"
    
    echo -e "${BLUE}🔧 Arquitectura:${NC} $(uname -m)"
    echo -e "${BLUE}🧠 Procesador:${NC}"
    
    # Detectar sistema operativo para comandos específicos
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "  No disponible"
        echo -e "${BLUE}💾 Memoria Total:${NC} $(system_profiler SPHardwareDataType | grep "Memory:" | awk '{print $2 " " $3}')"
    elif [[ "$OSTYPE" == "linux"* ]]; then
        # Linux
        grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^[ \t]*//' || echo "  No disponible"
        echo -e "${BLUE}💾 Memoria Total:${NC} $(free -h | grep '^Mem:' | awk '{print $2}')"
    else
        echo "  Información no disponible para este sistema"
    fi
}

# Información de almacenamiento
show_storage_info() {
    print_header "INFORMACIÓN DE ALMACENAMIENTO"
    
    echo -e "${PURPLE}💿 Uso del Disco:${NC}"
    df -h | head -1
    df -h | grep -E '^/dev/' | head -5
    
    echo -e "\n${PURPLE}📁 Uso del Directorio Actual:${NC}"
    du -sh . 2>/dev/null || echo "  No se puede calcular"
}

# Información de red
show_network_info() {
    print_header "INFORMACIÓN DE RED"
    
    echo -e "${CYAN}🌐 Interfaces de Red:${NC}"
    
    if command -v ip >/dev/null 2>&1; then
        # Linux con ip command
        ip addr show | grep -E '^[0-9]+:' | awk '{print "  " $2}' | sed 's/:$//'
    elif command -v ifconfig >/dev/null 2>&1; then
        # macOS y otros con ifconfig
        ifconfig | grep -E '^[a-z]' | awk '{print "  " $1}' | sed 's/:$//'
    else
        echo "  Comandos de red no disponibles"
    fi
    
    echo -e "\n${CYAN}📡 IP Externa:${NC}"
    curl -s ifconfig.me 2>/dev/null || echo "  No se puede obtener (sin conexión a internet)"
}

# Información de procesos
show_process_info() {
    print_header "INFORMACIÓN DE PROCESOS"
    
    echo -e "${RED}🔥 Top 5 Procesos por CPU:${NC}"
    ps aux | sort -k3 -nr | head -6 | awk 'NR==1{print "  " $0} NR>1{printf "  %-8s %-8s %-8s %s\n", $2, $3"%", $4"%", $11}'
    
    echo -e "\n${RED}💾 Top 5 Procesos por Memoria:${NC}"
    ps aux | sort -k4 -nr | head -6 | awk 'NR==1{print "  " $0} NR>1{printf "  %-8s %-8s %-8s %s\n", $2, $3"%", $4"%", $11}'
}

# Información de variables de entorno importantes
show_environment_info() {
    print_header "VARIABLES DE ENTORNO IMPORTANTES"
    
    local important_vars=("PATH" "HOME" "USER" "SHELL" "LANG" "EDITOR" "TERM")
    
    for var in "${important_vars[@]}"; do
        if [[ -n "${!var}" ]]; then
            echo -e "${GREEN}$var:${NC} ${!var}"
        fi
    done
}

# Información completa
show_full_info() {
    echo -e "${YELLOW}🔍 Generando reporte completo del sistema...${NC}\n"
    
    show_basic_info
    show_hardware_info
    show_storage_info
    show_network_info
    show_process_info
    show_environment_info
    
    echo -e "\n${GREEN}✅ Reporte completo generado exitosamente${NC}"
}

# Función para mostrar ayuda
show_help() {
    echo "📖 Monitor de Información del Sistema"
    echo ""
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  -a, --all        Mostrar toda la información"
    echo "  -b, --basic      Información básica del sistema"
    echo "  -h, --hardware   Información de hardware"
    echo "  -s, --storage    Información de almacenamiento"
    echo "  -n, --network    Información de red"
    echo "  -p, --processes  Información de procesos"
    echo "  -e, --env        Variables de entorno"
    echo "  --help           Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0               # Información completa"
    echo "  $0 --basic       # Solo información básica"
    echo "  $0 --hardware    # Solo información de hardware"
}

# Procesamiento de argumentos
case "${1:-}" in
    -a|--all|"")
        show_full_info
        ;;
    -b|--basic)
        show_basic_info
        ;;
    -h|--hardware)
        show_hardware_info
        ;;
    -s|--storage)
        show_storage_info
        ;;
    -n|--network)
        show_network_info
        ;;
    -p|--processes)
        show_process_info
        ;;
    -e|--env)
        show_environment_info
        ;;
    --help)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Opción no reconocida: $1${NC}"
        echo -e "${YELLOW}💡 Usa '$0 --help' para ver las opciones disponibles${NC}"
        exit 1
        ;;
esac

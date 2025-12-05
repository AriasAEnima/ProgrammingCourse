#!/bin/bash

# 📁 Operaciones con Archivos
# Descripción: Script para realizar operaciones básicas con archivos y directorios
# Uso: ./02_file_operations.sh [comando] [argumentos]

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}ℹ️  INFO:${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ SUCCESS:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING:${NC} $1"
}

log_error() {
    echo -e "${RED}❌ ERROR:${NC} $1"
}

# Función para listar archivos con detalles
list_files() {
    local directory="${1:-.}"
    
    if [[ ! -d "$directory" ]]; then
        log_error "El directorio '$directory' no existe"
        return 1
    fi
    
    log_info "Listando archivos en: $directory"
    echo "============================================"
    
    # Contar archivos y directorios
    local file_count=$(find "$directory" -maxdepth 1 -type f | wc -l)
    local dir_count=$(find "$directory" -maxdepth 1 -type d | wc -l)
    dir_count=$((dir_count - 1)) # Restar el directorio actual
    
    echo "📊 Estadísticas:"
    echo "   📄 Archivos: $file_count"
    echo "   📁 Directorios: $dir_count"
    echo ""
    
    # Listar con detalles
    ls -la "$directory"
}

# Función para crear estructura de directorios
create_structure() {
    local base_dir="$1"
    
    if [[ -z "$base_dir" ]]; then
        log_error "Nombre del directorio base requerido"
        return 1
    fi
    
    log_info "Creando estructura de proyecto: $base_dir"
    
    # Crear directorios
    mkdir -p "$base_dir"/{src,docs,tests,config}
    
    # Crear archivos básicos
    touch "$base_dir/README.md"
    touch "$base_dir/.gitignore"
    touch "$base_dir/src/main.py"
    touch "$base_dir/tests/test_main.py"
    touch "$base_dir/config/settings.conf"
    
    log_success "Estructura creada exitosamente"
    tree "$base_dir" 2>/dev/null || find "$base_dir" -type d -exec echo "📁 {}" \; -o -type f -exec echo "📄 {}" \;
}

# Función para buscar archivos
search_files() {
    local pattern="$1"
    local directory="${2:-.}"
    
    if [[ -z "$pattern" ]]; then
        log_error "Patrón de búsqueda requerido"
        return 1
    fi
    
    log_info "Buscando archivos con patrón: '$pattern' en '$directory'"
    
    local results=$(find "$directory" -name "*$pattern*" -type f 2>/dev/null)
    
    if [[ -z "$results" ]]; then
        log_warning "No se encontraron archivos con el patrón '$pattern'"
        return 0
    fi
    
    echo "🔍 Resultados encontrados:"
    echo "$results" | while read -r file; do
        echo "   📄 $file"
    done
}

# Función para mostrar ayuda
show_help() {
    echo "📖 Herramienta de Operaciones con Archivos"
    echo ""
    echo "Uso: $0 [COMANDO] [ARGUMENTOS]"
    echo ""
    echo "Comandos disponibles:"
    echo "  list [directorio]           Listar archivos con estadísticas"
    echo "  create <nombre>             Crear estructura de proyecto"
    echo "  search <patrón> [directorio] Buscar archivos por patrón"
    echo "  help                        Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 list                     # Listar archivos en directorio actual"
    echo "  $0 list /home/user          # Listar archivos en directorio específico"
    echo "  $0 create mi_proyecto       # Crear estructura de proyecto"
    echo "  $0 search '.py' src/        # Buscar archivos .py en src/"
}

# Procesamiento de comandos
case "${1:-}" in
    list)
        list_files "$2"
        ;;
    create)
        create_structure "$2"
        ;;
    search)
        search_files "$2" "$3"
        ;;
    help|-h|--help)
        show_help
        ;;
    "")
        log_warning "No se especificó comando"
        show_help
        exit 1
        ;;
    *)
        log_error "Comando no reconocido: $1"
        show_help
        exit 1
        ;;
esac

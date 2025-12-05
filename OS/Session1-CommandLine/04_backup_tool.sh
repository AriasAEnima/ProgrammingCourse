#!/bin/bash

# 💾 Herramienta de Respaldo Simple
# Descripción: Script para crear respaldos de archivos y directorios
# Uso: ./04_backup_tool.sh [opciones] <origen> [destino]

# Configuración por defecto
DEFAULT_BACKUP_DIR="$HOME/backups"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
SCRIPT_NAME=$(basename "$0")

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Variables de configuración
VERBOSE=false
COMPRESS=false
EXCLUDE_PATTERNS=()
DRY_RUN=false

# Función para logging con niveles
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        INFO)
            echo -e "${BLUE}[INFO  $timestamp]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS $timestamp]${NC} $message"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARN  $timestamp]${NC} $message"
            ;;
        ERROR)
            echo -e "${RED}[ERROR $timestamp]${NC} $message"
            ;;
        DEBUG)
            if [[ "$VERBOSE" == true ]]; then
                echo -e "${PURPLE}[DEBUG $timestamp]${NC} $message"
            fi
            ;;
    esac
}

# Función para validar que el origen existe
validate_source() {
    local source="$1"
    
    if [[ ! -e "$source" ]]; then
        log ERROR "El origen '$source' no existe"
        return 1
    fi
    
    if [[ ! -r "$source" ]]; then
        log ERROR "No se tienen permisos de lectura para '$source'"
        return 1
    fi
    
    return 0
}

# Función para preparar el directorio de destino
prepare_destination() {
    local dest_dir="$1"
    
    if [[ ! -d "$dest_dir" ]]; then
        log INFO "Creando directorio de destino: $dest_dir"
        if [[ "$DRY_RUN" == false ]]; then
            mkdir -p "$dest_dir" || {
                log ERROR "No se pudo crear el directorio de destino"
                return 1
            }
        fi
    fi
    
    if [[ "$DRY_RUN" == false && ! -w "$dest_dir" ]]; then
        log ERROR "No se tienen permisos de escritura en '$dest_dir'"
        return 1
    fi
    
    return 0
}

# Función para construir el comando rsync
build_rsync_command() {
    local source="$1"
    local destination="$2"
    local cmd="rsync -av"
    
    # Agregar opciones según configuración
    if [[ "$VERBOSE" == true ]]; then
        cmd="$cmd --progress"
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        cmd="$cmd --dry-run"
    fi
    
    # Agregar patrones de exclusión
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        cmd="$cmd --exclude='$pattern'"
    done
    
    cmd="$cmd '$source' '$destination'"
    echo "$cmd"
}

# Función principal de respaldo
create_backup() {
    local source="$1"
    local dest_base="$2"
    
    # Validar origen
    validate_source "$source" || return 1
    
    # Preparar nombre del respaldo
    local source_name=$(basename "$source")
    local backup_name="${source_name}_backup_${TIMESTAMP}"
    local destination="$dest_base/$backup_name"
    
    log INFO "Iniciando respaldo de '$source'"
    log INFO "Destino: $destination"
    
    # Preparar directorio de destino
    prepare_destination "$dest_base" || return 1
    
    # Construir y ejecutar comando
    local rsync_cmd=$(build_rsync_command "$source" "$destination")
    log DEBUG "Comando rsync: $rsync_cmd"
    
    if [[ "$DRY_RUN" == true ]]; then
        log INFO "SIMULACIÓN - No se realizarán cambios reales"
    fi
    
    # Ejecutar respaldo
    log INFO "Ejecutando respaldo..."
    eval "$rsync_cmd"
    local rsync_exit_code=$?
    
    if [[ $rsync_exit_code -eq 0 ]]; then
        if [[ "$DRY_RUN" == false ]]; then
            log SUCCESS "Respaldo completado exitosamente: $destination"
            
            # Comprimir si se solicitó
            if [[ "$COMPRESS" == true ]]; then
                compress_backup "$destination"
            fi
            
            # Mostrar estadísticas
            show_backup_stats "$destination"
        else
            log SUCCESS "Simulación completada exitosamente"
        fi
    else
        log ERROR "Error durante el respaldo (código de salida: $rsync_exit_code)"
        return 1
    fi
}

# Función para comprimir respaldo
compress_backup() {
    local backup_path="$1"
    local compressed_file="${backup_path}.tar.gz"
    
    log INFO "Comprimiendo respaldo..."
    tar -czf "$compressed_file" -C "$(dirname "$backup_path")" "$(basename "$backup_path")" && {
        rm -rf "$backup_path"
        log SUCCESS "Respaldo comprimido: $compressed_file"
    } || {
        log ERROR "Error al comprimir el respaldo"
    }
}

# Función para mostrar estadísticas del respaldo
show_backup_stats() {
    local backup_path="$1"
    
    if [[ -d "$backup_path" ]]; then
        local size=$(du -sh "$backup_path" | cut -f1)
        local file_count=$(find "$backup_path" -type f | wc -l)
        local dir_count=$(find "$backup_path" -type d | wc -l)
        
        log INFO "Estadísticas del respaldo:"
        log INFO "  📊 Tamaño total: $size"
        log INFO "  📄 Archivos: $file_count"
        log INFO "  📁 Directorios: $dir_count"
    fi
}

# Función para listar respaldos existentes
list_backups() {
    local backup_dir="${1:-$DEFAULT_BACKUP_DIR}"
    
    if [[ ! -d "$backup_dir" ]]; then
        log WARNING "El directorio de respaldos '$backup_dir' no existe"
        return 1
    fi
    
    log INFO "Respaldos en '$backup_dir':"
    echo ""
    
    local backups=$(find "$backup_dir" -maxdepth 1 -name "*backup*" \( -type d -o -name "*.tar.gz" \) | sort)
    
    if [[ -z "$backups" ]]; then
        log WARNING "No se encontraron respaldos"
        return 0
    fi
    
    echo "$backups" | while read -r backup; do
        local name=$(basename "$backup")
        local size=$(du -sh "$backup" 2>/dev/null | cut -f1)
        local date=$(stat -c '%y' "$backup" 2>/dev/null || stat -f '%Sm' "$backup" 2>/dev/null)
        
        echo -e "  📦 ${GREEN}$name${NC}"
        echo -e "     💾 Tamaño: $size"
        echo -e "     📅 Fecha: $date"
        echo ""
    done
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
💾 Herramienta de Respaldo Simple

Uso: $SCRIPT_NAME [OPCIONES] <origen> [destino]

ARGUMENTOS:
  origen          Archivo o directorio a respaldar
  destino         Directorio donde guardar el respaldo (opcional)
                  Por defecto: $DEFAULT_BACKUP_DIR

OPCIONES:
  -v, --verbose       Modo verboso (mostrar progreso detallado)
  -c, --compress      Comprimir el respaldo en tar.gz
  -n, --dry-run       Simulación (no realizar cambios reales)
  -e, --exclude PATRÓN Excluir archivos/directorios que coincidan con PATRÓN
  -l, --list [DIR]    Listar respaldos existentes
  -h, --help          Mostrar esta ayuda

EJEMPLOS:
  $SCRIPT_NAME /home/user/documents
    # Respaldar documents al directorio por defecto

  $SCRIPT_NAME -v -c /home/user/projects /backup/external
    # Respaldar projects con progreso verboso y compresión

  $SCRIPT_NAME -n -e "*.log" -e "node_modules" /home/user/code
    # Simulación excluyendo logs y node_modules

  $SCRIPT_NAME --list
    # Listar respaldos existentes

NOTAS:
  - Los respaldos incluyen timestamp automático
  - Se preservan permisos y enlaces simbólicos
  - Requiere rsync instalado en el sistema
EOF
}

# Procesamiento de argumentos
SOURCE=""
DESTINATION="$DEFAULT_BACKUP_DIR"

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--compress)
            COMPRESS=true
            shift
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -e|--exclude)
            EXCLUDE_PATTERNS+=("$2")
            shift 2
            ;;
        -l|--list)
            list_backups "$2"
            exit 0
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            log ERROR "Opción desconocida: $1"
            show_help
            exit 1
            ;;
        *)
            if [[ -z "$SOURCE" ]]; then
                SOURCE="$1"
            else
                DESTINATION="$1"
            fi
            shift
            ;;
    esac
done

# Validar argumentos requeridos
if [[ -z "$SOURCE" ]]; then
    log ERROR "Se requiere especificar el origen del respaldo"
    echo ""
    show_help
    exit 1
fi

# Verificar que rsync esté disponible
if ! command -v rsync >/dev/null 2>&1; then
    log ERROR "rsync no está instalado. Instálalo con:"
    log ERROR "  - Ubuntu/Debian: sudo apt install rsync"
    log ERROR "  - macOS: brew install rsync"
    log ERROR "  - CentOS/RHEL: sudo yum install rsync"
    exit 1
fi

# Ejecutar respaldo
create_backup "$SOURCE" "$DESTINATION"

#!/bin/bash

# Scripts de Mantenimiento Automatico
# Descripcion: Herramientas para automatizar tareas de mantenimiento del sistema
# Uso: ./03_maintenance_tasks.sh [comando] [opciones]

SCRIPT_NAME=$(basename "$0")
CONFIG_DIR="$HOME/.config/maintenance_tasks"
LOG_DIR="$CONFIG_DIR/logs"
BACKUP_DIR="$CONFIG_DIR/backups"
TEMP_DIR="/tmp/maintenance_$$"

# Configuracion por defecto
DEFAULT_LOG_RETENTION_DAYS=30
DEFAULT_TEMP_RETENTION_DAYS=7
DEFAULT_BACKUP_RETENTION_DAYS=90
DEFAULT_MAX_LOG_SIZE="100M"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funcion de logging
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_file="$LOG_DIR/maintenance.log"
    
    # Crear directorio de logs si no existe
    mkdir -p "$LOG_DIR"
    
    case "$level" in
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message"
            echo "[$timestamp] [INFO] $message" >> "$log_file"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            echo "[$timestamp] [SUCCESS] $message" >> "$log_file"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} $message"
            echo "[$timestamp] [WARNING] $message" >> "$log_file"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message" >&2
            echo "[$timestamp] [ERROR] $message" >> "$log_file"
            ;;
        HEADER)
            echo -e "\n${CYAN}=== $message ===${NC}"
            echo "[$timestamp] [HEADER] $message" >> "$log_file"
            ;;
    esac
}

# Inicializar directorios de configuracion
init_directories() {
    mkdir -p "$CONFIG_DIR" "$LOG_DIR" "$BACKUP_DIR" "$TEMP_DIR"
    
    # Crear archivo de configuracion si no existe
    local config_file="$CONFIG_DIR/config.conf"
    if [ ! -f "$config_file" ]; then
        cat > "$config_file" << EOF
# Configuracion de Tareas de Mantenimiento
LOG_RETENTION_DAYS=$DEFAULT_LOG_RETENTION_DAYS
TEMP_RETENTION_DAYS=$DEFAULT_TEMP_RETENTION_DAYS
BACKUP_RETENTION_DAYS=$DEFAULT_BACKUP_RETENTION_DAYS
MAX_LOG_SIZE=$DEFAULT_MAX_LOG_SIZE

# Directorios de limpieza temporal
TEMP_DIRS="/tmp /var/tmp $HOME/.cache"

# Patrones de archivos temporales
TEMP_PATTERNS="*.tmp *.temp *~ .#* core.*"

# Directorios de logs a limpiar
LOG_DIRS="/var/log $HOME/.local/share/logs"
EOF
        log SUCCESS "Archivo de configuracion creado: $config_file"
    fi
}

# Cargar configuracion
load_config() {
    local config_file="$CONFIG_DIR/config.conf"
    if [ -f "$config_file" ]; then
        source "$config_file"
    else
        log WARNING "Archivo de configuracion no encontrado, usando valores por defecto"
        LOG_RETENTION_DAYS=$DEFAULT_LOG_RETENTION_DAYS
        TEMP_RETENTION_DAYS=$DEFAULT_TEMP_RETENTION_DAYS
        BACKUP_RETENTION_DAYS=$DEFAULT_BACKUP_RETENTION_DAYS
        MAX_LOG_SIZE=$DEFAULT_MAX_LOG_SIZE
    fi
}

# Mostrar informacion del sistema
show_system_info() {
    log HEADER "Informacion del Sistema"
    
    echo -e "${BLUE}Sistema:${NC} $(uname -a)"
    echo -e "${BLUE}Uptime:${NC} $(uptime)"
    
    # Espacio en disco
    echo -e "\n${BLUE}Uso de Disco:${NC}"
    df -h | head -1
    df -h | grep -E '^/dev/' | head -5
    
    # Memoria
    echo -e "\n${BLUE}Memoria:${NC}"
    if command -v free >/dev/null 2>&1; then
        free -h
    else
        # macOS
        echo "Memoria total: $(sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}')"
    fi
    
    # Carga del sistema
    echo -e "\n${BLUE}Carga promedio:${NC} $(cat /proc/loadavg 2>/dev/null || uptime | awk -F'load average:' '{print $2}')"
}

# Limpiar archivos temporales
cleanup_temp_files() {
    log HEADER "Limpieza de Archivos Temporales"
    
    local total_removed=0
    local total_size=0
    
    # Directorios temporales configurados
    for temp_dir in $TEMP_DIRS; do
        if [ ! -d "$temp_dir" ]; then
            continue
        fi
        
        log INFO "Limpiando directorio: $temp_dir"
        
        # Buscar archivos temporales antiguos
        local files_found=$(find "$temp_dir" -maxdepth 2 -type f -mtime "+$TEMP_RETENTION_DAYS" 2>/dev/null | wc -l)
        
        if [ "$files_found" -gt 0 ]; then
            # Calcular tamaño antes de eliminar
            local dir_size=$(find "$temp_dir" -maxdepth 2 -type f -mtime "+$TEMP_RETENTION_DAYS" -exec du -c {} + 2>/dev/null | tail -1 | awk '{print $1}')
            
            # Eliminar archivos
            local removed=$(find "$temp_dir" -maxdepth 2 -type f -mtime "+$TEMP_RETENTION_DAYS" -delete -print 2>/dev/null | wc -l)
            
            total_removed=$((total_removed + removed))
            total_size=$((total_size + dir_size))
            
            log SUCCESS "Eliminados $removed archivos de $temp_dir"
        else
            log INFO "No hay archivos antiguos en $temp_dir"
        fi
    done
    
    # Limpiar patrones especificos
    for pattern in $TEMP_PATTERNS; do
        local found=$(find /tmp -maxdepth 1 -name "$pattern" -mtime "+$TEMP_RETENTION_DAYS" 2>/dev/null | wc -l)
        if [ "$found" -gt 0 ]; then
            find /tmp -maxdepth 1 -name "$pattern" -mtime "+$TEMP_RETENTION_DAYS" -delete 2>/dev/null
            log SUCCESS "Eliminados archivos con patron $pattern"
        fi
    done
    
    log SUCCESS "Total eliminado: $total_removed archivos, $((total_size / 1024)) KB liberados"
}

# Rotar y limpiar logs
cleanup_logs() {
    log HEADER "Limpieza y Rotacion de Logs"
    
    local total_rotated=0
    
    # Rotar logs propios
    local maintenance_log="$LOG_DIR/maintenance.log"
    if [ -f "$maintenance_log" ]; then
        local log_size=$(stat -c%s "$maintenance_log" 2>/dev/null || stat -f%z "$maintenance_log" 2>/dev/null)
        local max_size_bytes=$(echo "$MAX_LOG_SIZE" | sed 's/M/*1024*1024/' | sed 's/K/*1024/' | bc 2>/dev/null || echo 104857600)
        
        if [ "$log_size" -gt "$max_size_bytes" ]; then
            mv "$maintenance_log" "$maintenance_log.$(date +%Y%m%d_%H%M%S)"
            touch "$maintenance_log"
            log SUCCESS "Log rotado: $maintenance_log"
            total_rotated=$((total_rotated + 1))
        fi
    fi
    
    # Limpiar logs antiguos
    find "$LOG_DIR" -name "*.log.*" -mtime "+$LOG_RETENTION_DAYS" -delete 2>/dev/null
    
    # Limpiar directorios de logs del sistema (solo si tenemos permisos)
    for log_dir in $LOG_DIRS; do
        if [ -d "$log_dir" ] && [ -w "$log_dir" ]; then
            log INFO "Limpiando logs en: $log_dir"
            local cleaned=$(find "$log_dir" -name "*.log.[0-9]*" -mtime "+$LOG_RETENTION_DAYS" -delete -print 2>/dev/null | wc -l)
            if [ "$cleaned" -gt 0 ]; then
                log SUCCESS "Eliminados $cleaned logs antiguos de $log_dir"
            fi
        fi
    done
    
    log SUCCESS "Rotacion de logs completada: $total_rotated logs rotados"
}

# Verificar y limpiar espacio en disco
check_disk_space() {
    log HEADER "Verificacion de Espacio en Disco"
    
    local warning_threshold=85
    local critical_threshold=95
    
    # Verificar particiones principales
    df -h | grep -E '^/dev/' | while read -r filesystem size used avail use mountpoint; do
        local usage_percent=$(echo "$use" | sed 's/%//')
        
        echo -e "${BLUE}$mountpoint:${NC} $used/$size usado ($use)"
        
        if [ "$usage_percent" -ge "$critical_threshold" ]; then
            log ERROR "CRITICO: $mountpoint esta al $use de capacidad"
        elif [ "$usage_percent" -ge "$warning_threshold" ]; then
            log WARNING "ALERTA: $mountpoint esta al $use de capacidad"
        else
            log SUCCESS "$mountpoint tiene espacio suficiente ($use usado)"
        fi
    done
    
    # Buscar directorios que consumen mas espacio
    echo -e "\n${BLUE}Top 10 directorios por tamaño en $HOME:${NC}"
    du -h "$HOME"/* 2>/dev/null | sort -hr | head -10 || true
}

# Verificar servicios criticos
check_services() {
    log HEADER "Verificacion de Servicios"
    
    # Lista de servicios comunes a verificar
    local services=("ssh" "sshd" "nginx" "apache2" "httpd" "mysql" "postgresql" "docker" "cron" "crond")
    
    local running_services=0
    local total_checked=0
    
    for service in "${services[@]}"; do
        if systemctl list-unit-files | grep -q "^$service.service"; then
            total_checked=$((total_checked + 1))
            
            if systemctl is-active "$service" >/dev/null 2>&1; then
                log SUCCESS "Servicio $service esta corriendo"
                running_services=$((running_services + 1))
            else
                if systemctl is-enabled "$service" >/dev/null 2>&1; then
                    log WARNING "Servicio $service esta habilitado pero no corriendo"
                else
                    log INFO "Servicio $service no esta habilitado"
                fi
            fi
        fi
    done
    
    log INFO "Servicios verificados: $running_services/$total_checked corriendo"
}

# Actualizar base de datos de locate
update_locate_db() {
    log HEADER "Actualizacion de Base de Datos de Locate"
    
    if command -v updatedb >/dev/null 2>&1; then
        log INFO "Actualizando base de datos de locate..."
        if updatedb 2>/dev/null; then
            log SUCCESS "Base de datos de locate actualizada"
        else
            log WARNING "No se pudo actualizar locate (permisos insuficientes)"
            log INFO "Ejecuta: sudo updatedb"
        fi
    else
        log INFO "locate no esta instalado"
    fi
}

# Crear reporte de mantenimiento
generate_report() {
    log HEADER "Generando Reporte de Mantenimiento"
    
    local report_file="$LOG_DIR/maintenance_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "REPORTE DE MANTENIMIENTO"
        echo "========================"
        echo "Fecha: $(date)"
        echo "Sistema: $(uname -a)"
        echo "Usuario: $(whoami)"
        echo ""
        
        echo "ESPACIO EN DISCO:"
        df -h
        echo ""
        
        echo "MEMORIA:"
        free -h 2>/dev/null || echo "Comando free no disponible"
        echo ""
        
        echo "UPTIME:"
        uptime
        echo ""
        
        echo "CARGA PROMEDIO:"
        cat /proc/loadavg 2>/dev/null || uptime | awk -F'load average:' '{print $2}'
        echo ""
        
        echo "PROCESOS PRINCIPALES:"
        ps aux | head -10
        echo ""
        
        echo "ULTIMOS LOGS DE MANTENIMIENTO:"
        tail -20 "$LOG_DIR/maintenance.log" 2>/dev/null || echo "No hay logs disponibles"
        
    } > "$report_file"
    
    log SUCCESS "Reporte generado: $report_file"
    
    # Mostrar resumen
    echo -e "\n${BLUE}Resumen del reporte:${NC}"
    head -20 "$report_file"
}

# Ejecutar mantenimiento completo
run_full_maintenance() {
    log HEADER "Mantenimiento Completo del Sistema"
    
    local start_time=$(date +%s)
    
    # Inicializar
    init_directories
    load_config
    
    # Ejecutar tareas
    show_system_info
    cleanup_temp_files
    cleanup_logs
    check_disk_space
    check_services
    update_locate_db
    generate_report
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log SUCCESS "Mantenimiento completo finalizado en ${duration}s"
}

# Crear tarea programada de mantenimiento
setup_scheduled_task() {
    log HEADER "Configurar Tarea Programada"
    
    echo -e "${YELLOW}Opciones de programacion:${NC}"
    echo "1) Diario a las 2:00 AM"
    echo "2) Semanal los domingos a las 3:00 AM"
    echo "3) Mensual el primer dia a las 4:00 AM"
    echo "4) Personalizado"
    
    read -p "Selecciona opcion (1-4): " schedule_option
    
    local cron_expression=""
    case "$schedule_option" in
        1) cron_expression="0 2 * * *" ;;
        2) cron_expression="0 3 * * 0" ;;
        3) cron_expression="0 4 1 * *" ;;
        4) 
            read -p "Ingresa expresion cron: " cron_expression
            ;;
        *)
            log ERROR "Opcion invalida"
            return 1
            ;;
    esac
    
    local script_path=$(readlink -f "$0")
    local cron_command="$script_path full-maintenance >> $LOG_DIR/maintenance.log 2>&1"
    
    # Agregar a crontab
    (crontab -l 2>/dev/null || true; echo "$cron_expression $cron_command") | crontab -
    
    log SUCCESS "Tarea programada agregada:"
    log INFO "  Horario: $cron_expression"
    log INFO "  Comando: $cron_command"
}

# Mostrar ayuda
show_help() {
    cat << EOF
Scripts de Mantenimiento Automatico

USAGE:
    $SCRIPT_NAME [COMANDO] [OPCIONES]

COMANDOS:
    info                Mostrar informacion del sistema
    cleanup-temp        Limpiar archivos temporales
    cleanup-logs        Limpiar y rotar logs
    check-disk          Verificar espacio en disco
    check-services      Verificar servicios criticos
    update-locate       Actualizar base de datos locate
    report              Generar reporte de mantenimiento
    full-maintenance    Ejecutar mantenimiento completo
    setup-schedule      Configurar tarea programada
    help                Mostrar esta ayuda

EJEMPLOS:
    $SCRIPT_NAME info               # Ver informacion del sistema
    $SCRIPT_NAME cleanup-temp       # Limpiar archivos temporales
    $SCRIPT_NAME full-maintenance   # Mantenimiento completo
    $SCRIPT_NAME setup-schedule     # Programar mantenimiento

CONFIGURACION:
    $CONFIG_DIR/config.conf         # Archivo de configuracion

LOGS:
    $LOG_DIR/maintenance.log        # Log principal
    $LOG_DIR/maintenance_report_*   # Reportes generados

VARIABLES DE ENTORNO:
    LOG_RETENTION_DAYS              # Dias de retencion de logs
    TEMP_RETENTION_DAYS             # Dias de retencion de temporales
    BACKUP_RETENTION_DAYS           # Dias de retencion de backups
EOF
}

# Funcion principal
main() {
    local command="${1:-full-maintenance}"
    shift 2>/dev/null || true
    
    # Inicializar siempre
    init_directories
    load_config
    
    case "$command" in
        info)
            show_system_info
            ;;
        cleanup-temp)
            cleanup_temp_files
            ;;
        cleanup-logs)
            cleanup_logs
            ;;
        check-disk)
            check_disk_space
            ;;
        check-services)
            check_services
            ;;
        update-locate)
            update_locate_db
            ;;
        report)
            generate_report
            ;;
        full-maintenance)
            run_full_maintenance
            ;;
        setup-schedule)
            setup_scheduled_task
            ;;
        help|-h|--help)
            show_help
            ;;
        *)
            log ERROR "Comando no reconocido: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Cleanup al salir
cleanup() {
    rm -rf "$TEMP_DIR" 2>/dev/null || true
}

trap cleanup EXIT

# Ejecutar funcion principal
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

#!/bin/bash

# Fundamentos de Cron y Crontab
# Descripcion: Script interactivo para aprender y gestionar tareas de cron
# Uso: ./01_cron_basics.sh [comando] [opciones]

SCRIPT_NAME=$(basename "$0")
BACKUP_DIR="$HOME/cron_backups"
TEMP_CRON="/tmp/temp_crontab_$$"

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
    
    case "$level" in
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message" >&2
            ;;
        HEADER)
            echo -e "\n${CYAN}=== $message ===${NC}"
            ;;
    esac
}

# Verificar si cron esta instalado y corriendo
check_cron_service() {
    log HEADER "Verificando Servicio Cron"
    
    # Verificar si cron esta instalado
    if ! command -v crontab >/dev/null 2>&1; then
        log ERROR "crontab no esta instalado"
        log INFO "Para instalar:"
        log INFO "  Ubuntu/Debian: sudo apt install cron"
        log INFO "  CentOS/RHEL: sudo yum install cronie"
        log INFO "  macOS: Incluido por defecto"
        return 1
    fi
    
    log SUCCESS "crontab esta disponible"
    
    # Verificar si el servicio esta corriendo
    if systemctl is-active --quiet cron 2>/dev/null; then
        log SUCCESS "Servicio cron esta activo"
    elif systemctl is-active --quiet crond 2>/dev/null; then
        log SUCCESS "Servicio crond esta activo"
    elif launchctl list | grep -q com.apple.cron 2>/dev/null; then
        log SUCCESS "Servicio cron de macOS esta activo"
    else
        log WARNING "No se puede verificar el estado del servicio cron"
        log INFO "Para iniciar cron:"
        log INFO "  Linux: sudo systemctl start cron"
        log INFO "  macOS: sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.cron.plist"
    fi
}

# Mostrar crontab actual
show_current_crontab() {
    log HEADER "Crontab Actual"
    
    if crontab -l >/dev/null 2>&1; then
        echo -e "${BLUE}Usuario:${NC} $(whoami)"
        echo -e "${BLUE}Crontab actual:${NC}"
        echo "----------------------------------------"
        crontab -l | nl -ba
        echo "----------------------------------------"
        
        local count=$(crontab -l | grep -v '^#' | grep -v '^$' | wc -l)
        log INFO "Total de tareas activas: $count"
    else
        log WARNING "No hay crontab configurado para el usuario $(whoami)"
        log INFO "Usa '$SCRIPT_NAME add' para agregar tu primera tarea"
    fi
}

# Explicar sintaxis de cron
explain_cron_syntax() {
    log HEADER "Sintaxis de Cron"
    
    cat << 'EOF'

Formato: MIN HORA DIA MES DIA_SEMANA COMANDO

Campos:
  ┌─────────────── minutos (0-59)
  │ ┌───────────── horas (0-23)  
  │ │ ┌─────────── dia del mes (1-31)
  │ │ │ ┌───────── mes (1-12)
  │ │ │ │ ┌─────── dia de la semana (0-7, donde 0 y 7 = domingo)
  │ │ │ │ │
  * * * * * /ruta/al/comando

Caracteres especiales:
  *     = cualquier valor
  ,     = lista de valores (1,3,5)
  -     = rango de valores (1-5)
  /     = incremento (*/5 = cada 5 unidades)
  @     = alias especiales

Alias especiales:
  @reboot   = al reiniciar
  @yearly   = 0 0 1 1 * (anualmente)
  @monthly  = 0 0 1 * * (mensualmente)
  @weekly   = 0 0 * * 0 (semanalmente)
  @daily    = 0 0 * * * (diariamente)
  @hourly   = 0 * * * * (cada hora)

Ejemplos:
  0 2 * * *           # Diario a las 2:00 AM
  0 0 * * 0           # Semanal los domingos a medianoche
  0 */4 * * *         # Cada 4 horas
  */15 * * * *        # Cada 15 minutos
  0 9 1 * *           # El primer dia de cada mes a las 9:00 AM
  0 22 * * 1-5        # Lunes a viernes a las 10:00 PM
  30 14 * * 1,3,5     # Lunes, miercoles y viernes a las 2:30 PM
EOF
}

# Crear backup del crontab actual
backup_crontab() {
    log HEADER "Respaldo de Crontab"
    
    # Crear directorio de backups si no existe
    mkdir -p "$BACKUP_DIR"
    
    local backup_file="$BACKUP_DIR/crontab_$(date +%Y%m%d_%H%M%S).backup"
    
    if crontab -l > "$backup_file" 2>/dev/null; then
        log SUCCESS "Backup creado: $backup_file"
        return 0
    else
        log WARNING "No hay crontab para respaldar"
        return 1
    fi
}

# Agregar nueva tarea
add_cron_job() {
    log HEADER "Agregar Nueva Tarea"
    
    # Crear backup antes de modificar
    backup_crontab
    
    echo -e "${YELLOW}Ejemplos de horarios:${NC}"
    echo "  0 2 * * *     - Diario a las 2:00 AM"
    echo "  */30 * * * *  - Cada 30 minutos"
    echo "  0 9 * * 1     - Lunes a las 9:00 AM"
    echo "  @daily        - Una vez al dia"
    echo ""
    
    read -p "Ingresa el horario (formato cron): " schedule
    read -p "Ingresa el comando a ejecutar: " command
    
    if [ -z "$schedule" ] || [ -z "$command" ]; then
        log ERROR "Horario y comando son requeridos"
        return 1
    fi
    
    # Validar sintaxis basica
    if ! echo "$schedule" | grep -q '^[@*]' && ! echo "$schedule" | grep -E '^[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+$' >/dev/null; then
        log ERROR "Formato de horario invalido"
        log INFO "Usa la sintaxis: MIN HORA DIA MES DIA_SEMANA"
        return 1
    fi
    
    # Agregar comentario con fecha
    local comment="# Agregado el $(date) por $SCRIPT_NAME"
    local new_job="$schedule $command"
    
    # Obtener crontab actual y agregar nueva tarea
    {
        crontab -l 2>/dev/null || true
        echo "$comment"
        echo "$new_job"
    } | crontab -
    
    log SUCCESS "Tarea agregada exitosamente:"
    log INFO "  Horario: $schedule"
    log INFO "  Comando: $command"
}

# Eliminar tarea
remove_cron_job() {
    log HEADER "Eliminar Tarea"
    
    if ! crontab -l >/dev/null 2>&1; then
        log WARNING "No hay tareas para eliminar"
        return 1
    fi
    
    backup_crontab
    
    echo -e "${BLUE}Tareas actuales:${NC}"
    crontab -l | grep -n "."
    echo ""
    
    read -p "Ingresa el numero de linea a eliminar (0 para cancelar): " line_num
    
    if [ "$line_num" = "0" ] || [ -z "$line_num" ]; then
        log INFO "Operacion cancelada"
        return 0
    fi
    
    if ! [[ "$line_num" =~ ^[0-9]+$ ]]; then
        log ERROR "Numero de linea invalido"
        return 1
    fi
    
    # Crear nuevo crontab sin la linea especificada
    crontab -l | sed "${line_num}d" | crontab -
    
    log SUCCESS "Tarea en la linea $line_num eliminada"
}

# Editar crontab con editor
edit_crontab() {
    log HEADER "Editar Crontab"
    
    backup_crontab
    
    local editor="${EDITOR:-nano}"
    log INFO "Abriendo crontab con $editor"
    log INFO "Guardando backup antes de editar..."
    
    crontab -e
}

# Listar backups disponibles
list_backups() {
    log HEADER "Backups Disponibles"
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
        log WARNING "No hay backups disponibles"
        return 1
    fi
    
    echo -e "${BLUE}Directorio de backups:${NC} $BACKUP_DIR"
    echo ""
    
    ls -la "$BACKUP_DIR"/*.backup 2>/dev/null | while read -r line; do
        echo "  $line"
    done
}

# Restaurar desde backup
restore_backup() {
    log HEADER "Restaurar Backup"
    
    list_backups
    
    if [ ! -d "$BACKUP_DIR" ]; then
        return 1
    fi
    
    echo ""
    read -p "Ingresa el nombre del archivo de backup: " backup_file
    
    if [ -z "$backup_file" ]; then
        log INFO "Operacion cancelada"
        return 0
    fi
    
    local full_path="$BACKUP_DIR/$backup_file"
    if [ ! -f "$full_path" ]; then
        # Intentar con el path completo si no se encontro
        if [ -f "$backup_file" ]; then
            full_path="$backup_file"
        else
            log ERROR "Archivo de backup no encontrado: $backup_file"
            return 1
        fi
    fi
    
    # Crear backup del estado actual antes de restaurar
    backup_crontab
    
    # Restaurar
    if crontab "$full_path"; then
        log SUCCESS "Crontab restaurado desde: $full_path"
    else
        log ERROR "Error al restaurar crontab"
        return 1
    fi
}

# Validar expresion cron
validate_cron_expression() {
    local expression="$1"
    
    if [ -z "$expression" ]; then
        read -p "Ingresa expresion cron para validar: " expression
    fi
    
    log HEADER "Validar Expresion Cron"
    
    # Validacion basica de formato
    if echo "$expression" | grep -q '^@'; then
        log SUCCESS "Alias valido: $expression"
        return 0
    fi
    
    # Contar campos
    local field_count=$(echo "$expression" | awk '{print NF}')
    if [ "$field_count" -lt 5 ]; then
        log ERROR "Expresion incompleta. Se requieren 5 campos: MIN HORA DIA MES DIA_SEMANA"
        return 1
    fi
    
    log SUCCESS "Formato de expresion parece valido: $expression"
    
    # Mostrar interpretacion
    echo -e "\n${BLUE}Interpretacion:${NC}"
    echo "  Minutos: $(echo $expression | awk '{print $1}')"
    echo "  Horas: $(echo $expression | awk '{print $2}')"
    echo "  Dia del mes: $(echo $expression | awk '{print $3}')"
    echo "  Mes: $(echo $expression | awk '{print $4}')"
    echo "  Dia de la semana: $(echo $expression | awk '{print $5}')"
}

# Ver logs de cron
view_cron_logs() {
    log HEADER "Logs de Cron"
    
    local log_files=(
        "/var/log/cron"
        "/var/log/cron.log" 
        "/var/log/syslog"
        "/var/log/messages"
    )
    
    local found_log=""
    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ] && [ -r "$log_file" ]; then
            found_log="$log_file"
            break
        fi
    done
    
    if [ -n "$found_log" ]; then
        log INFO "Mostrando logs de: $found_log"
        echo ""
        # Mostrar solo entradas recientes de cron
        grep -i cron "$found_log" | tail -20
    else
        log WARNING "No se encontraron logs de cron accesibles"
        log INFO "Intenta con:"
        log INFO "  sudo grep CRON /var/log/syslog | tail -10"
        log INFO "  journalctl -u cron | tail -10"
    fi
}

# Mostrar ayuda
show_help() {
    cat << EOF
Fundamentos de Cron y Crontab

USAGE:
    $SCRIPT_NAME [COMANDO] [OPCIONES]

COMANDOS:
    check               Verificar servicio cron
    show                Mostrar crontab actual
    syntax              Explicar sintaxis de cron
    add                 Agregar nueva tarea
    remove              Eliminar tarea existente
    edit                Editar crontab con editor
    backup              Crear backup del crontab
    list-backups        Listar backups disponibles
    restore             Restaurar desde backup
    validate [EXPR]     Validar expresion cron
    logs                Ver logs de cron
    help                Mostrar esta ayuda

EJEMPLOS:
    $SCRIPT_NAME check              # Verificar cron
    $SCRIPT_NAME show               # Ver tareas actuales
    $SCRIPT_NAME add                # Agregar nueva tarea
    $SCRIPT_NAME validate "0 2 * * *"  # Validar expresion

VARIABLES DE ENTORNO:
    EDITOR              Editor para crontab (default: nano)

ARCHIVOS:
    $BACKUP_DIR/        # Directorio de backups
EOF
}

# Funcion principal
main() {
    local command="${1:-show}"
    shift 2>/dev/null || true
    
    case "$command" in
        check)
            check_cron_service
            ;;
        show)
            show_current_crontab
            ;;
        syntax)
            explain_cron_syntax
            ;;
        add)
            add_cron_job
            ;;
        remove)
            remove_cron_job
            ;;
        edit)
            edit_crontab
            ;;
        backup)
            backup_crontab
            ;;
        list-backups)
            list_backups
            ;;
        restore)
            restore_backup
            ;;
        validate)
            validate_cron_expression "$1"
            ;;
        logs)
            view_cron_logs
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
    rm -f "$TEMP_CRON" 2>/dev/null || true
}

trap cleanup EXIT

# Ejecutar funcion principal
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

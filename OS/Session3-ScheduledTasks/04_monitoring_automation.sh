#!/bin/bash

# Monitoreo y Alertas Automatizadas
# Descripcion: Sistema completo de monitoreo con alertas y notificaciones
# Uso: ./04_monitoring_automation.sh [comando] [opciones]

SCRIPT_NAME=$(basename "$0")
CONFIG_DIR="$HOME/.config/monitoring_automation"
LOG_DIR="$CONFIG_DIR/logs"
ALERTS_DIR="$CONFIG_DIR/alerts"
REPORTS_DIR="$CONFIG_DIR/reports"

# Configuracion por defecto
DEFAULT_CHECK_INTERVAL=300  # 5 minutos
DEFAULT_CPU_THRESHOLD=80
DEFAULT_MEMORY_THRESHOLD=85
DEFAULT_DISK_THRESHOLD=90
DEFAULT_LOAD_THRESHOLD=5.0

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
    local log_file="$LOG_DIR/monitoring.log"
    
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
        CRITICAL)
            echo -e "${RED}[CRITICAL]${NC} $message" >&2
            echo "[$timestamp] [CRITICAL] $message" >> "$log_file"
            ;;
        HEADER)
            echo -e "\n${CYAN}=== $message ===${NC}"
            echo "[$timestamp] [HEADER] $message" >> "$log_file"
            ;;
    esac
}

# Inicializar directorios y configuracion
init_monitoring() {
    mkdir -p "$CONFIG_DIR" "$LOG_DIR" "$ALERTS_DIR" "$REPORTS_DIR"
    
    local config_file="$CONFIG_DIR/monitoring.conf"
    if [ ! -f "$config_file" ]; then
        cat > "$config_file" << EOF
# Configuracion de Monitoreo Automatizado

# Intervalos (en segundos)
CHECK_INTERVAL=$DEFAULT_CHECK_INTERVAL

# Umbrales de alertas
CPU_THRESHOLD=$DEFAULT_CPU_THRESHOLD
MEMORY_THRESHOLD=$DEFAULT_MEMORY_THRESHOLD
DISK_THRESHOLD=$DEFAULT_DISK_THRESHOLD
LOAD_THRESHOLD=$DEFAULT_LOAD_THRESHOLD

# Notificaciones
EMAIL_ENABLED=false
EMAIL_TO=""
WEBHOOK_ENABLED=false
WEBHOOK_URL=""

# Servicios a monitorear
SERVICES_TO_MONITOR="ssh nginx apache2 mysql postgresql docker"

# Directorios criticos
CRITICAL_DIRS="/ /home /var /tmp"

# Procesos criticos
CRITICAL_PROCESSES="init systemd"
EOF
        log SUCCESS "Archivo de configuracion creado: $config_file"
    fi
}

# Cargar configuracion
load_config() {
    local config_file="$CONFIG_DIR/monitoring.conf"
    if [ -f "$config_file" ]; then
        source "$config_file"
    else
        log WARNING "Archivo de configuracion no encontrado, usando valores por defecto"
        CPU_THRESHOLD=$DEFAULT_CPU_THRESHOLD
        MEMORY_THRESHOLD=$DEFAULT_MEMORY_THRESHOLD
        DISK_THRESHOLD=$DEFAULT_DISK_THRESHOLD
        LOAD_THRESHOLD=$DEFAULT_LOAD_THRESHOLD
    fi
}

# Verificar uso de CPU
check_cpu_usage() {
    local cpu_usage=""
    
    # Intentar diferentes metodos para obtener CPU
    if command -v top >/dev/null 2>&1; then
        # Usar top (disponible en la mayoria de sistemas)
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 2>/dev/null)
    fi
    
    # Metodo alternativo con iostat
    if [ -z "$cpu_usage" ] && command -v iostat >/dev/null 2>&1; then
        cpu_usage=$(iostat -c 1 1 | tail -1 | awk '{print 100-$6}' 2>/dev/null)
    fi
    
    # Metodo de /proc/stat
    if [ -z "$cpu_usage" ] && [ -f /proc/stat ]; then
        cpu_usage=$(awk '/^cpu /{u=$2+$4; t=$2+$3+$4+$5; if (NR==1){u1=u; t1=t;} else print ($2+$4-u1) * 100 / (t-t1) "%"; }' /proc/stat /proc/stat | tail -1 | cut -d'%' -f1)
    fi
    
    # Fallback: usar load average como aproximacion
    if [ -z "$cpu_usage" ]; then
        local load=$(cat /proc/loadavg 2>/dev/null | awk '{print $1}' || uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $1}' | tr -d ' ')
        cpu_usage=$(echo "$load * 20" | bc -l 2>/dev/null | cut -d. -f1 || echo "0")
    fi
    
    # Limpiar resultado
    cpu_usage=$(echo "$cpu_usage" | tr -d ' ' | cut -d. -f1)
    
    # Validar resultado
    if [[ "$cpu_usage" =~ ^[0-9]+$ ]] && [ "$cpu_usage" -le 100 ]; then
        echo "$cpu_usage"
    else
        echo "0"
    fi
}

# Verificar uso de memoria
check_memory_usage() {
    local memory_percent=""
    
    if command -v free >/dev/null 2>&1; then
        # Linux
        memory_percent=$(free | grep '^Mem:' | awk '{printf "%.0f", $3/$2 * 100.0}')
    elif [ -f /proc/meminfo ]; then
        # Alternativo usando /proc/meminfo
        local total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        local available=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
        local used=$((total - available))
        memory_percent=$(echo "scale=0; $used * 100 / $total" | bc 2>/dev/null || echo "0")
    elif command -v vm_stat >/dev/null 2>&1; then
        # macOS
        local page_size=$(vm_stat | grep "page size" | awk '{print $8}')
        local pages_free=$(vm_stat | grep "Pages free" | awk '{print $3}' | tr -d '.')
        local pages_active=$(vm_stat | grep "Pages active" | awk '{print $3}' | tr -d '.')
        local pages_inactive=$(vm_stat | grep "Pages inactive" | awk '{print $3}' | tr -d '.')
        local pages_wired=$(vm_stat | grep "Pages wired down" | awk '{print $4}' | tr -d '.')
        
        local total_pages=$((pages_free + pages_active + pages_inactive + pages_wired))
        local used_pages=$((pages_active + pages_inactive + pages_wired))
        
        memory_percent=$(echo "scale=0; $used_pages * 100 / $total_pages" | bc 2>/dev/null || echo "0")
    else
        memory_percent="0"
    fi
    
    echo "${memory_percent:-0}"
}

# Verificar uso de disco
check_disk_usage() {
    local max_usage=0
    local critical_disk=""
    
    # Verificar particiones principales
    df -h | grep -E '^/dev/' | while read -r filesystem size used avail use mountpoint; do
        local usage_percent=$(echo "$use" | sed 's/%//')
        
        if [ "$usage_percent" -gt "$max_usage" ]; then
            max_usage="$usage_percent"
            critical_disk="$mountpoint"
        fi
        
        if [ "$usage_percent" -ge "$DISK_THRESHOLD" ]; then
            create_alert "DISK" "CRITICAL" "Disco $mountpoint al $use de capacidad"
        fi
    done
    
    echo "$max_usage"
}

# Verificar carga del sistema
check_load_average() {
    local load_1min=""
    
    if [ -f /proc/loadavg ]; then
        load_1min=$(cat /proc/loadavg | awk '{print $1}')
    else
        load_1min=$(uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $1}' | tr -d ' ')
    fi
    
    echo "${load_1min:-0}"
}

# Verificar servicios criticos
check_services() {
    local failed_services=""
    local total_services=0
    local running_services=0
    
    for service in $SERVICES_TO_MONITOR; do
        if systemctl list-unit-files | grep -q "^$service.service" 2>/dev/null; then
            total_services=$((total_services + 1))
            
            if systemctl is-active "$service" >/dev/null 2>&1; then
                running_services=$((running_services + 1))
            else
                if systemctl is-enabled "$service" >/dev/null 2>&1; then
                    failed_services="$failed_services $service"
                    create_alert "SERVICE" "ERROR" "Servicio $service no esta corriendo"
                fi
            fi
        fi
    done
    
    log INFO "Servicios: $running_services/$total_services corriendo"
    
    if [ -n "$failed_services" ]; then
        log WARNING "Servicios fallidos:$failed_services"
        return 1
    fi
    
    return 0
}

# Verificar procesos criticos
check_processes() {
    local missing_processes=""
    
    for process in $CRITICAL_PROCESSES; do
        if ! pgrep "$process" >/dev/null 2>&1; then
            missing_processes="$missing_processes $process"
            create_alert "PROCESS" "CRITICAL" "Proceso critico $process no encontrado"
        fi
    done
    
    if [ -n "$missing_processes" ]; then
        log ERROR "Procesos criticos faltantes:$missing_processes"
        return 1
    fi
    
    return 0
}

# Crear alerta
create_alert() {
    local type="$1"
    local severity="$2"
    local message="$3"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local alert_file="$ALERTS_DIR/alert_${type}_${timestamp}.txt"
    
    mkdir -p "$ALERTS_DIR"
    
    {
        echo "ALERTA DE MONITOREO"
        echo "==================="
        echo "Timestamp: $(date)"
        echo "Tipo: $type"
        echo "Severidad: $severity"
        echo "Mensaje: $message"
        echo "Host: $(hostname)"
        echo "Usuario: $(whoami)"
        echo ""
        echo "=== INFORMACION DEL SISTEMA ==="
        echo "Uptime: $(uptime)"
        echo "Load: $(cat /proc/loadavg 2>/dev/null || uptime | awk -F'load average:' '{print $2}')"
        echo "Memory: $(free -h 2>/dev/null || echo 'N/A')"
        echo ""
    } > "$alert_file"
    
    log "$severity" "ALERTA [$type]: $message"
    
    # Enviar notificacion si esta habilitada
    send_notification "$type" "$severity" "$message" "$alert_file"
}

# Enviar notificacion
send_notification() {
    local type="$1"
    local severity="$2"
    local message="$3"
    local alert_file="$4"
    
    # Email notification
    if [ "$EMAIL_ENABLED" = "true" ] && [ -n "$EMAIL_TO" ] && command -v mail >/dev/null 2>&1; then
        local subject="[MONITORING] $severity: $type Alert on $(hostname)"
        mail -s "$subject" "$EMAIL_TO" < "$alert_file"
        log INFO "Email enviado a: $EMAIL_TO"
    fi
    
    # Webhook notification
    if [ "$WEBHOOK_ENABLED" = "true" ] && [ -n "$WEBHOOK_URL" ] && command -v curl >/dev/null 2>&1; then
        local payload=$(cat << EOF
{
    "type": "$type",
    "severity": "$severity", 
    "message": "$message",
    "hostname": "$(hostname)",
    "timestamp": "$(date -Iseconds)"
}
EOF
)
        
        if curl -X POST -H "Content-Type: application/json" -d "$payload" "$WEBHOOK_URL" >/dev/null 2>&1; then
            log INFO "Webhook enviado a: $WEBHOOK_URL"
        else
            log WARNING "Error enviando webhook"
        fi
    fi
}

# Ejecutar verificacion completa
run_monitoring_check() {
    log HEADER "Verificacion de Monitoreo - $(date)"
    
    local alerts_triggered=0
    
    # Verificar CPU
    local cpu_usage=$(check_cpu_usage)
    log INFO "CPU: ${cpu_usage}%"
    if [ "$cpu_usage" -ge "$CPU_THRESHOLD" ]; then
        create_alert "CPU" "WARNING" "Uso de CPU alto: ${cpu_usage}%"
        alerts_triggered=$((alerts_triggered + 1))
    fi
    
    # Verificar memoria
    local memory_usage=$(check_memory_usage)
    log INFO "Memoria: ${memory_usage}%"
    if [ "$memory_usage" -ge "$MEMORY_THRESHOLD" ]; then
        create_alert "MEMORY" "WARNING" "Uso de memoria alto: ${memory_usage}%"
        alerts_triggered=$((alerts_triggered + 1))
    fi
    
    # Verificar disco
    local disk_usage=$(check_disk_usage)
    log INFO "Disco: ${disk_usage}%"
    
    # Verificar carga del sistema
    local load_avg=$(check_load_average)
    log INFO "Load Average: $load_avg"
    if [ "$(echo "$load_avg > $LOAD_THRESHOLD" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
        create_alert "LOAD" "WARNING" "Carga del sistema alta: $load_avg"
        alerts_triggered=$((alerts_triggered + 1))
    fi
    
    # Verificar servicios
    if ! check_services; then
        alerts_triggered=$((alerts_triggered + 1))
    fi
    
    # Verificar procesos criticos
    if ! check_processes; then
        alerts_triggered=$((alerts_triggered + 1))
    fi
    
    # Resumen
    if [ $alerts_triggered -eq 0 ]; then
        log SUCCESS "Todas las verificaciones pasaron sin alertas"
    else
        log WARNING "$alerts_triggered alertas generadas"
    fi
    
    return $alerts_triggered
}

# Generar reporte de estado
generate_status_report() {
    log HEADER "Generando Reporte de Estado"
    
    local report_file="$REPORTS_DIR/status_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "REPORTE DE ESTADO DEL SISTEMA"
        echo "=============================="
        echo "Generado: $(date)"
        echo "Host: $(hostname)"
        echo "Sistema: $(uname -a)"
        echo ""
        
        echo "METRICAS ACTUALES:"
        echo "  CPU: $(check_cpu_usage)%"
        echo "  Memoria: $(check_memory_usage)%"
        echo "  Disco: $(check_disk_usage)%"
        echo "  Load Average: $(check_load_average)"
        echo ""
        
        echo "UPTIME:"
        uptime
        echo ""
        
        echo "USO DE DISCO:"
        df -h
        echo ""
        
        echo "MEMORIA:"
        free -h 2>/dev/null || echo "Comando free no disponible"
        echo ""
        
        echo "PROCESOS TOP:"
        ps aux | head -10
        echo ""
        
        echo "ULTIMAS ALERTAS:"
        find "$ALERTS_DIR" -name "alert_*.txt" -mtime -1 | head -5 | while read -r alert; do
            echo "$(basename "$alert"):"
            head -10 "$alert"
            echo ""
        done
        
    } > "$report_file"
    
    log SUCCESS "Reporte generado: $report_file"
    
    # Mostrar resumen
    echo -e "\n${BLUE}Resumen del reporte:${NC}"
    head -25 "$report_file"
}

# Configurar monitoreo automatico
setup_monitoring() {
    log HEADER "Configurar Monitoreo Automatico"
    
    echo -e "${YELLOW}Opciones de frecuencia:${NC}"
    echo "1) Cada 5 minutos"
    echo "2) Cada 15 minutos"
    echo "3) Cada hora"
    echo "4) Personalizado"
    
    read -p "Selecciona frecuencia (1-4): " freq_option
    
    local cron_expression=""
    case "$freq_option" in
        1) cron_expression="*/5 * * * *" ;;
        2) cron_expression="*/15 * * * *" ;;
        3) cron_expression="0 * * * *" ;;
        4) 
            read -p "Ingresa expresion cron: " cron_expression
            ;;
        *)
            log ERROR "Opcion invalida"
            return 1
            ;;
    esac
    
    local script_path=$(readlink -f "$0")
    local cron_command="$script_path check >> $LOG_DIR/monitoring.log 2>&1"
    
    # Agregar a crontab
    (crontab -l 2>/dev/null || true; echo "$cron_expression $cron_command") | crontab -
    
    log SUCCESS "Monitoreo automatico configurado:"
    log INFO "  Frecuencia: $cron_expression"
    log INFO "  Comando: $cron_command"
    
    # Configurar reporte diario
    local report_command="$script_path report >> $LOG_DIR/monitoring.log 2>&1"
    (crontab -l 2>/dev/null || true; echo "0 6 * * * $report_command") | crontab -
    
    log SUCCESS "Reporte diario configurado para las 6:00 AM"
}

# Ver alertas recientes
show_recent_alerts() {
    log HEADER "Alertas Recientes"
    
    local alert_count=$(find "$ALERTS_DIR" -name "alert_*.txt" -mtime -7 2>/dev/null | wc -l)
    
    if [ "$alert_count" -eq 0 ]; then
        log SUCCESS "No hay alertas en los ultimos 7 dias"
        return 0
    fi
    
    log INFO "Encontradas $alert_count alertas en los ultimos 7 dias"
    echo ""
    
    find "$ALERTS_DIR" -name "alert_*.txt" -mtime -7 | sort -r | head -10 | while read -r alert_file; do
        echo -e "${YELLOW}$(basename "$alert_file"):${NC}"
        head -8 "$alert_file" | tail -5
        echo ""
    done
}

# Mostrar ayuda
show_help() {
    cat << EOF
Monitoreo y Alertas Automatizadas

USAGE:
    $SCRIPT_NAME [COMANDO] [OPCIONES]

COMANDOS:
    check               Ejecutar verificacion completa
    report              Generar reporte de estado
    setup               Configurar monitoreo automatico
    alerts              Mostrar alertas recientes
    config              Mostrar configuracion actual
    test                Probar sistema de notificaciones
    help                Mostrar esta ayuda

EJEMPLOS:
    $SCRIPT_NAME check              # Verificacion manual
    $SCRIPT_NAME report             # Generar reporte
    $SCRIPT_NAME setup              # Configurar automatico
    $SCRIPT_NAME alerts             # Ver alertas recientes

CONFIGURACION:
    $CONFIG_DIR/monitoring.conf     # Archivo de configuracion

LOGS:
    $LOG_DIR/monitoring.log         # Log principal
    $ALERTS_DIR/                    # Alertas generadas
    $REPORTS_DIR/                   # Reportes de estado

UMBRALES POR DEFECTO:
    CPU: ${DEFAULT_CPU_THRESHOLD}%
    Memoria: ${DEFAULT_MEMORY_THRESHOLD}%
    Disco: ${DEFAULT_DISK_THRESHOLD}%
    Load: ${DEFAULT_LOAD_THRESHOLD}
EOF
}

# Funcion principal
main() {
    local command="${1:-check}"
    shift 2>/dev/null || true
    
    # Inicializar siempre
    init_monitoring
    load_config
    
    case "$command" in
        check)
            run_monitoring_check
            ;;
        report)
            generate_status_report
            ;;
        setup)
            setup_monitoring
            ;;
        alerts)
            show_recent_alerts
            ;;
        config)
            log HEADER "Configuracion Actual"
            cat "$CONFIG_DIR/monitoring.conf" 2>/dev/null || log ERROR "No se puede leer configuracion"
            ;;
        test)
            log HEADER "Probando Sistema de Notificaciones"
            create_alert "TEST" "INFO" "Prueba del sistema de alertas"
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

# Ejecutar funcion principal
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

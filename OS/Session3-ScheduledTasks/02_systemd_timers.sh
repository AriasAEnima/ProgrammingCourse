#!/bin/bash

# Gestion de Systemd Timers
# Descripcion: Script para crear, gestionar y monitorear systemd timers
# Uso: ./02_systemd_timers.sh [comando] [opciones]

SCRIPT_NAME=$(basename "$0")
SERVICES_DIR="/etc/systemd/system"
USER_SERVICES_DIR="$HOME/.config/systemd/user"
TEMP_DIR="/tmp/systemd_timer_$$"

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

# Verificar systemd
check_systemd() {
    log HEADER "Verificando Systemd"
    
    if ! command -v systemctl >/dev/null 2>&1; then
        log ERROR "systemctl no esta disponible"
        log INFO "Este script requiere un sistema con systemd"
        return 1
    fi
    
    log SUCCESS "systemctl esta disponible"
    
    # Verificar si systemd esta corriendo
    if systemctl is-system-running >/dev/null 2>&1; then
        log SUCCESS "Systemd esta corriendo"
    else
        log WARNING "Systemd podria no estar funcionando correctamente"
    fi
    
    # Mostrar version
    local version=$(systemctl --version | head -1)
    log INFO "Version: $version"
}

# Listar timers activos
list_timers() {
    log HEADER "Timers Activos"
    
    echo -e "${BLUE}Timers del sistema:${NC}"
    systemctl list-timers --all --no-pager 2>/dev/null || {
        log WARNING "No se pueden listar timers del sistema (permisos insuficientes)"
    }
    
    echo -e "\n${BLUE}Timers del usuario:${NC}"
    systemctl --user list-timers --all --no-pager 2>/dev/null || {
        log INFO "No hay timers de usuario configurados"
    }
}

# Crear directorio para servicios de usuario
setup_user_services() {
    if [ ! -d "$USER_SERVICES_DIR" ]; then
        log INFO "Creando directorio para servicios de usuario: $USER_SERVICES_DIR"
        mkdir -p "$USER_SERVICES_DIR"
    fi
}

# Crear nuevo timer
create_timer() {
    log HEADER "Crear Nuevo Timer"
    
    # Preguntar si es timer de usuario o sistema
    echo -e "${YELLOW}Tipo de timer:${NC}"
    echo "1) Usuario (no requiere sudo)"
    echo "2) Sistema (requiere sudo)"
    read -p "Selecciona opcion (1-2): " timer_type
    
    if [ "$timer_type" = "1" ]; then
        local is_user=true
        local target_dir="$USER_SERVICES_DIR"
        setup_user_services
    elif [ "$timer_type" = "2" ]; then
        local is_user=false
        local target_dir="$SERVICES_DIR"
        if [ "$EUID" -ne 0 ]; then
            log ERROR "Timer de sistema requiere permisos de root"
            log INFO "Ejecuta: sudo $0 create"
            return 1
        fi
    else
        log ERROR "Opcion invalida"
        return 1
    fi
    
    # Obtener informacion del timer
    read -p "Nombre del timer (sin extension): " timer_name
    read -p "Descripcion: " description
    read -p "Script o comando a ejecutar: " command
    
    if [ -z "$timer_name" ] || [ -z "$command" ]; then
        log ERROR "Nombre y comando son requeridos"
        return 1
    fi
    
    # Configurar horario
    echo -e "\n${YELLOW}Opciones de horario:${NC}"
    echo "1) Diario"
    echo "2) Semanal" 
    echo "3) Mensual"
    echo "4) Cada hora"
    echo "5) Personalizado"
    read -p "Selecciona horario (1-5): " schedule_type
    
    local calendar_spec=""
    case "$schedule_type" in
        1) calendar_spec="daily" ;;
        2) calendar_spec="weekly" ;;
        3) calendar_spec="monthly" ;;
        4) calendar_spec="hourly" ;;
        5) 
            read -p "Ingresa especificacion OnCalendar (ej: *-*-* 02:00:00): " calendar_spec
            ;;
        *)
            log ERROR "Opcion invalida"
            return 1
            ;;
    esac
    
    # Crear archivo de servicio
    local service_file="$target_dir/${timer_name}.service"
    local timer_file="$target_dir/${timer_name}.timer"
    
    log INFO "Creando archivos de servicio..."
    
    # Archivo .service
    cat > "$service_file" << EOF
[Unit]
Description=$description
Wants=${timer_name}.timer

[Service]
Type=oneshot
ExecStart=$command

[Install]
WantedBy=multi-user.target
EOF
    
    # Archivo .timer
    cat > "$timer_file" << EOF
[Unit]
Description=Timer para $description
Requires=${timer_name}.service

[Timer]
OnCalendar=$calendar_spec
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    log SUCCESS "Archivos creados:"
    log INFO "  Servicio: $service_file"
    log INFO "  Timer: $timer_file"
    
    # Recargar systemd y habilitar
    if [ "$is_user" = true ]; then
        systemctl --user daemon-reload
        systemctl --user enable "${timer_name}.timer"
        systemctl --user start "${timer_name}.timer"
        log SUCCESS "Timer de usuario habilitado e iniciado"
    else
        systemctl daemon-reload
        systemctl enable "${timer_name}.timer"
        systemctl start "${timer_name}.timer"
        log SUCCESS "Timer de sistema habilitado e iniciado"
    fi
    
    # Mostrar estado
    show_timer_status "$timer_name" "$is_user"
}

# Mostrar estado de un timer
show_timer_status() {
    local timer_name="$1"
    local is_user="${2:-false}"
    
    log HEADER "Estado del Timer: $timer_name"
    
    if [ "$is_user" = true ]; then
        systemctl --user status "${timer_name}.timer" --no-pager
        echo ""
        systemctl --user status "${timer_name}.service" --no-pager
    else
        systemctl status "${timer_name}.timer" --no-pager
        echo ""
        systemctl status "${timer_name}.service" --no-pager
    fi
}

# Mostrar logs de un timer
show_timer_logs() {
    local timer_name="$1"
    local is_user="${2:-false}"
    
    if [ -z "$timer_name" ]; then
        read -p "Nombre del timer: " timer_name
    fi
    
    log HEADER "Logs del Timer: $timer_name"
    
    if [ "$is_user" = true ]; then
        journalctl --user -u "${timer_name}.service" --no-pager -n 20
    else
        journalctl -u "${timer_name}.service" --no-pager -n 20
    fi
}

# Eliminar timer
remove_timer() {
    log HEADER "Eliminar Timer"
    
    # Listar timers disponibles
    echo -e "${BLUE}Timers disponibles:${NC}"
    systemctl list-timers --all --no-pager | grep -v "^$"
    systemctl --user list-timers --all --no-pager 2>/dev/null | grep -v "^$"
    
    echo ""
    read -p "Nombre del timer a eliminar: " timer_name
    read -p "Es timer de usuario? (y/N): " is_user_input
    
    if [ -z "$timer_name" ]; then
        log ERROR "Nombre del timer es requerido"
        return 1
    fi
    
    local is_user=false
    if [[ "$is_user_input" =~ ^[Yy] ]]; then
        is_user=true
    fi
    
    # Detener y deshabilitar timer
    if [ "$is_user" = true ]; then
        systemctl --user stop "${timer_name}.timer" 2>/dev/null
        systemctl --user disable "${timer_name}.timer" 2>/dev/null
        local service_file="$USER_SERVICES_DIR/${timer_name}.service"
        local timer_file="$USER_SERVICES_DIR/${timer_name}.timer"
    else
        if [ "$EUID" -ne 0 ]; then
            log ERROR "Eliminar timer de sistema requiere permisos de root"
            return 1
        fi
        systemctl stop "${timer_name}.timer" 2>/dev/null
        systemctl disable "${timer_name}.timer" 2>/dev/null
        local service_file="$SERVICES_DIR/${timer_name}.service"
        local timer_file="$SERVICES_DIR/${timer_name}.timer"
    fi
    
    # Eliminar archivos
    rm -f "$service_file" "$timer_file"
    
    # Recargar systemd
    if [ "$is_user" = true ]; then
        systemctl --user daemon-reload
    else
        systemctl daemon-reload
    fi
    
    log SUCCESS "Timer $timer_name eliminado"
}

# Mostrar ejemplo de timer
show_timer_example() {
    log HEADER "Ejemplo de Timer Completo"
    
    cat << 'EOF'

=== Ejemplo: Timer de Backup Diario ===

1. Archivo de servicio (backup-daily.service):

[Unit]
Description=Backup diario de archivos importantes
Wants=backup-daily.timer

[Service]
Type=oneshot
User=backup
ExecStart=/usr/local/bin/backup-script.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

2. Archivo de timer (backup-daily.timer):

[Unit]
Description=Timer para backup diario
Requires=backup-daily.service

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target

3. Comandos para activar:

sudo systemctl daemon-reload
sudo systemctl enable backup-daily.timer
sudo systemctl start backup-daily.timer

4. Verificar estado:

systemctl status backup-daily.timer
systemctl list-timers backup-daily.timer

=== Especificaciones OnCalendar ===

Formato: DiasSemana Año-Mes-Dia Hora:Minuto:Segundo

Ejemplos:
  *-*-* 02:00:00        # Diario a las 2:00 AM
  Mon *-*-* 09:00:00    # Lunes a las 9:00 AM
  *-*-01 00:00:00       # Primer dia de cada mes
  *-01-01 00:00:00      # Año nuevo
  *:0/15                # Cada 15 minutos
  hourly                # Cada hora
  daily                 # Diario
  weekly                # Semanal
  monthly               # Mensual

=== Opciones Utiles ===

[Timer]
OnCalendar=daily           # Horario
Persistent=true            # Ejecutar si se perdio por apagado
RandomizedDelaySec=300     # Delay aleatorio hasta 5 min
AccuracySec=1s            # Precision del timer

[Service]
Type=oneshot              # Ejecutar una vez
User=username             # Usuario especifico
Environment="VAR=value"   # Variables de entorno
WorkingDirectory=/path    # Directorio de trabajo
StandardOutput=journal    # Output a journal
StandardError=journal     # Errores a journal
EOF
}

# Analizar timer existente
analyze_timer() {
    read -p "Nombre del timer a analizar: " timer_name
    read -p "Es timer de usuario? (y/N): " is_user_input
    
    if [ -z "$timer_name" ]; then
        log ERROR "Nombre del timer es requerido"
        return 1
    fi
    
    local is_user=false
    if [[ "$is_user_input" =~ ^[Yy] ]]; then
        is_user=true
        local service_file="$USER_SERVICES_DIR/${timer_name}.service"
        local timer_file="$USER_SERVICES_DIR/${timer_name}.timer"
    else
        local service_file="$SERVICES_DIR/${timer_name}.service"
        local timer_file="$SERVICES_DIR/${timer_name}.timer"
    fi
    
    log HEADER "Analisis del Timer: $timer_name"
    
    # Verificar archivos
    if [ ! -f "$timer_file" ]; then
        log ERROR "Archivo de timer no encontrado: $timer_file"
        return 1
    fi
    
    if [ ! -f "$service_file" ]; then
        log ERROR "Archivo de servicio no encontrado: $service_file"
        return 1
    fi
    
    # Mostrar contenido de archivos
    echo -e "${BLUE}Archivo de timer:${NC} $timer_file"
    echo "----------------------------------------"
    cat "$timer_file"
    echo "----------------------------------------"
    
    echo -e "\n${BLUE}Archivo de servicio:${NC} $service_file"
    echo "----------------------------------------"
    cat "$service_file"
    echo "----------------------------------------"
    
    # Mostrar estado
    echo ""
    show_timer_status "$timer_name" "$is_user"
    
    # Mostrar proxima ejecucion
    echo -e "\n${BLUE}Proxima ejecucion:${NC}"
    if [ "$is_user" = true ]; then
        systemctl --user list-timers "${timer_name}.timer" --no-pager
    else
        systemctl list-timers "${timer_name}.timer" --no-pager
    fi
}

# Mostrar ayuda
show_help() {
    cat << EOF
Gestion de Systemd Timers

USAGE:
    $SCRIPT_NAME [COMANDO] [OPCIONES]

COMANDOS:
    check               Verificar systemd
    list                Listar timers activos
    create              Crear nuevo timer
    status TIMER        Mostrar estado de timer
    logs TIMER          Mostrar logs de timer
    remove              Eliminar timer
    analyze             Analizar timer existente
    example             Mostrar ejemplo completo
    help                Mostrar esta ayuda

EJEMPLOS:
    $SCRIPT_NAME check              # Verificar systemd
    $SCRIPT_NAME list               # Ver timers activos
    $SCRIPT_NAME create             # Crear nuevo timer
    $SCRIPT_NAME status mi-timer    # Ver estado de timer
    $SCRIPT_NAME logs mi-timer      # Ver logs de timer

DIRECTORIOS:
    Sistema:    $SERVICES_DIR
    Usuario:    $USER_SERVICES_DIR

COMANDOS SYSTEMCTL UTILES:
    systemctl list-timers              # Ver todos los timers
    systemctl status timer.timer       # Estado de timer
    journalctl -u timer.service        # Logs de servicio
    systemctl daemon-reload            # Recargar configuracion
EOF
}

# Funcion principal
main() {
    local command="${1:-list}"
    shift 2>/dev/null || true
    
    case "$command" in
        check)
            check_systemd
            ;;
        list)
            list_timers
            ;;
        create)
            create_timer
            ;;
        status)
            if [ -n "$1" ]; then
                show_timer_status "$1"
            else
                log ERROR "Se requiere nombre del timer"
                log INFO "Uso: $SCRIPT_NAME status NOMBRE_TIMER"
            fi
            ;;
        logs)
            show_timer_logs "$1"
            ;;
        remove)
            remove_timer
            ;;
        analyze)
            analyze_timer
            ;;
        example)
            show_timer_example
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

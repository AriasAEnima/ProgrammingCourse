#!/bin/bash

# 🚀 CLI Profesional Completo
# Descripción: Herramienta de línea de comandos con todas las características profesionales
# Uso: ./04_professional_cli.sh [comando] [opciones] [argumentos]

# Información del script
SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="2.0.0"
AUTHOR="Programming Course"
LICENSE="MIT"

# Configuración de directorios
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"

APP_CONFIG_DIR="$CONFIG_HOME/professional_cli"
APP_DATA_DIR="$DATA_HOME/professional_cli"
APP_CACHE_DIR="$CACHE_HOME/professional_cli"

CONFIG_FILE="$APP_CONFIG_DIR/config.conf"
LOG_FILE="$APP_DATA_DIR/app.log"
HISTORY_FILE="$APP_DATA_DIR/history.log"
PID_FILE="$APP_CACHE_DIR/cli.pid"

# Configuración por defecto
declare -A DEFAULT_CONFIG=(
    ["app.name"]="Professional CLI"
    ["app.debug"]="false"
    ["app.verbose"]="false"
    ["app.log_level"]="info"
    ["app.color_output"]="true"
    ["app.interactive_mode"]="true"
    ["output.format"]="table"
    ["output.pager"]="auto"
    ["network.timeout"]="30"
    ["network.retries"]="3"
    ["cache.enabled"]="true"
    ["cache.ttl"]="3600"
)

# Variables globales
declare -A CONFIG=()
VERBOSE=false
DEBUG=false
QUIET=false
DRY_RUN=false
FORCE=false
COLOR_OUTPUT=true
INTERACTIVE_MODE=true
OUTPUT_FORMAT="table"
LOG_LEVEL="info"

# Colores y estilos
if [[ -t 1 && "$COLOR_OUTPUT" == "true" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    PURPLE='\033[0;35m'
    CYAN='\033[0;36m'
    WHITE='\033[1;37m'
    BOLD='\033[1m'
    DIM='\033[2m'
    UNDERLINE='\033[4m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' PURPLE='' CYAN='' WHITE='' BOLD='' DIM='' UNDERLINE='' NC=''
fi

# Códigos de salida estándar
readonly EXIT_SUCCESS=0
readonly EXIT_FAILURE=1
readonly EXIT_INVALID_ARGS=2
readonly EXIT_CONFIG_ERROR=3
readonly EXIT_NETWORK_ERROR=4
readonly EXIT_PERMISSION_ERROR=5

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

# Función de logging con rotación
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local pid=$$
    
    # Verificar nivel de log
    case "$LOG_LEVEL" in
        debug) allowed_levels="debug info warn error fatal" ;;
        info)  allowed_levels="info warn error fatal" ;;
        warn)  allowed_levels="warn error fatal" ;;
        error) allowed_levels="error fatal" ;;
        fatal) allowed_levels="fatal" ;;
    esac
    
    if [[ ! " $allowed_levels " =~ " $level " ]]; then
        return 0
    fi
    
    # No mostrar en modo quiet excepto errores críticos
    if [[ "$QUIET" == true && ! "$level" =~ ^(error|fatal)$ ]]; then
        return 0
    fi
    
    local color=""
    local output=1
    
    case "$level" in
        debug)  color="$PURPLE"; output=2 ;;
        info)   color="$BLUE" ;;
        warn)   color="$YELLOW"; output=2 ;;
        error)  color="$RED"; output=2 ;;
        fatal)  color="$RED$BOLD"; output=2 ;;
    esac
    
    local formatted_message="${color}[${level^^} $timestamp]${NC} $message"
    
    # Output a consola
    echo -e "$formatted_message" >&$output
    
    # Log a archivo si está configurado
    if [[ -n "$LOG_FILE" && -w "$(dirname "$LOG_FILE")" ]]; then
        echo "[$level $timestamp] PID:$pid $message" >> "$LOG_FILE"
        
        # Rotación simple del log (mantener últimas 1000 líneas)
        if [[ $(wc -l < "$LOG_FILE" 2>/dev/null || echo 0) -gt 1000 ]]; then
            tail -n 500 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
        fi
    fi
}

# Funciones de logging específicas
debug() { log debug "$@"; }
info() { log info "$@"; }
warn() { log warn "$@"; }
error() { log error "$@"; }
fatal() { log fatal "$@"; exit $EXIT_FAILURE; }

# Función para mostrar barras de progreso
progress_bar() {
    local current="$1"
    local total="$2"
    local width="${3:-50}"
    local char="${4:-█}"
    
    local percentage=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))
    
    printf "\r${BLUE}Progress: [${GREEN}"
    printf "%*s" "$filled" "" | tr ' ' "$char"
    printf "${NC}"
    printf "%*s" "$empty" ""
    printf "${BLUE}] %d%% (%d/%d)${NC}" "$percentage" "$current" "$total"
    
    if [[ "$current" -eq "$total" ]]; then
        printf "\n"
    fi
}

# Función para mostrar spinners
spinner() {
    local pid=$1
    local message="${2:-Processing...}"
    local delay=0.1
    local spinstr='|/-\'
    
    while kill -0 "$pid" 2>/dev/null; do
        local temp=${spinstr#?}
        printf "\r${CYAN}%s %c${NC}" "$message" "$spinstr"
        spinstr=$temp${spinstr%"$temp"}
        sleep $delay
    done
    printf "\r%*s\r" $((${#message} + 2)) ""
}

# =============================================================================
# GESTIÓN DE CONFIGURACIÓN
# =============================================================================

init_directories() {
    local dirs=("$APP_CONFIG_DIR" "$APP_DATA_DIR" "$APP_CACHE_DIR")
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir" || {
                error "No se pudo crear directorio: $dir"
                return $EXIT_PERMISSION_ERROR
            }
        fi
    done
}

load_config() {
    # Cargar configuración por defecto
    for key in "${!DEFAULT_CONFIG[@]}"; do
        CONFIG["$key"]="${DEFAULT_CONFIG[$key]}"
    done
    
    # Cargar desde archivo de configuración
    if [[ -f "$CONFIG_FILE" ]]; then
        debug "Cargando configuración desde: $CONFIG_FILE"
        
        local section=""
        while IFS= read -r line; do
            line=$(echo "$line" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
            
            if [[ -z "$line" || "$line" =~ ^[#;] ]]; then
                continue
            fi
            
            if [[ "$line" =~ ^\[([^]]+)\]$ ]]; then
                section="${BASH_REMATCH[1]}"
                continue
            fi
            
            if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
                local key="${BASH_REMATCH[1]}"
                local value="${BASH_REMATCH[2]}"
                key=$(echo "$key" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
                value=$(echo "$value" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//')
                
                if [[ -n "$section" ]]; then
                    CONFIG["$section.$key"]="$value"
                else
                    CONFIG["$key"]="$value"
                fi
            fi
        done < "$CONFIG_FILE"
    fi
    
    # Aplicar configuración a variables globales
    VERBOSE=$(get_config "app.verbose" "false")
    DEBUG=$(get_config "app.debug" "false")
    COLOR_OUTPUT=$(get_config "app.color_output" "true")
    INTERACTIVE_MODE=$(get_config "app.interactive_mode" "true")
    OUTPUT_FORMAT=$(get_config "output.format" "table")
    LOG_LEVEL=$(get_config "app.log_level" "info")
    
    [[ "$VERBOSE" == "true" ]] && VERBOSE=true || VERBOSE=false
    [[ "$DEBUG" == "true" ]] && DEBUG=true || DEBUG=false
}

get_config() {
    local key="$1"
    local default_value="$2"
    echo "${CONFIG[$key]:-$default_value}"
}

save_config() {
    init_directories || return $?
    
    info "Guardando configuración en: $CONFIG_FILE"
    
    # Crear backup
    if [[ -f "$CONFIG_FILE" ]]; then
        cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Organizar por secciones
    declare -A sections
    for key in "${!CONFIG[@]}"; do
        if [[ "$key" =~ ^([^.]+)\.(.+)$ ]]; then
            local section="${BASH_REMATCH[1]}"
            local setting="${BASH_REMATCH[2]}"
            sections["$section"]+="$setting = ${CONFIG[$key]}\n"
        fi
    done
    
    # Escribir archivo
    {
        echo "# Configuración de Professional CLI"
        echo "# Actualizado el $(date)"
        echo ""
        
        for section in $(printf '%s\n' "${!sections[@]}" | sort); do
            echo "[$section]"
            echo -e "${sections[$section]}"
        done
    } > "$CONFIG_FILE"
    
    info "Configuración guardada exitosamente"
}

# =============================================================================
# FUNCIONES DE PRESENTACIÓN
# =============================================================================

print_table() {
    local -n data=$1
    local headers=("${@:2}")
    
    if [[ ${#data[@]} -eq 0 ]]; then
        warn "No hay datos para mostrar"
        return
    fi
    
    # Calcular anchos de columnas
    local -a widths
    for ((i=0; i<${#headers[@]}; i++)); do
        widths[i]=${#headers[i]}
    done
    
    for row in "${data[@]}"; do
        IFS='|' read -ra fields <<< "$row"
        for ((i=0; i<${#fields[@]}; i++)); do
            if [[ ${#fields[i]} -gt ${widths[i]:-0} ]]; then
                widths[i]=${#fields[i]}
            fi
        done
    done
    
    # Imprimir encabezados
    printf "${BOLD}"
    for ((i=0; i<${#headers[@]}; i++)); do
        printf "%-*s" $((widths[i] + 2)) "${headers[i]}"
    done
    printf "${NC}\n"
    
    # Línea separadora
    for ((i=0; i<${#headers[@]}; i++)); do
        printf "%*s" $((widths[i] + 2)) "" | tr ' ' '-'
    done
    printf "\n"
    
    # Datos
    for row in "${data[@]}"; do
        IFS='|' read -ra fields <<< "$row"
        for ((i=0; i<${#fields[@]}; i++)); do
            printf "%-*s" $((widths[i] + 2)) "${fields[i]:-}"
        done
        printf "\n"
    done
}

print_json() {
    local -n data=$1
    
    echo "["
    local first=true
    for row in "${data[@]}"; do
        if [[ "$first" == false ]]; then
            echo ","
        fi
        echo "  {\"data\": \"$row\"}"
        first=false
    done
    echo "]"
}

print_csv() {
    local -n data=$1
    local headers=("${@:2}")
    
    # Imprimir encabezados
    IFS=','; echo "${headers[*]}"
    
    # Imprimir datos
    for row in "${data[@]}"; do
        echo "$row" | tr '|' ','
    done
}

# =============================================================================
# COMANDOS PRINCIPALES
# =============================================================================

cmd_status() {
    info "Estado del sistema:"
    
    local data=(
        "Version|$VERSION"
        "Config Dir|$APP_CONFIG_DIR"
        "Data Dir|$APP_DATA_DIR"
        "Cache Dir|$APP_CACHE_DIR"
        "Log Level|$LOG_LEVEL"
        "Output Format|$OUTPUT_FORMAT"
        "Interactive|$INTERACTIVE_MODE"
        "Debug Mode|$DEBUG"
    )
    
    case "$OUTPUT_FORMAT" in
        json) print_json data ;;
        csv) print_csv data "Property" "Value" ;;
        *) print_table data "Property" "Value" ;;
    esac
}

cmd_config() {
    local action="${1:-show}"
    shift 2>/dev/null || true
    
    case "$action" in
        show)
            info "Configuración actual:"
            local data=()
            for key in $(printf '%s\n' "${!CONFIG[@]}" | sort); do
                data+=("$key|${CONFIG[$key]}")
            done
            
            case "$OUTPUT_FORMAT" in
                json) print_json data ;;
                csv) print_csv data "Key" "Value" ;;
                *) print_table data "Key" "Value" ;;
            esac
            ;;
        
        set)
            if [[ -z "$1" || -z "$2" ]]; then
                error "Uso: config set <clave> <valor>"
                return $EXIT_INVALID_ARGS
            fi
            CONFIG["$1"]="$2"
            info "Configuración actualizada: $1 = $2"
            save_config
            ;;
        
        reset)
            if confirm "¿Restablecer configuración por defecto?"; then
                for key in "${!DEFAULT_CONFIG[@]}"; do
                    CONFIG["$key"]="${DEFAULT_CONFIG[$key]}"
                done
                save_config
                info "Configuración restablecida"
            fi
            ;;
        
        *)
            error "Acción de configuración no válida: $action"
            return $EXIT_INVALID_ARGS
            ;;
    esac
}

cmd_logs() {
    local action="${1:-show}"
    local lines="${2:-50}"
    
    case "$action" in
        show)
            if [[ -f "$LOG_FILE" ]]; then
                info "Últimas $lines líneas del log:"
                tail -n "$lines" "$LOG_FILE"
            else
                warn "Archivo de log no encontrado: $LOG_FILE"
            fi
            ;;
        
        clear)
            if confirm "¿Limpiar archivo de log?"; then
                > "$LOG_FILE"
                info "Log limpiado"
            fi
            ;;
        
        rotate)
            if [[ -f "$LOG_FILE" ]]; then
                local backup="$LOG_FILE.$(date +%Y%m%d_%H%M%S)"
                mv "$LOG_FILE" "$backup"
                info "Log rotado a: $backup"
            fi
            ;;
        
        *)
            error "Acción de log no válida: $action"
            return $EXIT_INVALID_ARGS
            ;;
    esac
}

cmd_test() {
    info "Ejecutando pruebas del sistema..."
    
    local tests_passed=0
    local tests_total=5
    
    # Test 1: Directorios
    info "Test 1/5: Verificando directorios..."
    if init_directories; then
        ((tests_passed++))
        info "✓ Directorios OK"
    else
        error "✗ Error en directorios"
    fi
    progress_bar 1 $tests_total
    
    # Test 2: Configuración
    info "Test 2/5: Verificando configuración..."
    if [[ -n "$(get_config "app.name")" ]]; then
        ((tests_passed++))
        info "✓ Configuración OK"
    else
        error "✗ Error en configuración"
    fi
    progress_bar 2 $tests_total
    
    # Test 3: Logging
    info "Test 3/5: Verificando logging..."
    if log info "Test message" && [[ -f "$LOG_FILE" ]]; then
        ((tests_passed++))
        info "✓ Logging OK"
    else
        error "✗ Error en logging"
    fi
    progress_bar 3 $tests_total
    
    # Test 4: Formato de salida
    info "Test 4/5: Verificando formatos de salida..."
    local test_data=("test1|value1" "test2|value2")
    if print_table test_data "Key" "Value" >/dev/null; then
        ((tests_passed++))
        info "✓ Formatos OK"
    else
        error "✗ Error en formatos"
    fi
    progress_bar 4 $tests_total
    
    # Test 5: Permisos
    info "Test 5/5: Verificando permisos..."
    if [[ -w "$APP_DATA_DIR" && -w "$APP_CONFIG_DIR" ]]; then
        ((tests_passed++))
        info "✓ Permisos OK"
    else
        error "✗ Error en permisos"
    fi
    progress_bar 5 $tests_total
    
    echo ""
    info "Pruebas completadas: $tests_passed/$tests_total pasaron"
    
    if [[ $tests_passed -eq $tests_total ]]; then
        info "✅ Todos los tests pasaron"
        return $EXIT_SUCCESS
    else
        error "❌ Algunos tests fallaron"
        return $EXIT_FAILURE
    fi
}

# =============================================================================
# FUNCIONES DE INTERACCIÓN
# =============================================================================

confirm() {
    local message="$1"
    local default="${2:-n}"
    
    if [[ "$FORCE" == "true" ]]; then
        return 0
    fi
    
    if [[ "$INTERACTIVE_MODE" != "true" ]]; then
        [[ "$default" == "y" ]] && return 0 || return 1
    fi
    
    local prompt="$message [y/N]: "
    if [[ "$default" == "y" ]]; then
        prompt="$message [Y/n]: "
    fi
    
    while true; do
        read -p "$prompt" response
        response=${response:-$default}
        
        case "$response" in
            [Yy]|[Yy][Ee][Ss]) return 0 ;;
            [Nn]|[Nn][Oo]) return 1 ;;
            *) echo "Por favor responde 'y' o 'n'" ;;
        esac
    done
}

select_option() {
    local prompt="$1"
    shift
    local options=("$@")
    
    if [[ "$INTERACTIVE_MODE" != "true" ]]; then
        echo "${options[0]}"
        return
    fi
    
    echo "$prompt"
    for ((i=0; i<${#options[@]}; i++)); do
        echo "  $((i+1)). ${options[i]}"
    done
    
    while true; do
        read -p "Selecciona una opción (1-${#options[@]}): " choice
        
        if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le ${#options[@]} ]]; then
            echo "${options[$((choice-1))]}"
            return
        else
            echo "Opción inválida. Introduce un número entre 1 y ${#options[@]}"
        fi
    done
}

# =============================================================================
# SISTEMA DE AYUDA
# =============================================================================

show_version() {
    cat << EOF
${BOLD}$SCRIPT_NAME${NC} v$VERSION

CLI profesional con características avanzadas de configuración,
logging, formateo de salida y manejo de errores.

Autor: $AUTHOR
Licencia: $LICENSE

Directorios:
  Config: $APP_CONFIG_DIR
  Data:   $APP_DATA_DIR
  Cache:  $APP_CACHE_DIR
EOF
}

show_help() {
    cat << EOF
${BOLD}$SCRIPT_NAME${NC} - CLI Profesional Completo

${UNDERLINE}USAGE:${NC}
    $SCRIPT_NAME [OPCIONES GLOBALES] <comando> [argumentos]

${UNDERLINE}COMANDOS:${NC}
    ${BOLD}status${NC}              Mostrar estado del sistema
    ${BOLD}config${NC} <acción>     Gestionar configuración
    ${BOLD}logs${NC} <acción>       Gestionar logs
    ${BOLD}test${NC}                Ejecutar pruebas del sistema
    ${BOLD}version${NC}             Mostrar información de versión
    ${BOLD}help${NC}                Mostrar esta ayuda

${UNDERLINE}OPCIONES GLOBALES:${NC}
    ${BOLD}-v, --verbose${NC}       Modo verboso
    ${BOLD}-q, --quiet${NC}         Modo silencioso
    ${BOLD}-d, --debug${NC}         Modo debug
    ${BOLD}--dry-run${NC}           Simular operaciones
    ${BOLD}--force${NC}             Forzar operaciones sin confirmación
    ${BOLD}--no-color${NC}          Deshabilitar colores
    ${BOLD}--format FORMAT${NC}     Formato de salida: table|json|csv
    ${BOLD}--log-level LEVEL${NC}   Nivel de log: debug|info|warn|error|fatal
    ${BOLD}--config FILE${NC}       Archivo de configuración personalizado

${UNDERLINE}SUBCOMANDOS:${NC}
    ${BOLD}config show${NC}         Mostrar configuración actual
    ${BOLD}config set KEY VALUE${NC} Establecer valor de configuración
    ${BOLD}config reset${NC}        Restablecer configuración por defecto
    
    ${BOLD}logs show [N]${NC}       Mostrar últimas N líneas del log
    ${BOLD}logs clear${NC}          Limpiar archivo de log
    ${BOLD}logs rotate${NC}         Rotar archivo de log

${UNDERLINE}EJEMPLOS:${NC}
    $SCRIPT_NAME status
    $SCRIPT_NAME --format json config show
    $SCRIPT_NAME --verbose test
    $SCRIPT_NAME config set output.format csv
    $SCRIPT_NAME logs show 100
    $SCRIPT_NAME --dry-run --debug test

${UNDERLINE}CÓDIGOS DE SALIDA:${NC}
    0   Éxito
    1   Error general
    2   Argumentos inválidos
    3   Error de configuración
    4   Error de red
    5   Error de permisos

${UNDERLINE}ARCHIVOS:${NC}
    Config: $CONFIG_FILE
    Logs:   $LOG_FILE
    Data:   $APP_DATA_DIR

Para más información, visita: https://github.com/example/professional-cli
EOF
}

# =============================================================================
# PARSING DE ARGUMENTOS
# =============================================================================

parse_global_options() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                LOG_LEVEL="debug"
                shift
                ;;
            -q|--quiet)
                QUIET=true
                shift
                ;;
            -d|--debug)
                DEBUG=true
                LOG_LEVEL="debug"
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --force)
                FORCE=true
                INTERACTIVE_MODE=false
                shift
                ;;
            --no-color)
                COLOR_OUTPUT=false
                shift
                ;;
            --format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            --log-level)
                LOG_LEVEL="$2"
                shift 2
                ;;
            --config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit $EXIT_SUCCESS
                ;;
            --version)
                show_version
                exit $EXIT_SUCCESS
                ;;
            --)
                shift
                break
                ;;
            -*)
                error "Opción no reconocida: $1"
                exit $EXIT_INVALID_ARGS
                ;;
            *)
                # Primer argumento no-opción es el comando
                break
                ;;
        esac
    done
    
    # Devolver argumentos restantes
    echo "$@"
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

main() {
    # Guardar PID
    echo $$ > "$PID_FILE" 2>/dev/null || true
    
    # Configurar trap para limpieza
    trap 'rm -f "$PID_FILE" 2>/dev/null || true' EXIT
    
    # Inicializar directorios y configuración
    init_directories || exit $EXIT_CONFIG_ERROR
    load_config
    
    # Parsear opciones globales
    local remaining_args
    remaining_args=$(parse_global_options "$@")
    eval set -- "$remaining_args"
    
    # Recargar configuración con valores de línea de comandos
    CONFIG["app.verbose"]="$VERBOSE"
    CONFIG["app.debug"]="$DEBUG"
    CONFIG["app.color_output"]="$COLOR_OUTPUT"
    CONFIG["output.format"]="$OUTPUT_FORMAT"
    CONFIG["app.log_level"]="$LOG_LEVEL"
    
    # Obtener comando
    local command="${1:-help}"
    shift 2>/dev/null || true
    
    debug "Ejecutando comando: $command con argumentos: $*"
    
    # Ejecutar comando
    case "$command" in
        status)
            cmd_status "$@"
            ;;
        config)
            cmd_config "$@"
            ;;
        logs)
            cmd_logs "$@"
            ;;
        test)
            cmd_test "$@"
            ;;
        version)
            show_version
            ;;
        help)
            show_help
            ;;
        *)
            error "Comando no reconocido: $command"
            echo ""
            info "Usa '$SCRIPT_NAME help' para ver comandos disponibles"
            exit $EXIT_INVALID_ARGS
            ;;
    esac
    
    local exit_code=$?
    debug "Comando completado con código de salida: $exit_code"
    exit $exit_code
}

# Ejecutar función principal solo si el script es ejecutado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

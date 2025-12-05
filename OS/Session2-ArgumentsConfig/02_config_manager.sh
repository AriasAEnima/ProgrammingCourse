#!/bin/bash

# 🔧 Gestor de Configuración Avanzado
# Descripción: Sistema completo para manejo de configuración con múltiples fuentes
# Uso: ./02_config_manager.sh [comando] [opciones]

SCRIPT_NAME=$(basename "$0")
VERSION="1.0.0"

# Directorios de configuración siguiendo XDG Base Directory
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
CONFIG_DIR="$CONFIG_HOME/config_manager"
GLOBAL_CONFIG_DIR="/etc/config_manager"
LOCAL_CONFIG_FILE="./config_manager.conf"

# Archivos de configuración
USER_CONFIG="$CONFIG_DIR/config.conf"
GLOBAL_CONFIG="$GLOBAL_CONFIG_DIR/config.conf"

# Configuración por defecto
declare -A DEFAULT_CONFIG=(
    ["app.name"]="Config Manager"
    ["app.version"]="1.0.0"
    ["app.debug"]="false"
    ["database.host"]="localhost"
    ["database.port"]="5432"
    ["database.name"]="myapp"
    ["logging.level"]="info"
    ["logging.file"]="/var/log/app.log"
    ["server.host"]="0.0.0.0"
    ["server.port"]="8080"
    ["cache.enabled"]="true"
    ["cache.ttl"]="3600"
)

# Configuración actual en memoria
declare -A CURRENT_CONFIG=()

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función de logging
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
            echo -e "${RED}[ERROR $timestamp]${NC} $message" >&2
            ;;
        DEBUG)
            echo -e "${PURPLE}[DEBUG $timestamp]${NC} $message" >&2
            ;;
    esac
}

# Función para inicializar directorios de configuración
init_config_dirs() {
    if [[ ! -d "$CONFIG_DIR" ]]; then
        log INFO "Creando directorio de configuración: $CONFIG_DIR"
        mkdir -p "$CONFIG_DIR" || {
            log ERROR "No se pudo crear directorio de configuración"
            return 1
        }
    fi
}

# Función para crear archivo de configuración por defecto
create_default_config() {
    local config_file="$1"
    local config_dir=$(dirname "$config_file")
    
    log INFO "Creando configuración por defecto: $config_file"
    
    mkdir -p "$config_dir" 2>/dev/null
    
    cat > "$config_file" << EOF
# Configuración de Config Manager
# Generado automáticamente el $(date)

[app]
name = ${DEFAULT_CONFIG["app.name"]}
version = ${DEFAULT_CONFIG["app.version"]}
debug = ${DEFAULT_CONFIG["app.debug"]}

[database]
host = ${DEFAULT_CONFIG["database.host"]}
port = ${DEFAULT_CONFIG["database.port"]}
name = ${DEFAULT_CONFIG["database.name"]}

[logging]
level = ${DEFAULT_CONFIG["logging.level"]}
file = ${DEFAULT_CONFIG["logging.file"]}

[server]
host = ${DEFAULT_CONFIG["server.host"]}
port = ${DEFAULT_CONFIG["server.port"]}

[cache]
enabled = ${DEFAULT_CONFIG["cache.enabled"]}
ttl = ${DEFAULT_CONFIG["cache.ttl"]}
EOF
    
    log SUCCESS "Configuración por defecto creada exitosamente"
}

# Función para leer archivo de configuración INI
read_config_file() {
    local config_file="$1"
    local section=""
    
    if [[ ! -f "$config_file" ]]; then
        return 1
    fi
    
    log DEBUG "Leyendo configuración de: $config_file"
    
    while IFS= read -r line; do
        # Remover espacios en blanco al inicio y final
        line=$(echo "$line" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
        
        # Saltar líneas vacías y comentarios
        if [[ -z "$line" || "$line" =~ ^[#;] ]]; then
            continue
        fi
        
        # Detectar secciones [section]
        if [[ "$line" =~ ^\[([^]]+)\]$ ]]; then
            section="${BASH_REMATCH[1]}"
            continue
        fi
        
        # Leer pares clave=valor
        if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"
            
            # Limpiar espacios
            key=$(echo "$key" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
            value=$(echo "$value" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
            
            # Remover comillas si existen
            value=$(echo "$value" | sed 's/^"//; s/"$//')
            
            # Construir clave completa con sección
            if [[ -n "$section" ]]; then
                CURRENT_CONFIG["$section.$key"]="$value"
            else
                CURRENT_CONFIG["$key"]="$value"
            fi
        fi
    done < "$config_file"
}

# Función para cargar configuración desde múltiples fuentes
load_config() {
    log INFO "Cargando configuración desde múltiples fuentes..."
    
    # 1. Cargar configuración por defecto
    for key in "${!DEFAULT_CONFIG[@]}"; do
        CURRENT_CONFIG["$key"]="${DEFAULT_CONFIG[$key]}"
    done
    log DEBUG "Configuración por defecto cargada"
    
    # 2. Cargar configuración global del sistema
    if [[ -f "$GLOBAL_CONFIG" ]]; then
        read_config_file "$GLOBAL_CONFIG"
        log DEBUG "Configuración global cargada"
    fi
    
    # 3. Cargar configuración del usuario
    if [[ -f "$USER_CONFIG" ]]; then
        read_config_file "$USER_CONFIG"
        log DEBUG "Configuración de usuario cargada"
    fi
    
    # 4. Cargar configuración local del proyecto
    if [[ -f "$LOCAL_CONFIG_FILE" ]]; then
        read_config_file "$LOCAL_CONFIG_FILE"
        log DEBUG "Configuración local cargada"
    fi
    
    # 5. Aplicar variables de entorno (formato: CM_SECTION_KEY)
    while IFS= read -r -d '' env_var; do
        if [[ "$env_var" =~ ^CM_([A-Z_]+)=(.*)$ ]]; then
            local env_key="${BASH_REMATCH[1]}"
            local env_value="${BASH_REMATCH[2]}"
            
            # Convertir CM_DATABASE_HOST a database.host
            env_key=$(echo "$env_key" | tr '[:upper:]' '[:lower:]' | sed 's/_/./g')
            CURRENT_CONFIG["$env_key"]="$env_value"
            log DEBUG "Variable de entorno aplicada: $env_key=$env_value"
        fi
    done < <(env -0 | grep -z "^CM_")
    
    log SUCCESS "Configuración cargada exitosamente"
}

# Función para obtener valor de configuración
get_config() {
    local key="$1"
    local default_value="$2"
    
    if [[ -n "${CURRENT_CONFIG[$key]:-}" ]]; then
        echo "${CURRENT_CONFIG[$key]}"
    elif [[ -n "$default_value" ]]; then
        echo "$default_value"
    else
        return 1
    fi
}

# Función para establecer valor de configuración
set_config() {
    local key="$1"
    local value="$2"
    local persistent="${3:-false}"
    
    CURRENT_CONFIG["$key"]="$value"
    log INFO "Configuración actualizada: $key=$value"
    
    if [[ "$persistent" == "true" ]]; then
        save_user_config
    fi
}

# Función para guardar configuración del usuario
save_user_config() {
    init_config_dirs || return 1
    
    log INFO "Guardando configuración de usuario: $USER_CONFIG"
    
    # Crear backup si existe
    if [[ -f "$USER_CONFIG" ]]; then
        cp "$USER_CONFIG" "$USER_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Organizar configuración por secciones
    declare -A sections
    for key in "${!CURRENT_CONFIG[@]}"; do
        if [[ "$key" =~ ^([^.]+)\.(.+)$ ]]; then
            local section="${BASH_REMATCH[1]}"
            local setting="${BASH_REMATCH[2]}"
            sections["$section"]+="$setting = ${CURRENT_CONFIG[$key]}\n"
        fi
    done
    
    # Escribir archivo de configuración
    {
        echo "# Configuración de usuario de Config Manager"
        echo "# Actualizado el $(date)"
        echo ""
        
        for section in $(printf '%s\n' "${!sections[@]}" | sort); do
            echo "[$section]"
            echo -e "${sections[$section]}"
        done
    } > "$USER_CONFIG"
    
    log SUCCESS "Configuración guardada exitosamente"
}

# Función para mostrar configuración actual
show_config() {
    local filter_pattern="${1:-.*}"
    
    echo -e "${CYAN}📋 Configuración Actual${NC}"
    echo "=================================="
    
    # Organizar por secciones
    declare -A sections
    for key in "${!CURRENT_CONFIG[@]}"; do
        if [[ "$key" =~ $filter_pattern ]]; then
            if [[ "$key" =~ ^([^.]+)\.(.+)$ ]]; then
                local section="${BASH_REMATCH[1]}"
                local setting="${BASH_REMATCH[2]}"
                sections["$section"]+="  $setting = ${CURRENT_CONFIG[$key]}\n"
            else
                sections["global"]+="  $key = ${CURRENT_CONFIG[$key]}\n"
            fi
        fi
    done
    
    for section in $(printf '%s\n' "${!sections[@]}" | sort); do
        echo -e "\n${YELLOW}[$section]${NC}"
        echo -e "${sections[$section]}"
    done
}

# Función para validar configuración
validate_config() {
    local errors=0
    
    log INFO "Validando configuración..."
    
    # Validar puerto de base de datos
    local db_port=$(get_config "database.port")
    if [[ ! "$db_port" =~ ^[0-9]+$ ]] || [[ "$db_port" -lt 1 ]] || [[ "$db_port" -gt 65535 ]]; then
        log ERROR "Puerto de base de datos inválido: $db_port"
        errors=$((errors + 1))
    fi
    
    # Validar puerto del servidor
    local server_port=$(get_config "server.port")
    if [[ ! "$server_port" =~ ^[0-9]+$ ]] || [[ "$server_port" -lt 1 ]] || [[ "$server_port" -gt 65535 ]]; then
        log ERROR "Puerto del servidor inválido: $server_port"
        errors=$((errors + 1))
    fi
    
    # Validar nivel de logging
    local log_level=$(get_config "logging.level")
    local valid_levels="debug info warn error"
    if [[ ! " $valid_levels " =~ " $log_level " ]]; then
        log ERROR "Nivel de logging inválido: $log_level"
        errors=$((errors + 1))
    fi
    
    # Validar TTL de caché
    local cache_ttl=$(get_config "cache.ttl")
    if [[ ! "$cache_ttl" =~ ^[0-9]+$ ]]; then
        log ERROR "TTL de caché inválido: $cache_ttl"
        errors=$((errors + 1))
    fi
    
    if [[ $errors -eq 0 ]]; then
        log SUCCESS "Configuración válida"
    else
        log ERROR "Se encontraron $errors errores de validación"
    fi
    
    return $errors
}

# Función para exportar configuración
export_config() {
    local format="${1:-ini}"
    local output_file="$2"
    
    case "$format" in
        ini)
            export_ini_config "$output_file"
            ;;
        json)
            export_json_config "$output_file"
            ;;
        env)
            export_env_config "$output_file"
            ;;
        *)
            log ERROR "Formato de exportación no soportado: $format"
            return 1
            ;;
    esac
}

# Función para exportar como INI
export_ini_config() {
    local output_file="$1"
    local output=""
    
    if [[ -n "$output_file" ]]; then
        output="> '$output_file'"
        log INFO "Exportando configuración INI a: $output_file"
    fi
    
    {
        echo "# Configuración exportada el $(date)"
        show_config
    } $(eval echo "$output")
    
    if [[ -n "$output_file" ]]; then
        log SUCCESS "Configuración exportada exitosamente"
    fi
}

# Función para exportar como JSON
export_json_config() {
    local output_file="$1"
    local output=""
    
    if [[ -n "$output_file" ]]; then
        output="> '$output_file'"
        log INFO "Exportando configuración JSON a: $output_file"
    fi
    
    {
        echo "{"
        local first=true
        
        # Organizar por secciones
        declare -A sections
        for key in "${!CURRENT_CONFIG[@]}"; do
            if [[ "$key" =~ ^([^.]+)\.(.+)$ ]]; then
                local section="${BASH_REMATCH[1]}"
                local setting="${BASH_REMATCH[2]}"
                sections["$section"]+="\"$setting\": \"${CURRENT_CONFIG[$key]}\","
            fi
        done
        
        for section in $(printf '%s\n' "${!sections[@]}" | sort); do
            if [[ "$first" == false ]]; then
                echo ","
            fi
            echo "  \"$section\": {"
            echo -n "    ${sections[$section]}" | sed 's/,$//'
            echo ""
            echo -n "  }"
            first=false
        done
        
        echo ""
        echo "}"
    } $(eval echo "$output")
    
    if [[ -n "$output_file" ]]; then
        log SUCCESS "Configuración JSON exportada exitosamente"
    fi
}

# Función para exportar como variables de entorno
export_env_config() {
    local output_file="$1"
    local output=""
    
    if [[ -n "$output_file" ]]; then
        output="> '$output_file'"
        log INFO "Exportando variables de entorno a: $output_file"
    fi
    
    {
        echo "# Variables de entorno generadas el $(date)"
        echo "# Cargar con: source $output_file"
        echo ""
        
        for key in $(printf '%s\n' "${!CURRENT_CONFIG[@]}" | sort); do
            local env_var="CM_$(echo "$key" | tr '[:lower:].' '[:upper:]_')"
            echo "export $env_var=\"${CURRENT_CONFIG[$key]}\""
        done
    } $(eval echo "$output")
    
    if [[ -n "$output_file" ]]; then
        log SUCCESS "Variables de entorno exportadas exitosamente"
    fi
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
🔧 Gestor de Configuración Avanzado v$VERSION

USAGE:
    $SCRIPT_NAME [COMANDO] [OPCIONES]

COMANDOS:
    init                    Inicializar configuración por defecto
    show [PATRÓN]          Mostrar configuración actual
    get CLAVE [DEFAULT]    Obtener valor de configuración
    set CLAVE VALOR [--save] Establecer valor de configuración
    validate               Validar configuración actual
    export [FORMAT] [FILE] Exportar configuración
    reset                  Restablecer a valores por defecto

FORMATOS DE EXPORTACIÓN:
    ini                    Formato INI (por defecto)
    json                   Formato JSON
    env                    Variables de entorno

ARCHIVOS DE CONFIGURACIÓN (orden de precedencia):
    1. Variables de entorno (CM_SECTION_KEY)
    2. Configuración local: ./config_manager.conf
    3. Configuración usuario: $USER_CONFIG
    4. Configuración global: $GLOBAL_CONFIG
    5. Valores por defecto

EJEMPLOS:
    $SCRIPT_NAME init                           # Crear configuración inicial
    $SCRIPT_NAME show                          # Mostrar toda la configuración
    $SCRIPT_NAME show database                 # Mostrar solo sección database
    $SCRIPT_NAME get database.host localhost   # Obtener host con default
    $SCRIPT_NAME set server.port 9000 --save   # Establecer puerto persistente
    $SCRIPT_NAME export json config.json       # Exportar a JSON
    $SCRIPT_NAME validate                      # Validar configuración

VARIABLES DE ENTORNO:
    CM_DATABASE_HOST                           # Equivale a database.host
    CM_SERVER_PORT                            # Equivale a server.port
    CM_LOGGING_LEVEL                          # Equivale a logging.level
EOF
}

# Función principal
main() {
    local command="${1:-show}"
    shift 2>/dev/null || true
    
    case "$command" in
        init)
            init_config_dirs
            create_default_config "$USER_CONFIG"
            ;;
        
        show)
            load_config
            show_config "$1"
            ;;
        
        get)
            if [[ -z "$1" ]]; then
                log ERROR "Se requiere especificar una clave"
                exit 1
            fi
            load_config
            get_config "$1" "$2"
            ;;
        
        set)
            if [[ -z "$1" || -z "$2" ]]; then
                log ERROR "Se requieren clave y valor"
                exit 1
            fi
            load_config
            local save_flag="false"
            if [[ "$3" == "--save" ]]; then
                save_flag="true"
            fi
            set_config "$1" "$2" "$save_flag"
            ;;
        
        validate)
            load_config
            validate_config
            ;;
        
        export)
            load_config
            export_config "$1" "$2"
            ;;
        
        reset)
            log WARNING "¿Estás seguro de que quieres restablecer la configuración? (y/N)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                create_default_config "$USER_CONFIG"
            else
                log INFO "Operación cancelada"
            fi
            ;;
        
        help|-h|--help)
            show_help
            ;;
        
        *)
            log ERROR "Comando no reconocido: $command"
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

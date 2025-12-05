#!/bin/bash

# 🌍 Manejador de Variables de Entorno
# Descripción: Sistema completo para gestión segura de variables de entorno
# Uso: ./03_env_handler.sh [comando] [opciones]

SCRIPT_NAME=$(basename "$0")
VERSION="1.0.0"

# Configuración
ENV_DIR="$HOME/.config/env_handler"
DEFAULT_ENV_FILE="$ENV_DIR/.env"
BACKUP_DIR="$ENV_DIR/backups"

# Archivos de entorno por tipo
DEV_ENV_FILE="$ENV_DIR/.env.development"
PROD_ENV_FILE="$ENV_DIR/.env.production"
TEST_ENV_FILE="$ENV_DIR/.env.test"
LOCAL_ENV_FILE="./.env"

# Variables sensibles (no mostrar en logs/output)
SENSITIVE_PATTERNS=("*PASSWORD*" "*SECRET*" "*KEY*" "*TOKEN*" "*CREDENTIAL*")

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

# Función para verificar si una variable es sensible
is_sensitive() {
    local var_name="$1"
    
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        if [[ "$var_name" == $pattern ]]; then
            return 0
        fi
    done
    return 1
}

# Función para enmascarar valores sensibles
mask_sensitive_value() {
    local var_name="$1"
    local var_value="$2"
    
    if is_sensitive "$var_name"; then
        echo "***MASKED***"
    else
        echo "$var_value"
    fi
}

# Función para inicializar directorios
init_env_dirs() {
    if [[ ! -d "$ENV_DIR" ]]; then
        log INFO "Creando directorio de configuración: $ENV_DIR"
        mkdir -p "$ENV_DIR" || {
            log ERROR "No se pudo crear directorio de configuración"
            return 1
        }
    fi
    
    if [[ ! -d "$BACKUP_DIR" ]]; then
        mkdir -p "$BACKUP_DIR"
    fi
}

# Función para crear archivo .env por defecto
create_default_env() {
    local env_file="${1:-$DEFAULT_ENV_FILE}"
    local env_type="${2:-default}"
    
    log INFO "Creando archivo de entorno por defecto: $env_file"
    
    mkdir -p "$(dirname "$env_file")"
    
    cat > "$env_file" << EOF
# Variables de Entorno - $env_type
# Generado automáticamente el $(date)

# Configuración de la aplicación
APP_NAME=MyApplication
APP_VERSION=1.0.0
APP_ENV=$env_type
APP_DEBUG=false

# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_$env_type
DB_USER=myapp_user
DB_PASSWORD=secure_password_here

# Redis Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Keys (ejemplo)
API_SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Configuración del servidor
SERVER_HOST=0.0.0.0
SERVER_PORT=8080

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/myapp.log

# Características opcionales
FEATURE_ANALYTICS=true
FEATURE_DEBUG_MODE=false
EOF
    
    log SUCCESS "Archivo de entorno creado: $env_file"
}

# Función para cargar variables de entorno desde archivo
load_env_file() {
    local env_file="$1"
    local export_vars="${2:-false}"
    
    if [[ ! -f "$env_file" ]]; then
        log ERROR "Archivo de entorno no encontrado: $env_file"
        return 1
    fi
    
    log INFO "Cargando variables de entorno desde: $env_file"
    
    local count=0
    while IFS= read -r line; do
        # Saltar líneas vacías y comentarios
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Procesar líneas con formato VAR=value
        if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
            local var_name="${BASH_REMATCH[1]}"
            local var_value="${BASH_REMATCH[2]}"
            
            # Remover comillas si existen
            var_value=$(echo "$var_value" | sed 's/^"//; s/"$//')
            
            if [[ "$export_vars" == "true" ]]; then
                export "$var_name"="$var_value"
                log DEBUG "Variable exportada: $var_name=$(mask_sensitive_value "$var_name" "$var_value")"
            else
                log DEBUG "Variable encontrada: $var_name=$(mask_sensitive_value "$var_name" "$var_value")"
            fi
            
            count=$((count + 1))
        fi
    done < "$env_file"
    
    log SUCCESS "Se cargaron $count variables de entorno"
}

# Función para mostrar variables de entorno
show_env_vars() {
    local filter_pattern="${1:-.*}"
    local show_values="${2:-true}"
    local env_file="$3"
    
    echo -e "${CYAN}🌍 Variables de Entorno${NC}"
    echo "=================================="
    
    if [[ -n "$env_file" ]]; then
        echo -e "${YELLOW}Archivo: $env_file${NC}\n"
        
        if [[ ! -f "$env_file" ]]; then
            log ERROR "Archivo no encontrado: $env_file"
            return 1
        fi
        
        # Mostrar variables del archivo
        while IFS= read -r line; do
            if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
                local var_name="${BASH_REMATCH[1]}"
                local var_value="${BASH_REMATCH[2]}"
                
                if [[ "$var_name" =~ $filter_pattern ]]; then
                    var_value=$(echo "$var_value" | sed 's/^"//; s/"$//')
                    
                    if [[ "$show_values" == "true" ]]; then
                        echo "  $var_name = $(mask_sensitive_value "$var_name" "$var_value")"
                    else
                        echo "  $var_name"
                    fi
                fi
            fi
        done < "$env_file"
    else
        # Mostrar variables del entorno actual
        env | grep -E "^[A-Za-z_][A-Za-z0-9_]*=" | while IFS= read -r env_var; do
            local var_name="${env_var%%=*}"
            local var_value="${env_var#*=}"
            
            if [[ "$var_name" =~ $filter_pattern ]]; then
                if [[ "$show_values" == "true" ]]; then
                    echo "  $var_name = $(mask_sensitive_value "$var_name" "$var_value")"
                else
                    echo "  $var_name"
                fi
            fi
        done | sort
    fi
}

# Función para establecer variable de entorno
set_env_var() {
    local var_name="$1"
    local var_value="$2"
    local persistent="${3:-false}"
    local env_file="${4:-$DEFAULT_ENV_FILE}"
    
    if [[ -z "$var_name" || -z "$var_value" ]]; then
        log ERROR "Se requieren nombre y valor de la variable"
        return 1
    fi
    
    # Validar nombre de variable
    if [[ ! "$var_name" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
        log ERROR "Nombre de variable inválido: $var_name"
        return 1
    fi
    
    # Establecer en el entorno actual
    export "$var_name"="$var_value"
    log INFO "Variable establecida: $var_name=$(mask_sensitive_value "$var_name" "$var_value")"
    
    # Guardar persistentemente si se solicita
    if [[ "$persistent" == "true" ]]; then
        save_env_var "$var_name" "$var_value" "$env_file"
    fi
}

# Función para guardar variable en archivo
save_env_var() {
    local var_name="$1"
    local var_value="$2"
    local env_file="$3"
    
    init_env_dirs
    
    # Crear backup si el archivo existe
    if [[ -f "$env_file" ]]; then
        local backup_file="$BACKUP_DIR/$(basename "$env_file").$(date +%Y%m%d_%H%M%S)"
        cp "$env_file" "$backup_file"
        log DEBUG "Backup creado: $backup_file"
    fi
    
    # Crear archivo si no existe
    if [[ ! -f "$env_file" ]]; then
        mkdir -p "$(dirname "$env_file")"
        touch "$env_file"
    fi
    
    # Verificar si la variable ya existe en el archivo
    if grep -q "^$var_name=" "$env_file" 2>/dev/null; then
        # Actualizar variable existente
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i "" "s/^$var_name=.*/$var_name=\"$var_value\"/" "$env_file"
        else
            # Linux
            sed -i "s/^$var_name=.*/$var_name=\"$var_value\"/" "$env_file"
        fi
        log SUCCESS "Variable actualizada en $env_file"
    else
        # Agregar nueva variable
        echo "$var_name=\"$var_value\"" >> "$env_file"
        log SUCCESS "Variable agregada a $env_file"
    fi
}

# Función para eliminar variable de entorno
unset_env_var() {
    local var_name="$1"
    local persistent="${2:-false}"
    local env_file="${3:-$DEFAULT_ENV_FILE}"
    
    if [[ -z "$var_name" ]]; then
        log ERROR "Se requiere nombre de la variable"
        return 1
    fi
    
    # Eliminar del entorno actual
    unset "$var_name"
    log INFO "Variable eliminada del entorno: $var_name"
    
    # Eliminar del archivo si se solicita
    if [[ "$persistent" == "true" && -f "$env_file" ]]; then
        # Crear backup
        local backup_file="$BACKUP_DIR/$(basename "$env_file").$(date +%Y%m%d_%H%M%S)"
        cp "$env_file" "$backup_file"
        
        # Eliminar línea del archivo
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i "" "/^$var_name=/d" "$env_file"
        else
            # Linux
            sed -i "/^$var_name=/d" "$env_file"
        fi
        log SUCCESS "Variable eliminada de $env_file"
    fi
}

# Función para validar archivo de entorno
validate_env_file() {
    local env_file="$1"
    
    if [[ ! -f "$env_file" ]]; then
        log ERROR "Archivo no encontrado: $env_file"
        return 1
    fi
    
    log INFO "Validando archivo de entorno: $env_file"
    
    local line_num=0
    local errors=0
    local warnings=0
    
    while IFS= read -r line; do
        line_num=$((line_num + 1))
        
        # Saltar líneas vacías y comentarios
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Validar formato VAR=value
        if [[ ! "$line" =~ ^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*= ]]; then
            log ERROR "Línea $line_num: Formato inválido: $line"
            errors=$((errors + 1))
            continue
        fi
        
        # Extraer nombre y valor
        local var_name=$(echo "$line" | cut -d'=' -f1 | tr -d ' ')
        local var_value=$(echo "$line" | cut -d'=' -f2-)
        
        # Validar nombre de variable
        if [[ ! "$var_name" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
            log ERROR "Línea $line_num: Nombre de variable inválido: $var_name"
            errors=$((errors + 1))
        fi
        
        # Advertir sobre valores vacíos en variables sensibles
        if is_sensitive "$var_name" && [[ -z "$var_value" || "$var_value" =~ ^[\"\']*$ ]]; then
            log WARNING "Línea $line_num: Variable sensible con valor vacío: $var_name"
            warnings=$((warnings + 1))
        fi
        
        # Advertir sobre valores por defecto inseguros
        if is_sensitive "$var_name" && [[ "$var_value" =~ (password|secret|key|123|test|default) ]]; then
            log WARNING "Línea $line_num: Valor potencialmente inseguro: $var_name"
            warnings=$((warnings + 1))
        fi
    done < "$env_file"
    
    echo ""
    if [[ $errors -eq 0 ]]; then
        log SUCCESS "Validación completada: $errors errores, $warnings advertencias"
    else
        log ERROR "Validación fallida: $errors errores, $warnings advertencias"
    fi
    
    return $errors
}

# Función para comparar archivos de entorno
compare_env_files() {
    local file1="$1"
    local file2="$2"
    
    if [[ ! -f "$file1" || ! -f "$file2" ]]; then
        log ERROR "Uno o ambos archivos no existen"
        return 1
    fi
    
    log INFO "Comparando archivos de entorno:"
    log INFO "  Archivo 1: $file1"
    log INFO "  Archivo 2: $file2"
    
    # Obtener variables de cada archivo
    declare -A vars1 vars2
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
            vars1["${BASH_REMATCH[1]}"]="${BASH_REMATCH[2]}"
        fi
    done < "$file1"
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
            vars2["${BASH_REMATCH[1]}"]="${BASH_REMATCH[2]}"
        fi
    done < "$file2"
    
    echo ""
    echo -e "${CYAN}Resultados de la comparación:${NC}"
    echo "=================================="
    
    # Variables solo en archivo 1
    echo -e "\n${YELLOW}Solo en $file1:${NC}"
    for var in "${!vars1[@]}"; do
        if [[ -z "${vars2[$var]:-}" ]]; then
            echo "  + $var = $(mask_sensitive_value "$var" "${vars1[$var]}")"
        fi
    done
    
    # Variables solo en archivo 2
    echo -e "\n${YELLOW}Solo en $file2:${NC}"
    for var in "${!vars2[@]}"; do
        if [[ -z "${vars1[$var]:-}" ]]; then
            echo "  + $var = $(mask_sensitive_value "$var" "${vars2[$var]}")"
        fi
    done
    
    # Variables con valores diferentes
    echo -e "\n${YELLOW}Valores diferentes:${NC}"
    for var in "${!vars1[@]}"; do
        if [[ -n "${vars2[$var]:-}" && "${vars1[$var]}" != "${vars2[$var]}" ]]; then
            echo "  ~ $var:"
            echo "    $file1: $(mask_sensitive_value "$var" "${vars1[$var]}")"
            echo "    $file2: $(mask_sensitive_value "$var" "${vars2[$var]}")"
        fi
    done
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
🌍 Manejador de Variables de Entorno v$VERSION

USAGE:
    $SCRIPT_NAME [COMANDO] [OPCIONES]

COMANDOS:
    init [TIPO]                 Crear archivo .env por defecto
    load ARCHIVO [--export]     Cargar variables desde archivo
    show [PATRÓN] [ARCHIVO]     Mostrar variables de entorno
    set VAR VALOR [--save] [ARCHIVO] Establecer variable
    unset VAR [--save] [ARCHIVO] Eliminar variable
    validate ARCHIVO            Validar archivo .env
    compare ARCHIVO1 ARCHIVO2   Comparar dos archivos .env

TIPOS DE ENTORNO:
    dev, development           Configuración de desarrollo
    prod, production          Configuración de producción
    test, testing             Configuración de pruebas

OPCIONES:
    --export                  Exportar variables al entorno
    --save                    Guardar cambios persistentemente
    --no-mask                 Mostrar valores sensibles sin enmascarar
    -h, --help                Mostrar esta ayuda

ARCHIVOS:
    Por defecto: $DEFAULT_ENV_FILE
    Desarrollo:  $DEV_ENV_FILE
    Producción:  $PROD_ENV_FILE
    Pruebas:     $TEST_ENV_FILE
    Local:       ./.env

EJEMPLOS:
    $SCRIPT_NAME init dev                           # Crear .env de desarrollo
    $SCRIPT_NAME load .env --export                 # Cargar y exportar variables
    $SCRIPT_NAME show "DB_*"                       # Mostrar variables de DB
    $SCRIPT_NAME set API_KEY "secret123" --save     # Establecer clave API
    $SCRIPT_NAME validate .env.production           # Validar archivo
    $SCRIPT_NAME compare .env.dev .env.prod         # Comparar entornos

SEGURIDAD:
    - Variables sensibles se enmascaran automáticamente
    - Se crean backups antes de modificar archivos
    - Validación de formatos y valores inseguros

VARIABLES SENSIBLES:
    ${SENSITIVE_PATTERNS[*]}
EOF
}

# Función principal
main() {
    local command="${1:-show}"
    shift 2>/dev/null || true
    
    case "$command" in
        init)
            init_env_dirs
            local env_type="${1:-default}"
            local env_file
            
            case "$env_type" in
                dev|development) env_file="$DEV_ENV_FILE" ;;
                prod|production) env_file="$PROD_ENV_FILE" ;;
                test|testing) env_file="$TEST_ENV_FILE" ;;
                *) env_file="$DEFAULT_ENV_FILE" ;;
            esac
            
            create_default_env "$env_file" "$env_type"
            ;;
        
        load)
            if [[ -z "$1" ]]; then
                log ERROR "Se requiere especificar archivo de entorno"
                exit 1
            fi
            local export_flag="false"
            if [[ "$2" == "--export" ]]; then
                export_flag="true"
            fi
            load_env_file "$1" "$export_flag"
            ;;
        
        show)
            local pattern="${1:-.*}"
            local env_file="$2"
            local show_values="true"
            if [[ "$3" == "--no-mask" ]]; then
                show_values="true"
            fi
            show_env_vars "$pattern" "$show_values" "$env_file"
            ;;
        
        set)
            if [[ -z "$1" || -z "$2" ]]; then
                log ERROR "Se requieren nombre y valor de la variable"
                exit 1
            fi
            local save_flag="false"
            local env_file="$DEFAULT_ENV_FILE"
            
            shift 2
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --save) save_flag="true"; shift ;;
                    *) env_file="$1"; shift ;;
                esac
            done
            
            set_env_var "$1" "$2" "$save_flag" "$env_file"
            ;;
        
        unset)
            if [[ -z "$1" ]]; then
                log ERROR "Se requiere nombre de la variable"
                exit 1
            fi
            local save_flag="false"
            local env_file="$DEFAULT_ENV_FILE"
            
            shift
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --save) save_flag="true"; shift ;;
                    *) env_file="$1"; shift ;;
                esac
            done
            
            unset_env_var "$1" "$save_flag" "$env_file"
            ;;
        
        validate)
            if [[ -z "$1" ]]; then
                log ERROR "Se requiere especificar archivo de entorno"
                exit 1
            fi
            validate_env_file "$1"
            ;;
        
        compare)
            if [[ -z "$1" || -z "$2" ]]; then
                log ERROR "Se requieren dos archivos para comparar"
                exit 1
            fi
            compare_env_files "$1" "$2"
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

#!/bin/bash

# ⚙️ Sistema Avanzado de Parsing de Argumentos
# Descripción: Implementación robusta para manejo de argumentos de línea de comandos
# Uso: ./01_advanced_args.sh [opciones] [argumentos]

# Configuración por defecto
SCRIPT_NAME=$(basename "$0")
VERSION="1.0.0"
DEFAULT_OUTPUT_FORMAT="text"
DEFAULT_LOG_LEVEL="info"

# Variables de configuración
VERBOSE=false
DEBUG=false
QUIET=false
OUTPUT_FORMAT="$DEFAULT_OUTPUT_FORMAT"
LOG_LEVEL="$DEFAULT_LOG_LEVEL"
INPUT_FILE=""
OUTPUT_FILE=""
OPERATION=""
FORCE=false
DRY_RUN=false

# Arrays para argumentos múltiples
INCLUDE_PATTERNS=()
EXCLUDE_PATTERNS=()
EXTRA_ARGS=()

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función de logging con niveles
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Verificar si el nivel de log debe mostrarse
    case "$LOG_LEVEL" in
        debug) allowed_levels="debug info warn error" ;;
        info)  allowed_levels="info warn error" ;;
        warn)  allowed_levels="warn error" ;;
        error) allowed_levels="error" ;;
    esac
    
    if [[ ! " $allowed_levels " =~ " $level " ]]; then
        return 0
    fi
    
    # No mostrar nada en modo quiet excepto errores
    if [[ "$QUIET" == true && "$level" != "error" ]]; then
        return 0
    fi
    
    case "$level" in
        debug)
            echo -e "${PURPLE}[DEBUG $timestamp]${NC} $message" >&2
            ;;
        info)
            echo -e "${BLUE}[INFO  $timestamp]${NC} $message"
            ;;
        warn)
            echo -e "${YELLOW}[WARN  $timestamp]${NC} $message" >&2
            ;;
        error)
            echo -e "${RED}[ERROR $timestamp]${NC} $message" >&2
            ;;
    esac
}

# Función para mostrar información de depuración
debug_info() {
    if [[ "$DEBUG" == true ]]; then
        log debug "$@"
    fi
}

# Función para validar argumentos
validate_args() {
    local errors=0
    
    # Validar que se especificó una operación
    if [[ -z "$OPERATION" ]]; then
        log error "Se requiere especificar una operación"
        errors=$((errors + 1))
    fi
    
    # Validar archivo de entrada si es requerido
    if [[ -n "$INPUT_FILE" && ! -f "$INPUT_FILE" ]]; then
        log error "El archivo de entrada '$INPUT_FILE' no existe"
        errors=$((errors + 1))
    fi
    
    # Validar formato de salida
    local valid_formats="text json xml csv"
    if [[ ! " $valid_formats " =~ " $OUTPUT_FORMAT " ]]; then
        log error "Formato de salida inválido: '$OUTPUT_FORMAT'. Válidos: $valid_formats"
        errors=$((errors + 1))
    fi
    
    # Validar nivel de log
    local valid_levels="debug info warn error"
    if [[ ! " $valid_levels " =~ " $LOG_LEVEL " ]]; then
        log error "Nivel de log inválido: '$LOG_LEVEL'. Válidos: $valid_levels"
        errors=$((errors + 1))
    fi
    
    return $errors
}

# Función para mostrar configuración actual
show_config() {
    log info "Configuración actual:"
    echo "  🔧 Operación: ${OPERATION:-'no especificada'}"
    echo "  📁 Archivo entrada: ${INPUT_FILE:-'ninguno'}"
    echo "  📄 Archivo salida: ${OUTPUT_FILE:-'stdout'}"
    echo "  📋 Formato: $OUTPUT_FORMAT"
    echo "  📊 Nivel log: $LOG_LEVEL"
    echo "  🔍 Verbose: $VERBOSE"
    echo "  🐛 Debug: $DEBUG"
    echo "  🤫 Quiet: $QUIET"
    echo "  💪 Force: $FORCE"
    echo "  🎭 Dry run: $DRY_RUN"
    
    if [[ ${#INCLUDE_PATTERNS[@]} -gt 0 ]]; then
        echo "  ✅ Incluir: ${INCLUDE_PATTERNS[*]}"
    fi
    
    if [[ ${#EXCLUDE_PATTERNS[@]} -gt 0 ]]; then
        echo "  ❌ Excluir: ${EXCLUDE_PATTERNS[*]}"
    fi
    
    if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
        echo "  ➕ Argumentos extra: ${EXTRA_ARGS[*]}"
    fi
}

# Función para ejecutar operación
execute_operation() {
    log info "Ejecutando operación: $OPERATION"
    
    if [[ "$DRY_RUN" == true ]]; then
        log warn "MODO SIMULACIÓN - No se realizarán cambios reales"
    fi
    
    case "$OPERATION" in
        process)
            log info "Procesando archivo: ${INPUT_FILE:-'stdin'}"
            # Aquí iría la lógica de procesamiento
            ;;
        convert)
            log info "Convirtiendo formato de $OUTPUT_FORMAT"
            # Aquí iría la lógica de conversión
            ;;
        analyze)
            log info "Analizando datos..."
            # Aquí iría la lógica de análisis
            ;;
        *)
            log error "Operación no implementada: $OPERATION"
            return 1
            ;;
    esac
    
    log info "Operación completada exitosamente"
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
⚙️ Sistema Avanzado de Parsing de Argumentos v$VERSION

USAGE:
    $SCRIPT_NAME [OPCIONES] OPERACIÓN [ARGUMENTOS]

OPERACIONES:
    process     Procesar archivo de entrada
    convert     Convertir formato de datos
    analyze     Analizar contenido

OPCIONES PRINCIPALES:
    -i, --input FILE        Archivo de entrada
    -o, --output FILE       Archivo de salida (default: stdout)
    -f, --format FORMAT     Formato de salida: text|json|xml|csv (default: text)
    --operation OP          Operación a realizar

OPCIONES DE CONFIGURACIÓN:
    -v, --verbose           Modo verboso
    -q, --quiet             Modo silencioso
    -d, --debug             Modo debug
    --log-level LEVEL       Nivel de log: debug|info|warn|error (default: info)

OPCIONES DE FILTRADO:
    --include PATTERN       Incluir archivos que coincidan con PATTERN
    --exclude PATTERN       Excluir archivos que coincidan con PATTERN

OPCIONES DE CONTROL:
    --force                 Forzar operación (sobrescribir archivos)
    --dry-run               Simular operación sin hacer cambios
    --config                Mostrar configuración actual

INFORMACIÓN:
    -h, --help              Mostrar esta ayuda
    -V, --version           Mostrar versión
    --examples              Mostrar ejemplos de uso

EJEMPLOS:
    $SCRIPT_NAME --operation process -i data.txt -f json
    $SCRIPT_NAME convert --input file.csv --output result.xml --verbose
    $SCRIPT_NAME analyze --include "*.log" --exclude "debug*" --dry-run

VARIABLES DE ENTORNO:
    ADVANCED_ARGS_LOG_LEVEL    Nivel de log por defecto
    ADVANCED_ARGS_FORMAT       Formato de salida por defecto
    ADVANCED_ARGS_VERBOSE      Activar modo verbose (true/false)

EXIT CODES:
    0    Éxito
    1    Error de argumentos
    2    Error de validación
    3    Error de operación
    64   Error de uso (argumentos inválidos)
EOF
}

# Función para mostrar ejemplos
show_examples() {
    cat << EOF
📚 EJEMPLOS DE USO

1. PROCESAMIENTO BÁSICO:
   $SCRIPT_NAME --operation process --input data.txt

2. CONVERSIÓN CON FORMATO:
   $SCRIPT_NAME convert -i input.csv -o output.json -f json --verbose

3. ANÁLISIS CON FILTROS:
   $SCRIPT_NAME analyze --include "*.log" --include "*.txt" --exclude "temp*"

4. MODO DEBUG CON SIMULACIÓN:
   $SCRIPT_NAME process -i large_file.dat --debug --dry-run --log-level debug

5. CONFIGURACIÓN COMPLETA:
   $SCRIPT_NAME convert \\
     --input /path/to/input.xml \\
     --output /path/to/output.json \\
     --format json \\
     --verbose \\
     --force \\
     --include "data*" \\
     --exclude "*.tmp"

6. USO CON VARIABLES DE ENTORNO:
   ADVANCED_ARGS_LOG_LEVEL=debug \\
   ADVANCED_ARGS_FORMAT=xml \\
   $SCRIPT_NAME analyze --input data/

7. MODO SILENCIOSO PARA SCRIPTS:
   $SCRIPT_NAME process -i input.txt -o output.txt --quiet

8. VER CONFIGURACIÓN ACTUAL:
   $SCRIPT_NAME --config --operation process -v --format json
EOF
}

# Función para mostrar versión
show_version() {
    echo "$SCRIPT_NAME version $VERSION"
    echo "Sistema avanzado de parsing de argumentos"
    echo "Copyright (c) 2024 - Programming Course"
}

# Función principal de parsing de argumentos
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            # Operaciones
            --operation)
                OPERATION="$2"
                shift 2
                ;;
            process|convert|analyze)
                OPERATION="$1"
                shift
                ;;
            
            # Archivos de entrada y salida
            -i|--input)
                INPUT_FILE="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            
            # Formato y configuración
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            --log-level)
                LOG_LEVEL="$2"
                shift 2
                ;;
            
            # Flags booleanos
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
            --force)
                FORCE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            
            # Patrones de filtrado
            --include)
                INCLUDE_PATTERNS+=("$2")
                shift 2
                ;;
            --exclude)
                EXCLUDE_PATTERNS+=("$2")
                shift 2
                ;;
            
            # Información y ayuda
            -h|--help)
                show_help
                exit 0
                ;;
            -V|--version)
                show_version
                exit 0
                ;;
            --examples)
                show_examples
                exit 0
                ;;
            --config)
                show_config
                exit 0
                ;;
            
            # Argumentos no reconocidos
            -*)
                log error "Opción no reconocida: $1"
                log info "Use '$SCRIPT_NAME --help' para ver opciones disponibles"
                exit 64
                ;;
            
            # Argumentos posicionales
            *)
                EXTRA_ARGS+=("$1")
                shift
                ;;
        esac
    done
}

# Función principal
main() {
    # Aplicar configuración desde variables de entorno
    [[ -n "$ADVANCED_ARGS_LOG_LEVEL" ]] && LOG_LEVEL="$ADVANCED_ARGS_LOG_LEVEL"
    [[ -n "$ADVANCED_ARGS_FORMAT" ]] && OUTPUT_FORMAT="$ADVANCED_ARGS_FORMAT"
    [[ "$ADVANCED_ARGS_VERBOSE" == "true" ]] && VERBOSE=true
    
    # Parsear argumentos
    parse_arguments "$@"
    
    # Validar argumentos
    if ! validate_args; then
        log error "Errores de validación encontrados"
        exit 2
    fi
    
    # Mostrar configuración en modo debug
    debug_info "Iniciando con configuración:"
    if [[ "$DEBUG" == true ]]; then
        show_config
    fi
    
    # Ejecutar operación
    if ! execute_operation; then
        log error "Error durante la ejecución de la operación"
        exit 3
    fi
    
    log info "Script completado exitosamente"
}

# Ejecutar función principal solo si el script es ejecutado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

#!/bin/bash

# =============================================================================
# WEB MONITOR - Solución Completa
# =============================================================================
# Monitorea URLs configuradas y guarda resultados organizados por fecha
# 
# Uso:
#   ./web_monitor.sh                    # Una ejecución
#   ./web_monitor.sh --loop 30          # Ejecutar cada 30 segundos
#   ./web_monitor.sh --config custom/   # Usar directorio custom en lugar de config/
# =============================================================================

# Configuración por defecto
CONFIG_DIR="config"
RESULTS_DIR="results"
LOOP_INTERVAL=0
VERBOSE=false
LOG_FILE=""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Función de logging
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        SUCCESS) echo -e "${GREEN}[✅ SUCCESS]${NC} $message" ;;
        INFO)    echo -e "${CYAN}[ℹ️  INFO]${NC} $message" ;;
        WARNING) echo -e "${YELLOW}[⚠️  WARNING]${NC} $message" ;;
        ERROR)   echo -e "${RED}[❌ ERROR]${NC} $message" ;;
        HEADER)  echo -e "\n${CYAN}=== $message ===${NC}" ;;
    esac
    
    # Log a archivo si está configurado
    if [ -n "$LOG_FILE" ]; then
        echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    fi
}

# Función para mostrar ayuda
show_help() {
    cat << 'EOF'
WEB MONITOR - Solución Completa

DESCRIPCIÓN:
    Monitorea URLs desde archivos de configuración y guarda resultados
    organizados por sitio y fecha.

USO:
    ./web_monitor.sh [OPCIONES]

OPCIONES:
    --config DIR        Directorio de configuración (default: config/)
    --results DIR       Directorio de resultados (default: results/)
    --loop SECONDS      Ejecutar en bucle cada N segundos
    --log FILE          Archivo de log
    --verbose           Salida detallada
    --help              Mostrar esta ayuda

ESTRUCTURA DE CONFIG:
    config/
    ├── sitio1/
    │   └── url.txt     # Una URL por archivo
    ├── sitio2/
    │   └── url.txt
    └── ...

ESTRUCTURA DE RESULTADOS:
    results/
    ├── sitio1/
    │   └── 2025-08-25/
    │       ├── 2025-08-25-0930.txt
    │       └── 2025-08-25-1015.txt
    └── sitio2/
        └── 2025-08-25/
            └── 2025-08-25-0930.txt

EJEMPLOS:
    ./web_monitor.sh                    # Una ejecución
    ./web_monitor.sh --loop 60          # Cada minuto
    ./web_monitor.sh --verbose --log monitor.log
EOF
}

# Función para parsear argumentos
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --config)
                CONFIG_DIR="$2"
                shift 2
                ;;
            --results)
                RESULTS_DIR="$2"
                shift 2
                ;;
            --loop)
                LOOP_INTERVAL="$2"
                shift 2
                ;;
            --log)
                LOG_FILE="$2"
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log ERROR "Opción desconocida: $1"
                echo "Usa --help para ver opciones disponibles"
                exit 1
                ;;
        esac
    done
}

# Función para validar configuración
validate_config() {
    if [ ! -d "$CONFIG_DIR" ]; then
        log ERROR "Directorio de configuración no existe: $CONFIG_DIR"
        exit 1
    fi
    
    local site_count=0
    for site_dir in "$CONFIG_DIR"/*; do
        [ -d "$site_dir" ] && site_count=$((site_count + 1))
    done
    
    if [ $site_count -eq 0 ]; then
        log ERROR "No hay sitios configurados en $CONFIG_DIR"
        exit 1
    fi
    
    log INFO "Encontrados $site_count sitios para monitorear"
    
    # Crear directorio de resultados si no existe
    mkdir -p "$RESULTS_DIR"
}

# Función para monitorear un sitio
monitor_site() {
    local site_dir="$1"
    local site_name=$(basename "$site_dir")
    local url_file="$site_dir/url.txt"
    
    # Validar archivo de URL
    if [ ! -f "$url_file" ]; then
        log WARNING "$site_name: archivo url.txt no encontrado"
        return 1
    fi
    
    # Leer y limpiar URL
    local url=$(cat "$url_file" | tr -d '\r\n' | xargs)
    
    if [ -z "$url" ]; then
        log WARNING "$site_name: URL vacía"
        return 1
    fi
    
    # Preparar directorios de resultado
    local date_today=$(date '+%Y-%m-%d')
    local time_now=$(date '+%Y-%m-%d-%H%M')
    local result_dir="$RESULTS_DIR/$site_name/$date_today"
    local result_file="$result_dir/${time_now}.txt"
    
    mkdir -p "$result_dir"
    
    # Hacer request DIRECTO - sin parsing complejo
    if [ "$VERBOSE" = true ]; then
        log INFO "$site_name: Monitoreando $url"
    fi
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Crear header del archivo
    cat > "$result_file" << EOF
=== WEB MONITORING RESULT ===
SITIO: $site_name
URL: $url
TIMESTAMP: $timestamp

=== CURL OUTPUT ===
EOF
    
    # Hacer curl y guardar DIRECTO en archivo
    if curl -s \
           --max-time 10 \
           --connect-timeout 5 \
           --user-agent "WebMonitor/1.0" \
           --write-out "\n--- CURL INFO ---\nHTTP Code: %{http_code}\nTime Total: %{time_total}s\nSize: %{size_download} bytes\n" \
           "$url" >> "$result_file" 2>/dev/null; then
        
        # CURL exitoso
        log SUCCESS "$site_name: ✅ Respuesta recibida"
        return 0
        
    else
        # CURL falló
        echo "ERROR: CURL failed (code: $?)" >> "$result_file"
        log ERROR "$site_name: ❌ CURL falló"
        return 1
    fi
}

# Función principal de monitoreo
run_monitoring() {
    log HEADER "Iniciando Monitoreo Web - $(date)"
    
    local total_sites=0
    local success_count=0
    local error_count=0
    
    # Monitorear cada sitio
    for site_dir in "$CONFIG_DIR"/*; do
        if [ -d "$site_dir" ]; then
            total_sites=$((total_sites + 1))
            
            if monitor_site "$site_dir"; then
                success_count=$((success_count + 1))
            else
                error_count=$((error_count + 1))
            fi
        fi
    done
    
    # Reporte final
    log INFO "Monitoreo completado: $total_sites sitios ($success_count exitosos, $error_count errores)"
    
    if [ "$VERBOSE" = true ]; then
        log INFO "Resultados guardados en: $RESULTS_DIR"
    fi
}

# Función principal
main() {
    parse_args "$@"
    validate_config
    
    if [ "$LOOP_INTERVAL" -gt 0 ]; then
        log INFO "Iniciando monitoreo en bucle cada ${LOOP_INTERVAL}s (Ctrl+C para detener)"
        while true; do
            run_monitoring
            log INFO "Esperando ${LOOP_INTERVAL}s hasta el próximo monitoreo..."
            sleep "$LOOP_INTERVAL"
        done
    else
        run_monitoring
    fi
}

# Ejecutar si se llama directamente
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

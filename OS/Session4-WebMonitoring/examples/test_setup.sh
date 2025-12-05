#!/bin/bash

# Script de Prueba y Verificacion del Setup
# Descripcion: Verifica que todo este configurado correctamente para el monitoreo web
# Uso: ./test_setup.sh

SCRIPT_NAME=$(basename "$0")

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Contadores
TESTS_TOTAL=0
TESTS_PASSED=0

# Funcion de logging
log() {
    local level="$1"
    shift
    local message="$*"
    
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
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        HEADER)
            echo -e "\n${CYAN}=== $message ===${NC}"
            ;;
    esac
}

# Funcion para ejecutar test
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "\n${YELLOW}Test $TESTS_TOTAL: $test_name${NC}"
    
    if $test_function; then
        log SUCCESS "✅ $test_name - PASO"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log ERROR "❌ $test_name - FALLO"
        return 1
    fi
}

# Test 1: Verificar estructura de directorios
test_directory_structure() {
    local required_dirs=("config" "examples")
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            log ERROR "Directorio faltante: $dir"
            return 1
        fi
    done
    
    log INFO "Estructura de directorios correcta"
    return 0
}

# Test 2: Verificar archivos de configuracion
test_config_files() {
    local config_sites=("ecommerce-main" "api-backend" "cdn-static" "news-portal")
    local missing_configs=0
    
    for site in "${config_sites[@]}"; do
        local url_file="config/$site/url.txt"
        if [ ! -f "$url_file" ]; then
            log ERROR "Archivo de configuracion faltante: $url_file"
            missing_configs=$((missing_configs + 1))
        else
            local url=$(cat "$url_file")
            if [ -z "$url" ]; then
                log ERROR "URL vacia en: $url_file"
                missing_configs=$((missing_configs + 1))
            else
                log INFO "Configurado: $site -> $url"
            fi
        fi
    done
    
    if [ $missing_configs -eq 0 ]; then
        log INFO "Todos los archivos de configuracion estan presentes"
        return 0
    else
        log ERROR "$missing_configs archivos de configuracion con problemas"
        return 1
    fi
}

# Test 3: Verificar herramientas necesarias
test_dependencies() {
    local required_tools=("curl" "date" "mkdir" "cat")
    local missing_tools=0
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            log ERROR "Herramienta faltante: $tool"
            missing_tools=$((missing_tools + 1))
        else
            log INFO "Herramienta disponible: $tool"
        fi
    done
    
    if [ $missing_tools -eq 0 ]; then
        log INFO "Todas las herramientas necesarias estan disponibles"
        return 0
    else
        log ERROR "$missing_tools herramientas faltantes"
        return 1
    fi
}

# Test 4: Probar conectividad basica
test_connectivity() {
    local test_url="https://httpbin.org/get"
    
    log INFO "Probando conectividad con: $test_url"
    
    if curl -s --head --max-time 10 "$test_url" >/dev/null 2>&1; then
        log INFO "Conectividad a internet: OK"
        return 0
    else
        log ERROR "No hay conectividad a internet o httpbin.org no accesible"
        return 1
    fi
}

# Test 5: Verificar URLs de configuracion
test_configured_urls() {
    local failed_urls=0
    
    for site_dir in config/*/; do
        local site_name=$(basename "$site_dir")
        local url_file="$site_dir/url.txt"
        
        if [ -f "$url_file" ]; then
            local url=$(cat "$url_file")
            log INFO "Probando $site_name: $url"
            
            if curl -s --head --max-time 10 "$url" >/dev/null 2>&1; then
                log SUCCESS "$site_name: Accesible"
            else
                log WARNING "$site_name: No accesible (podria ser temporal)"
                failed_urls=$((failed_urls + 1))
            fi
        fi
    done
    
    if [ $failed_urls -eq 0 ]; then
        log INFO "Todas las URLs configuradas son accesibles"
        return 0
    else
        log WARNING "$failed_urls URLs no accesibles (esto podria ser normal)"
        return 0  # No fallar el test por URLs temporalmente inaccesibles
    fi
}

# Test 6: Verificar permisos de escritura
test_write_permissions() {
    local test_dirs=("." "config" "examples")
    
    for dir in "${test_dirs[@]}"; do
        if [ ! -w "$dir" ]; then
            log ERROR "Sin permisos de escritura en: $dir"
            return 1
        fi
    done
    
    # Probar crear archivo temporal
    local test_file="test_write_$$"
    if echo "test" > "$test_file" 2>/dev/null; then
        rm -f "$test_file"
        log INFO "Permisos de escritura: OK"
        return 0
    else
        log ERROR "No se puede crear archivos en el directorio actual"
        return 1
    fi
}

# Test 7: Simular creacion de resultado
test_result_creation() {
    local test_results_dir="test_results"
    local site_name="test-site"
    local date_dir=$(date '+%Y-%m-%d')
    local timestamp=$(date '+%Y-%m-%d-%H%M')
    
    # Crear estructura de prueba
    mkdir -p "$test_results_dir/$site_name/$date_dir"
    
    # Crear archivo de resultado de prueba
    local result_file="$test_results_dir/$site_name/$date_dir/$timestamp.txt"
    
    cat > "$result_file" << EOF
=== WEB MONITORING RESULT ===
URL: https://httpbin.org/get
Timestamp: $(date)
Status Code: 200
Response Time: 1.234s

=== TEST DATA ===
This is a test result file
EOF
    
    if [ -f "$result_file" ]; then
        log INFO "Archivo de resultado de prueba creado: $result_file"
        
        # Limpiar
        rm -rf "$test_results_dir"
        
        log INFO "Simulacion de creacion de resultados: OK"
        return 0
    else
        log ERROR "No se pudo crear archivo de resultado de prueba"
        return 1
    fi
}

# Mostrar informacion del sistema
show_system_info() {
    log HEADER "Informacion del Sistema"
    
    echo -e "${BLUE}Sistema:${NC} $(uname -s)"
    echo -e "${BLUE}Hostname:${NC} $(hostname)"
    echo -e "${BLUE}Usuario:${NC} $(whoami)"
    echo -e "${BLUE}Directorio:${NC} $(pwd)"
    echo -e "${BLUE}Fecha:${NC} $(date)"
    
    if command -v curl >/dev/null 2>&1; then
        echo -e "${BLUE}Curl version:${NC} $(curl --version | head -1)"
    fi
}

# Mostrar resumen final
show_summary() {
    log HEADER "Resumen de Pruebas"
    
    echo -e "${BLUE}Tests ejecutados:${NC} $TESTS_TOTAL"
    echo -e "${BLUE}Tests exitosos:${NC} $TESTS_PASSED"
    echo -e "${BLUE}Tests fallidos:${NC} $((TESTS_TOTAL - TESTS_PASSED))"
    
    local success_rate=$((TESTS_PASSED * 100 / TESTS_TOTAL))
    echo -e "${BLUE}Tasa de exito:${NC} ${success_rate}%"
    
    if [ $TESTS_PASSED -eq $TESTS_TOTAL ]; then
        log SUCCESS "🎉 Todos los tests pasaron - Sistema listo para monitoreo web"
        echo ""
        echo -e "${GREEN}Proximos pasos:${NC}"
        echo "1. Implementar el script principal de monitoreo"
        echo "2. Configurar sitios reales en config/"
        echo "3. Programar ejecucion automatica con cron"
        return 0
    else
        log WARNING "⚠️  Algunos tests fallaron - Revisar problemas antes de continuar"
        echo ""
        echo -e "${YELLOW}Acciones recomendadas:${NC}"
        echo "1. Revisar errores mostrados arriba"
        echo "2. Instalar herramientas faltantes si es necesario"
        echo "3. Verificar permisos y conectividad"
        echo "4. Re-ejecutar este script hasta que todos los tests pasen"
        return 1
    fi
}

# Funcion principal
main() {
    log HEADER "Verificacion del Setup de Monitoreo Web"
    
    show_system_info
    
    # Ejecutar todos los tests
    run_test "Estructura de Directorios" test_directory_structure
    run_test "Archivos de Configuracion" test_config_files  
    run_test "Dependencias del Sistema" test_dependencies
    run_test "Conectividad Basica" test_connectivity
    run_test "URLs Configuradas" test_configured_urls
    run_test "Permisos de Escritura" test_write_permissions
    run_test "Creacion de Resultados" test_result_creation
    
    show_summary
}

# Ejecutar funcion principal
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

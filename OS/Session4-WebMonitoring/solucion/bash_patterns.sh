#!/bin/bash

# Patrones de Lectura de Archivos y Directorios en Bash
# Descripcion: Ejemplos practicos para leer configuraciones de monitoreo web
# Uso: ./bash_reading_patterns.sh [ejemplo]

SCRIPT_NAME=$(basename "$0")

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funcion de logging
log() {
    local level="$1"
    shift
    local message="$*"
    
    case "$level" in
        INFO) echo -e "${BLUE}[INFO]${NC} $message" ;;
        SUCCESS) echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
        WARNING) echo -e "${YELLOW}[WARNING]${NC} $message" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} $message" ;;
        HEADER) echo -e "\n${CYAN}=== $message ===${NC}" ;;
    esac
}

# =============================================================================
# EJEMPLO 1: FOR con GLOB - Leer Directorios (BASICO)
# =============================================================================
ejemplo_for_directorios_basico() {
    log HEADER "Ejemplo 1: FOR con Directorios - Básico"
    
    # ✅ CORRECTO - Expandir glob de directorios
    for site_dir in config/*/; do
        # Verificar si el directorio realmente existe
        if [ -d "$site_dir" ]; then
            echo "  📁 Directorio encontrado: $site_dir"
        else
            echo "  ❌ No hay directorios con patrón config/*/"
            break
        fi
    done
}

# =============================================================================
# EJEMPLO 2: FOR con GLOB - Lectura Robusta
# =============================================================================
ejemplo_for_directorios_robusto() {
    log HEADER "Ejemplo 2: FOR con Directorios - Robusto"
    
    # ✅ ROBUSTO - Con validación y nombre limpio
    for site_dir in config/*/; do
        # Saltar si no hay coincidencias (glob no expandido)
        [ ! -d "$site_dir" ] && continue
        
        # Obtener nombre del sitio (quitar config/ y /)
        site_name=$(basename "$site_dir")
        
        echo "  🌐 Sitio: $site_name"
        echo "     📍 Ruta: $site_dir"
    done
}

# =============================================================================
# EJEMPLO 3: Leer Contenido de Archivos
# =============================================================================
ejemplo_leer_archivos() {
    log HEADER "Ejemplo 3: Leer Contenido de Archivos"
    
    # ✅ LEER archivo url.txt de cada sitio
    for site_dir in config/*/; do
        [ ! -d "$site_dir" ] && continue
        
        site_name=$(basename "$site_dir")
        url_file="$site_dir/url.txt"
        
        # Verificar que el archivo existe
        if [ -f "$url_file" ]; then
            # Leer URL del archivo y limpiar espacios/saltos de línea
            url=$(cat "$url_file" | tr -d '\r\n' | xargs)
            echo "  🌐 $site_name → 🔗 $url"
        else
            echo "  ❌ $site_name → ERROR: $url_file no existe"
        fi
    done
}

# =============================================================================
# EJEMPLO 4: Validación Completa
# =============================================================================
ejemplo_validacion_completa() {
    log HEADER "Ejemplo 4: Validación Completa"
    
    # ✅ VALIDACIÓN COMPLETA - Producción ready
    for site_dir in config/*/; do
        # 1. Verificar directorio existe
        [ ! -d "$site_dir" ] && continue
        
        site_name=$(basename "$site_dir")
        url_file="$site_dir/url.txt"
        
        # 2. Verificar archivo existe
        if [ ! -f "$url_file" ]; then
            echo "  ❌ $site_name: sin archivo url.txt"
            continue
        fi
        
        # 3. Leer y validar URL no está vacía
        url=$(cat "$url_file" | tr -d '\r\n' | xargs)
        
        if [ -z "$url" ]; then
            echo "  ❌ $site_name: URL vacía"
            continue
        fi
        
        # 4. Validar formato básico de URL
        if [[ ! "$url" =~ ^https?:// ]]; then
            echo "  ⚠️  $site_name: URL sin protocolo → $url"
        else
            echo "  ✅ $site_name → $url"
        fi
    done
}

# =============================================================================
# EJEMPLO 5: Contadores y Estadísticas
# =============================================================================
ejemplo_contadores() {
    log HEADER "Ejemplo 5: Contadores y Estadísticas"
    
    # ✅ CONTADORES - Para reportes y logs
    local total_sites=0
    local valid_sites=0
    local invalid_sites=0
    
    for site_dir in config/*/; do
        [ ! -d "$site_dir" ] && continue
        
        total_sites=$((total_sites + 1))
        site_name=$(basename "$site_dir")
        url_file="$site_dir/url.txt"
        
        if [ -f "$url_file" ]; then
            url=$(cat "$url_file" | tr -d '\r\n' | xargs)
            if [ -n "$url" ]; then
                valid_sites=$((valid_sites + 1))
                echo "  ✅ $site_name"
            else
                invalid_sites=$((invalid_sites + 1))
                echo "  ❌ $site_name (URL vacía)"
            fi
        else
            invalid_sites=$((invalid_sites + 1))
            echo "  ❌ $site_name (sin url.txt)"
        fi
    done
    
    echo ""
    echo "  📊 Total: $total_sites | Válidos: $valid_sites | Inválidos: $invalid_sites"
}

# =============================================================================
# EJEMPLO 6: Manejo de Espacios y Caracteres Especiales
# =============================================================================
ejemplo_caracteres_especiales() {
    log HEADER "Ejemplo 6: Manejo de Espacios y Caracteres Especiales"
    
    log INFO "Creando directorio temporal con espacios para demostrar..."
    
    # Crear un directorio temporal con espacios para demostrar
    mkdir -p "config/sitio con espacios" 2>/dev/null
    echo "https://example.com" > "config/sitio con espacios/url.txt" 2>/dev/null
    
    # ✅ MANEJO SEGURO - Con comillas y validación
    for site_dir in config/*/; do
        # SIEMPRE usar comillas dobles para variables
        [ ! -d "$site_dir" ] && continue
        
        site_name=$(basename "$site_dir")
        url_file="$site_dir/url.txt"
        
        # Usar comillas en todos los tests
        if [ -f "$url_file" ]; then
            # Múltiples métodos de lectura segura
            url=$(head -1 "$url_file" | tr -d '\r\n' | xargs)
            
            # Validar que no esté vacío DESPUÉS de limpiar
            if [ -n "$url" ]; then
                echo "  🌐 Sitio: '$site_name' → URL: '$url'"
            fi
        fi
    done
    
    # Limpiar directorio temporal
    rm -rf "config/sitio con espacios" 2>/dev/null
    log INFO "Directorio temporal eliminado"
}

# =============================================================================
# EJEMPLO 7: CURL con Status Code y Timing
# =============================================================================
ejemplo_curl_monitoring() {
    log HEADER "Ejemplo 7: CURL para Web Monitoring"
    
    # ✅ CURL COMPLETO - Con status, timing y manejo de errores
    for site_dir in config/*/; do
        [ ! -d "$site_dir" ] && continue
        
        site_name=$(basename "$site_dir")
        url_file="$site_dir/url.txt"
        
        # Verificar archivo y leer URL
        if [ ! -f "$url_file" ]; then
            echo "  ❌ $site_name: sin url.txt"
            continue
        fi
        
        url=$(cat "$url_file" | tr -d '\r\n' | xargs)
        [ -z "$url" ] && continue
        
        echo "  🌐 Probando $site_name ($url)..."
        
        # CURL con información completa
        response=$(curl -s -w "STATUS:%{http_code}|TIME:%{time_total}s|SIZE:%{size_download}bytes" \
                       --max-time 10 \
                       --connect-timeout 5 \
                       "$url" 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            # Extraer métricas de la respuesta
            metrics=$(echo "$response" | tail -1)
            status_code=$(echo "$metrics" | cut -d'|' -f1 | cut -d':' -f2)
            time_total=$(echo "$metrics" | cut -d'|' -f2 | cut -d':' -f2)
            size_bytes=$(echo "$metrics" | cut -d'|' -f3 | cut -d':' -f2)
            
            # Determinar estado basado en código HTTP
            if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
                echo "     ✅ HTTP $status_code | ⏱️  $time_total | 📦 $size_bytes"
            elif [ "$status_code" -ge 300 ] && [ "$status_code" -lt 400 ]; then
                echo "     🔄 HTTP $status_code (Redirect) | ⏱️  $time_total"
            elif [ "$status_code" -ge 400 ] && [ "$status_code" -lt 500 ]; then
                echo "     ⚠️  HTTP $status_code (Client Error) | ⏱️  $time_total"
            elif [ "$status_code" -ge 500 ]; then
                echo "     💥 HTTP $status_code (Server Error) | ⏱️  $time_total"
            else
                echo "     ❓ HTTP $status_code (Unknown) | ⏱️  $time_total"
            fi
        else
            echo "     💀 CURL FAILED - Timeout o conexión fallida"
        fi
        
        # Pequeña pausa entre requests
        sleep 0.5
    done
}

# =============================================================================
# EJEMPLO 8: CURL Avanzado con Headers y Logs
# =============================================================================
ejemplo_curl_avanzado() {
    log HEADER "Ejemplo 8: CURL Avanzado - Headers y Logging"
    
    # Crear directorio temporal para logs
    mkdir -p "/tmp/curl_logs"
    timestamp=$(date '+%Y%m%d_%H%M%S')
    
    # ✅ CURL PROFESIONAL - Con logs detallados
    for site_dir in config/*/; do
        [ ! -d "$site_dir" ] && continue
        
        site_name=$(basename "$site_dir")
        url_file="$site_dir/url.txt"
        
        [ ! -f "$url_file" ] && continue
        url=$(cat "$url_file" | tr -d '\r\n' | xargs)
        [ -z "$url" ] && continue
        
        echo "  🔍 Análisis completo: $site_name"
        
        # Log file para este sitio
        log_file="/tmp/curl_logs/${site_name}_${timestamp}.log"
        
        # CURL con logging completo
        curl -s -I \
             -w "⏱️  Total: %{time_total}s | DNS: %{time_namelookup}s | Connect: %{time_connect}s | Transfer: %{time_starttransfer}s\n📏 Size: %{size_download} bytes | Speed: %{speed_download} bytes/s\n🔗 Status: %{http_code} | Redirects: %{num_redirects}\n" \
             --max-time 10 \
             --user-agent "WebMonitor/1.0 (Learning Project)" \
             "$url" > "$log_file" 2>&1
        
        if [ $? -eq 0 ]; then
            # Mostrar solo métricas clave
            tail -3 "$log_file" | while read line; do
                echo "     $line"
            done
        else
            echo "     💀 Request failed - Ver $log_file"
        fi
    done
    
    echo ""
    log INFO "Logs guardados en: /tmp/curl_logs/"
    ls -la /tmp/curl_logs/ 2>/dev/null | grep "_${timestamp}.log" | head -3
}

# =============================================================================
# ERRORES COMUNES
# =============================================================================
mostrar_errores_comunes() {
    log HEADER "❌ ERRORES COMUNES A EVITAR"
    
    echo ""
    log ERROR "1. FOR SIN VALIDACIÓN:"
    echo "   for dir in config/*/; do"
    echo "       echo \$dir  # ← Puede imprimir 'config/*' si no hay directorios"
    echo "   done"
    echo ""
    
    log ERROR "2. VARIABLES SIN COMILLAS:"
    echo "   if [ -f \$url_file ]; then  # ← Falla si hay espacios"
    echo ""
    
    log ERROR "3. NO LIMPIAR ENTRADA:"
    echo "   url=\$(cat file.txt)  # ← Puede incluir \\r\\n"
    echo ""
    
    log ERROR "4. NO VALIDAR CONTENIDO:"
    echo "   cat \"\$file\" | some_command  # ← Falla si file está vacío"
    echo ""
    
    log SUCCESS "✅ PATRONES CORRECTOS:"
    echo ""
    echo "1. ✅ FOR CON VALIDACIÓN:"
    echo "   for dir in config/*/; do"
    echo "       [ ! -d \"\$dir\" ] && continue"
    echo "       echo \"\$dir\""
    echo "   done"
    echo ""
    
    echo "2. ✅ VARIABLES CON COMILLAS:"
    echo "   if [ -f \"\$url_file\" ]; then"
    echo ""
    
    echo "3. ✅ LIMPIAR ENTRADA:"
    echo "   url=\$(cat \"\$file\" | tr -d '\\r\\n' | xargs)"
    echo ""
    
    echo "4. ✅ VALIDAR ANTES DE USAR:"
    echo "   [ -n \"\$url\" ] && process_url \"\$url\""
    echo ""
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
main() {
    local ejemplo="${1:-all}"
    
    case "$ejemplo" in
        1|basico)
            ejemplo_for_directorios_basico
            ;;
        2|robusto)
            ejemplo_for_directorios_robusto
            ;;
        3|archivos)
            ejemplo_leer_archivos
            ;;
        4|validacion)
            ejemplo_validacion_completa
            ;;
        5|contadores)
            ejemplo_contadores
            ;;
        6|espacios)
            ejemplo_caracteres_especiales
            ;;
        7|curl)
            ejemplo_curl_monitoring
            ;;
        8|curl-avanzado)
            ejemplo_curl_avanzado
            ;;
        errores)
            mostrar_errores_comunes
            ;;
        all)
            ejemplo_for_directorios_basico
            ejemplo_for_directorios_robusto
            ejemplo_leer_archivos
            ejemplo_validacion_completa
            ejemplo_contadores
            ejemplo_caracteres_especiales
            ejemplo_curl_monitoring
            ejemplo_curl_avanzado
            ejemplo_redireccion
            mostrar_errores_comunes
            ;;
        9|redireccion)
            ejemplo_redireccion
            ;;
        help|-h|--help)
            echo "Uso: $SCRIPT_NAME [ejemplo]"
            echo ""
            echo "Ejemplos disponibles:"
            echo "  1, basico       - FOR básico con directorios"
            echo "  2, robusto      - FOR robusto con validación"
            echo "  3, archivos     - Leer contenido de archivos"
            echo "  4, validacion   - Validación completa"
            echo "  5, contadores   - Contadores y estadísticas"
            echo "  6, espacios     - Manejo de caracteres especiales"
            echo "  7, curl         - CURL con status y timing"
            echo "  8, curl-avanzado - CURL con headers y logs"
            echo "  9, redireccion  - Redirección > >> < | &"
            echo "  errores         - Errores comunes"
            echo "  all             - Todos los ejemplos"
            ;;
        *)
            log ERROR "Ejemplo no reconocido: $ejemplo"
            echo "Usa '$SCRIPT_NAME help' para ver opciones disponibles"
            exit 1
            ;;
    esac
}

# Ejecutar función principal
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

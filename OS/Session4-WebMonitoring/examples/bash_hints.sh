#!/bin/bash

# =============================================================================
# PISTAS Y ESQUELETOS PARA LECTURA DE ARCHIVOS EN BASH
# =============================================================================
# 🎯 OBJETIVO: Practicar patrones bash comunes
# 📚 SOLUCIONES COMPLETAS en: bash_reading_patterns.sh
# =============================================================================

SCRIPT_NAME=$(basename "$0")

# =============================================================================
# PISTA 1: FOR básico con directorios
# =============================================================================
pista_for_basico() {
    echo "=== PISTA 1: FOR básico con directorios ==="
    
    # TODO: Completa los espacios en blanco
    for site_dir in _____; do          # ← ¿Qué patrón usar para config/?
        # TODO: ¿Cómo verificar que el directorio existe?
        [ ! -d "____" ] && continue
        
        # TODO: ¿Cómo extraer solo el nombre del directorio?
        site_name=$(basename "____")
        
        echo "Directorio encontrado: $site_name"
    done
}

# =============================================================================
# PISTA 2: Leer contenido de archivos
# =============================================================================
pista_leer_archivos() {
    echo "=== PISTA 2: Leer contenido de archivos ==="
    
    for site_dir in config/*/; do
        [ ! -d "$site_dir" ] && continue
        
        site_name=$(basename "$site_dir")
        url_file="____/url.txt"              # TODO: ¿Cómo construir la ruta completa?
        
        # TODO: ¿Cómo verificar que el archivo existe?
        if [ -f "____" ]; then
            # TODO: ¿Cómo leer y limpiar el contenido?
            url=$(cat "____" | tr -d '____' | ____)
            echo "$site_name → $url"
        else
            echo "ERROR: $site_name sin url.txt"
        fi
    done
}

# =============================================================================
# PISTA 3: Validación robusta
# =============================================================================
pista_validacion() {
    echo "=== PISTA 3: Validación robusta ==="
    
    for site_dir in config/*/; do
        # TODO: ¿Cómo verificar que el directorio existe?
        [ ! -d "____" ] && continue
        
        site_name=$(basename "$site_dir")
        url_file="$site_dir/url.txt"
        
        # TODO: ¿Cómo verificar que el archivo existe?
        if [ ! -f "____" ]; then
            echo "ERROR: $site_name sin archivo url.txt"
            continue
        fi
        
        url=$(cat "$url_file" | tr -d '\r\n' | xargs)
        
        # TODO: ¿Cómo verificar que la URL no está vacía?
        if [ -z "____" ]; then
            echo "ERROR: $site_name tiene URL vacía"
            continue
        fi
        
        # TODO: ¿Cómo verificar formato http/https?
        if [[ ! "$url" =~ ^____:// ]]; then
            echo "WARNING: $site_name URL sin protocolo: $url"
        else
            echo "✅ $site_name → $url"
        fi
    done
}

# =============================================================================
# PISTA 4: CURL básico
# =============================================================================
pista_curl_basico() {
    echo "=== PISTA 4: CURL simple - guardar todo ==="
    
    # Para cada URL válida
    url="https://httpbin.org/get"
    
    # TODO: ¿Cómo hacer curl simple con información básica?
    response=$(curl -s \
                   --max-time ____ \
                   --write-out "\n--- INFO ---\nHTTP: %{http_code}\nTime: %{time_total}s\n" \
                   "____" 2>/dev/null)
    
    # TODO: ¿Cómo verificar si curl tuvo éxito?
    if [ $? -eq 0 ]; then
        echo "✅ CURL exitoso"
        # TODO: ¿Cómo guardar TODA la respuesta en archivo?
        echo "$response" > "resultado_$(date +%H%M).txt"
    else
        echo "❌ CURL falló"
    fi
}

# =============================================================================
# PISTA 5: Manejo de errores
# =============================================================================
pista_manejo_errores() {
    echo "=== PISTA 5: Manejo de errores ==="
    
    # Ejemplo: diferentes tipos de errores que pueden ocurrir
    urls=("https://httpbin.org/get" "https://sitio-que-no-existe.fake" "https://httpbin.org/status/500")
    
    for url in "${urls[@]}"; do
        echo "Probando: $url"
        
        # TODO: ¿Cómo capturar tanto la respuesta como el código de salida?
        response=$(curl -s --max-time 5 "$url" 2>/dev/null)
        exit_code=$?
        
        # TODO: ¿Cómo evaluar diferentes tipos de errores?
        case $exit_code in
            0)
                echo "✅ Conexión exitosa"
                ;;
            6)
                echo "❌ No se pudo resolver el host (DNS)"
                ;;
            7)
                echo "❌ No se pudo conectar al servidor"
                ;;
            28)
                echo "⏰ Timeout - servidor no responde"
                ;;
            *)
                echo "❓ Error desconocido: código $exit_code"
                ;;
        esac
    done
}

# =============================================================================
# PISTA 6: Organización de resultados
# =============================================================================
pista_organizacion_resultados() {
    echo "=== PISTA 6: Organización de resultados por fecha ==="
    
    site_name="test-site"
    url="https://httpbin.org/get"
    
    # TODO: ¿Cómo obtener la fecha actual en formato YYYY-MM-DD?
    date_today=$(date '+____')
    
    # TODO: ¿Cómo obtener timestamp para el archivo?
    timestamp=$(date '+____')
    
    # TODO: ¿Cómo construir la ruta completa?
    result_dir="results/$site_name/____"
    result_file="$result_dir/$timestamp.txt"
    
    # TODO: ¿Cómo crear directorios?
    mkdir ____ "$result_dir"
    
    # TODO: ¿Cómo guardar header + curl completo?
    cat > "$result_file" << EOF
=== MONITORING RESULT ===
SITE: $site_name
URL: $url
TIMESTAMP: $(date)

=== CURL OUTPUT ===
EOF
    
    # TODO: ¿Cómo agregar el resultado de curl al archivo?
    curl -s --write-out "\nHTTP: %{http_code}" "$url" >> "$result_file"
}

# =============================================================================
# PISTA 7: Redirección de entrada y salida
# =============================================================================
pista_redireccion() {
    echo "=== PISTA 7: Redirección > >> < | ==="
    echo ""
    
    echo "💡 EJEMPLOS A COMPLETAR:"
    echo ""
    echo "1. Sobrescribir archivo:"
    echo '   echo "Primera línea" ____ archivo.txt'
    echo '   echo "Segunda línea" ____ archivo.txt  # ¿Qué queda?'
    echo ""
    
    echo "2. Agregar al final de archivo:"
    echo '   echo "Línea 1" > archivo2.txt'
    echo '   echo "Línea 2" ____ archivo2.txt'
    echo '   echo "Línea 3" ____ archivo2.txt'
    echo ""
    
    echo "3. Usar archivo como entrada:"
    echo '   wc -l ____ frutas.txt  # Contar líneas'
    echo ""
    
    echo "4. Conectar comandos con pipe:"
    echo '   ls -la ____ wc -l  # Contar archivos'
    echo '   ls -la ____ grep "\.txt"  # Buscar .txt'
    echo ""
    
    echo "5. Redirigir errores:"
    echo '   cat archivo_malo.txt ____/dev/null'
    echo ""
    
    echo "6. Here document (múltiples líneas):"
    echo '   cat ____ EOF > config.txt'
    echo '   Línea 1'
    echo '   Línea 2'
    echo '   EOF'
    echo ""
    
    echo "🚀 CASOS PRÁCTICOS:"
    echo ""
    echo "• Guardar curl: curl -s \"URL\" ____ archivo.json"
    echo "• Agregar log: echo \"LOG\" ____ monitor.log"
    echo "• Contar líneas: wc -l ____ archivo.txt"
    echo "• Buscar en logs: cat log ____ grep \"ERROR\""
    echo ""
    echo "❓ PREGUNTA: ¿Cuál es la diferencia entre > y >> ?"
}

# =============================================================================
# ERRORES COMUNES Y SOLUCIONES
# =============================================================================
mostrar_errores_comunes() {
    echo "=== ❌ ERRORES COMUNES Y SOLUCIONES ==="
    echo ""
    
    # ❌ ERROR 1: FOR sin validación
    echo "1. FOR sin validación:"
    echo "   ❌ for dir in config/*/; do echo \$dir; done  # ← Imprime 'config/*' si no hay dirs"
    echo "   ✅ [ ! -d \"\$dir\" ] && continue"
    echo ""
    
    # ❌ ERROR 2: Variables sin comillas  
    echo "2. Variables sin comillas:"
    echo "   ❌ if [ -f \$file ]; then  # ← Falla con espacios"
    echo "   ✅ if [ -f \"\$file\" ]; then"
    echo ""
    
    # ❌ ERROR 3: No limpiar entrada
    echo "3. No limpiar entrada:"
    echo "   ❌ url=\$(cat file.txt)  # ← Incluye \\r\\n"
    echo "   ✅ url=\$(cat file.txt | tr -d '\\r\\n' | xargs)"
    echo ""
    
    # ❌ ERROR 4: No validar antes de usar
    echo "4. No validar antes de usar:"
    echo "   ❌ curl \"\$url\"  # ← \$url puede estar vacía"
    echo "   ✅ [ -n \"\$url\" ] && curl \"\$url\""
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
main() {
    local ejemplo="${1:-help}"
    
    case $ejemplo in
        1|basico)
            pista_for_basico
            ;;
        2|archivos)
            pista_leer_archivos
            ;;
        3|validacion)
            pista_validacion
            ;;
        4|curl)
            pista_curl_basico
            ;;
        5|manejo)
            pista_manejo_errores
            ;;
        6|resultados)
            pista_organizacion_resultados
            ;;
        7|redireccion)
            pista_redireccion
            ;;
        errores)
            mostrar_errores_comunes
            ;;
        all)
            pista_for_basico
            pista_leer_archivos
            pista_validacion
            pista_curl_basico
            pista_manejo_errores
            pista_organizacion_resultados
            pista_redireccion
            mostrar_errores_comunes
            ;;
        help|-h|--help)
            echo "Uso: $SCRIPT_NAME [pista]"
            echo ""
            echo "🎯 PISTAS DISPONIBLES:"
            echo "  1, basico      - FOR básico con directorios"
            echo "  2, archivos    - Leer contenido de archivos"
            echo "  3, validacion  - Validación robusta"
            echo "  4, curl        - CURL simple - guardar todo"
            echo "  5, manejo      - Manejo de errores"
            echo "  6, resultados  - Organización por fecha"
            echo "  7, redireccion - Redirección > >> < |"
            echo "  errores        - Errores comunes"
            echo "  all            - Todas las pistas"
            echo ""
            echo "💡 Para ver SOLUCIONES COMPLETAS:"
            echo "     ../solucion/bash_patterns.sh [ejemplo]"
            echo "     ../solucion/web_monitor.sh --help"
            ;;
        *)
            log ERROR "Pista no reconocida: $ejemplo"
            echo "Usa '$SCRIPT_NAME help' para ver opciones disponibles"
            exit 1
            ;;
    esac
}

# Ejecutar función principal
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

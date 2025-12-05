#!/bin/bash

# Script para limpiar terminaciones de línea CRLF
# Uso: ./fix_scripts.sh [archivo] o ./fix_scripts.sh (para todos los .sh)

fix_single_file() {
    local file="$1"
    echo "Limpiando $file..."
    tr -d '\r' < "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
    chmod +x "$file"
    echo "✅ $file arreglado"
}

if [ "$1" ]; then
    # Arreglar archivo específico
    fix_single_file "$1"
else
    # Arreglar todos los archivos .sh
    echo "🔧 Limpiando todos los archivos .sh..."
    for file in *.sh; do
        if [ -f "$file" ]; then
            fix_single_file "$file"
        fi
    done
    echo "🎉 Todos los archivos arreglados!"
fi

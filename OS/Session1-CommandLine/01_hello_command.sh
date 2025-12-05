#!/bin/sh

USERNAME=`whoami`
CURRENT_TIME=`date '+%Y-%m-%d %H:%M:%S'`

show_greeting() {
    echo "============================================"
    echo "Hola, $USERNAME!"
    echo "Fecha y hora: $CURRENT_TIME"
    echo "Sistema: `uname -s`"
    echo "Directorio actual: `pwd`"
    echo "============================================"
}

show_help() {
    echo "Uso: sh $0 [OPCION]"
    echo "Opciones:"
    echo "  -h, --help     Mostrar esta ayuda"
    echo "  -s, --simple   Saludo simple"
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
elif [ "$1" = "-s" ] || [ "$1" = "--simple" ]; then
    echo "Hola, $USERNAME!"
else
    show_greeting
fi
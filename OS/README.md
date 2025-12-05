# 🖥️ Chapter-OS: Sistemas Operativos y Línea de Comandos

Este capítulo cubre conceptos fundamentales de sistemas operativos, enfocándose en la creación y manejo de herramientas de línea de comandos.

## 📚 Contenido del Capítulo

### Session1-CommandLine: Creación de Línea de Comandos
- Fundamentos de la línea de comandos
- Creación de scripts bash básicos
- Automatización de tareas del sistema
- Navegación y manipulación de archivos

### Session2-ArgumentsConfig: Manejo de Argumentos y Configuración
- Procesamiento de argumentos de línea de comandos
- Archivos de configuración
- Variables de entorno
- Validación y manejo de errores

### Session3-ScheduledTasks: Tareas Programadas y Automatización
- Fundamentos de cron y crontab
- Systemd timers como alternativa moderna
- Scripts de mantenimiento automático
- Monitoreo y notificaciones

### Session4-WebMonitoring: Monitoreo Web Automatizado
- Sistema de monitoreo de múltiples sitios web
- Consultas HTTP automatizadas con curl
- Organización de resultados por fecha y sitio
- Integración con cron para ejecución periódica

## 🎯 Objetivos de Aprendizaje

Al finalizar este capítulo, serás capaz de:
- ✅ Crear scripts de línea de comandos eficientes
- ✅ Manejar argumentos y opciones de manera profesional
- ✅ Implementar sistemas de configuración flexibles
- ✅ Automatizar tareas repetitivas del sistema

## 📖 Referencia Rápida de Comandos

### 🔍 Flags de Verificación de Archivos

| Flag | Descripción | Ejemplo | Uso Común |
|------|-------------|---------|-----------|
| `-e` | **Existe** (archivo o directorio) | `[ -e archivo ]` | Verificar existencia |
| `-f` | Es un **archivo** regular | `[ -f archivo.txt ]` | Verificar archivos |
| `-d` | Es un **directorio** | `[ -d carpeta ]` | Verificar directorios |
| `-r` | Tiene permisos de **lectura** | `[ -r archivo ]` | Verificar acceso |
| `-w` | Tiene permisos de **escritura** | `[ -w archivo ]` | Verificar modificación |
| `-x` | Tiene permisos de **ejecución** | `[ -x script.sh ]` | Verificar ejecutables |

### 💡 Reglas de Sintaxis Importantes

#### Espacios Obligatorios en `[ ]`
```bash
# ✅ CORRECTO - Espacios obligatorios alrededor de [ ]
[ -d directorio ]
[ -f archivo ]
[ "$var" = "valor" ]

# ❌ INCORRECTO - Sin espacios
[-d directorio]
[ -f archivo]
["$var"="valor"]
```

#### ¿Cuándo Usar `[ ]` y Cuándo NO?

**REGLA PRINCIPAL**: `[ ]` solo para TESTS/PRUEBAS, NO para comandos normales

##### ✅ **Comandos que VAN DENTRO de `[ ]` (Tests/Pruebas):**

```bash
# Tests de archivos/directorios
[ -e archivo ]       # ¿Existe?
[ -f archivo ]       # ¿Es archivo?
[ -d directorio ]    # ¿Es directorio?
[ -r archivo ]       # ¿Se puede leer?
[ -w archivo ]       # ¿Se puede escribir?
[ -x archivo ]       # ¿Se puede ejecutar?

# Comparaciones de strings
[ "$var" = "valor" ]     # ¿Son iguales?
[ "$var" != "valor" ]    # ¿Son diferentes?
[ -z "$var" ]            # ¿Está vacía?
[ -n "$var" ]            # ¿No está vacía?

# Comparaciones numéricas
[ "$num" -eq 5 ]     # ¿Es igual a 5?
[ "$num" -gt 10 ]    # ¿Es mayor que 10?
[ "$num" -lt 20 ]    # ¿Es menor que 20?
```

##### ❌ **Comandos que NO usan `[ ]` (Operaciones normales):**

```bash
# Comandos del sistema
echo "texto"              # NO: [ echo "texto" ]
ls -la                    # NO: [ ls -la ]
mkdir carpeta             # NO: [ mkdir carpeta ]
cp origen destino         # NO: [ cp origen destino ]
chmod +x archivo          # NO: [ chmod +x archivo ]
date                      # NO: [ date ]

# Operaciones de archivos
cat archivo.txt           # NO: [ cat archivo.txt ]
grep "patrón" archivo     # NO: [ grep "patrón" archivo ]
find . -name "*.sh"       # NO: [ find . -name "*.sh" ]
```

##### 🧠 **Truco para Recordar: "¿Es una pregunta?"**

```bash
# ¿Existe el archivo? → SÍ, es pregunta → Usar [ ]
if [ -f archivo ]; then
    cat archivo           # Mostrar archivo → NO es pregunta → Sin [ ]
fi

# ¿Es el usuario root? → SÍ, es pregunta → Usar [ ]
if [ "$USER" = "root" ]; then
    echo "Eres admin"     # Mostrar mensaje → NO es pregunta → Sin [ ]
fi
```

### 🛠️ Comandos y Opciones Esenciales

#### `echo` - Mostrar texto
```bash
echo "Texto simple"              # Texto básico
echo -e "\033[31mRojo\033[0m"    # Con colores (-e habilita escapes)
echo -n "Sin salto de línea"     # Sin \n al final
```

#### `read` - Leer entrada
```bash
read variable                    # Leer entrada básica
read -r line                     # Sin interpretar backslashes
read -p "Prompt: " variable      # Con mensaje
```

#### Substitución de Comandos
```bash
# Moderna (recomendada)
resultado=$(comando)
fecha=$(date '+%Y-%m-%d')

# Tradicional (compatible con sh)
resultado=`comando`
fecha=`date '+%Y-%m-%d'`
```

### 🐛 Solución de Problemas Comunes

#### Error: `: not found` o `$'\r': command not found`
```bash
# Problema: Terminaciones de línea Windows (CRLF)
# Solución:
tr -d '\r' < archivo.sh > archivo_limpio.sh
# o
sed 's/\r$//' archivo.sh > archivo_limpio.sh
```

#### Error: `missing ]`
```bash
# Problema: Falta espacio antes del ]
[ -d home]     # ❌ Incorrecto

# Solución: Agregar espacio
[ -d home ]    # ✅ Correcto
```

#### Error: `bash: not found`
```bash
# Usar sh en lugar de bash en sistemas mínimos
sh script.sh           # En lugar de bash script.sh
./script.sh            # Si tiene permisos de ejecución
```

### 📋 Comandos Universales (Disponibles en cualquier Unix)

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `echo` | Mostrar texto | `echo "Hola"` |
| `cat` | Mostrar contenido | `cat archivo.txt` |
| `ls` | Listar archivos | `ls -la` |
| `cd` | Cambiar directorio | `cd /home` |
| `pwd` | Directorio actual | `pwd` |
| `whoami` | Usuario actual | `whoami` |
| `date` | Fecha y hora | `date '+%Y-%m-%d'` |
| `uname` | Info del sistema | `uname -s` |
| `chmod` | Cambiar permisos | `chmod +x script.sh` |
| `mkdir` | Crear directorio | `mkdir carpeta` |
| `cp` | Copiar | `cp origen destino` |
| `mv` | Mover/renombrar | `mv viejo nuevo` |
| `rm` | Eliminar | `rm archivo` |
| `find` | Buscar archivos | `find . -name "*.sh"` |
| `grep` | Buscar texto | `grep "patrón" archivo` |

### 🔧 Herramientas de Limpieza

```bash
# Script automático para limpiar terminaciones CRLF
../fix_scripts.sh                    # Limpiar todos los .sh
../fix_scripts.sh archivo.sh         # Limpiar archivo específico

# Comando manual rápido
tr -d '\r' < archivo.sh > temp && mv temp archivo.sh && chmod +x archivo.sh
```

## 🚀 Requisitos Previos

- Conocimientos básicos de programación
- Familiaridad con sistemas Unix/Linux
- Terminal y editor de texto

## 📝 Estructura del Proyecto

```
Chapter-OS/
├── README.md
├── setup_alpine.sh              # 🏔️ Configuración automática para Alpine Linux
├── ALPINE_SETUP.md              # 📖 Guía completa para Alpine Linux
├── fix_scripts.sh               # 🔧 Herramienta para limpiar scripts
├── Session1-CommandLine/
│   ├── README.md
│   └── [4 scripts bash]
├── Session2-ArgumentsConfig/
│   ├── README.md  
│   └── [4 scripts bash]
├── Session3-ScheduledTasks/
│   ├── README.md
│   └── [4 scripts bash]
└── Session4-WebMonitoring/
    ├── README.md
    ├── [4 scripts bash]
    ├── config/                   # 📁 Ejemplos de configuración
    └── examples/                 # 🧪 Casos de prueba
```

## 🏔️ Configuración Especial para Alpine Linux

Si estás usando **Alpine Linux** (común en contenedores Docker), necesitas configuración adicional:

### ⚡ Configuración Rápida (Una Línea)
```bash
# Ejecutar script de configuración automática
./setup_alpine.sh
```

### 🔧 Configuración Manual
```bash
# 1. Instalar herramientas esenciales
apk update
apk add bash coreutils findutils grep sed gawk curl git nano dcron

# 2. Habilitar cron
rc-update add dcron default
rc-service dcron start

# 3. Limpiar scripts
./fix_scripts.sh

# 4. Cambiar a bash
bash
```

### 📖 Documentación Completa
Ver `ALPINE_SETUP.md` para guía detallada y solución de problemas específicos de Alpine.

---
💡 **Tip**: Cada sesión incluye ejemplos prácticos y ejercicios para reforzar el aprendizaje.

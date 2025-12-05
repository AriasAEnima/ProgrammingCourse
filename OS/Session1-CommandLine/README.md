# 🖥️ Session1: Creación de Línea de Comandos

## 📖 Descripción

Esta sesión cubre los fundamentos para crear herramientas de línea de comandos efectivas utilizando bash scripting.

## 🎯 Objetivos

- Entender la estructura básica de scripts bash
- Crear comandos personalizados
- Manejar entrada y salida de datos
- Implementar validaciones básicas
- Automatizar tareas del sistema operativo

## Install bash
```
apk add bash
```

## Fix jumplines

```
tr -d '\r' < 01_hello_command.sh > temp_file && mv temp_file 01_hello_command.sh 
```

## 📋 Contenido

### 1. Fundamentos de Bash Scripting
- Estructura básica de un script
- Shebang y permisos de ejecución
- Variables y tipos de datos
- Comentarios y documentación

### 2. Creación de Comandos
- Scripts ejecutables
- PATH y ubicación de comandos
- Convenciones de nomenclatura
- Manejo de errores básico

### 3. Entrada y Salida
- Lectura de input del usuario
- Redirección de output
- Códigos de salida
- Logging básico

## 🛠️ Archivos de Práctica

- `01_hello_command.sh` - Script básico de saludo
- `02_file_operations.sh` - Operaciones con archivos
- `03_system_info.sh` - Información del sistema
- `04_backup_tool.sh` - Herramienta de respaldo simple

## 🚀 Ejercicios

1. **Comando de Saludo**: Crear un script que salude al usuario actual
2. **Listador de Archivos**: Script para listar archivos con filtros
3. **Monitor del Sistema**: Mostrar información básica del sistema
4. **Automatizador**: Script para automatizar una tarea repetitiva

## 💡 Recursos

- [Bash Guide](https://www.gnu.org/software/bash/manual/)
- [Advanced Bash Scripting](https://tldp.org/LDP/abs/html/)
- [ShellCheck](https://www.shellcheck.net/) - Validador de scripts

---

**Siguiente**: Session2-ArgumentsConfig - Manejo avanzado de argumentos y configuración

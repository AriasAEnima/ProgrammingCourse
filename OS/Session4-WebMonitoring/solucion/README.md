# 🎯 Solución Completa - Web Monitoring

## 📋 Descripción

Esta carpeta contiene la **implementación completa** del proyecto de monitoreo web descrito en el README principal de `Session4-WebMonitoring`.

## 📁 Archivos

- **`web_monitor.sh`** - Script principal de monitoreo web
- **`bash_patterns.sh`** - Ejemplos de patrones bash utilizados en la solución  
- **`README.md`** - Esta documentación

## 🚀 Uso Rápido

```bash
# Ejecución simple (una vez)
./solucion/web_monitor.sh

# Monitoreo continuo cada 60 segundos
./solucion/web_monitor.sh --loop 60

# Con logging detallado
./solucion/web_monitor.sh --verbose --log monitor.log
```

## ⚙️ Opciones Completas

```bash
./web_monitor.sh [OPCIONES]

OPCIONES:
--config DIR        Directorio de configuración (default: config/)
--results DIR       Directorio de resultados (default: results/)  
--loop SECONDS      Ejecutar en bucle cada N segundos
--log FILE          Archivo de log
--verbose           Salida detallada
--help              Mostrar ayuda completa
```

## 📊 Ejemplo de Resultado

El script genera archivos organizados por sitio y fecha:

```
results/
├── ecommerce-main/
│   └── 2025-08-25/
│       ├── 2025-08-25-0930.txt
│       └── 2025-08-25-1015.txt
└── api-backend/
    └── 2025-08-25/
        └── 2025-08-25-0930.txt
```

### Contenido de archivo de resultado:

```
=== WEB MONITORING RESULT ===
SITIO: ecommerce-main
URL: https://httpbin.org/delay/1
TIMESTAMP: 2025-08-25 09:30:15

=== CURL OUTPUT ===
{
  "args": {},
  "headers": {
    "User-Agent": "WebMonitor/1.0"
  }
}

--- CURL INFO ---
HTTP Code: 200
Time Total: 1.234s
Size: 302 bytes
```

## 🔧 Características

### ✅ Funcionalidades Implementadas

- **Lectura automática** de configuraciones desde `config/*/url.txt`
- **Requests HTTP** con curl - guarda **todo el output** sin parsing complejo
- **Métricas básicas** incluidas (HTTP code, tiempo total, tamaño)
- **Manejo de errores** robusto (timeouts, DNS, SSL, etc.)
- **Organización por fecha** automática
- **Logging** configurable con niveles (INFO, WARNING, ERROR, SUCCESS)
- **Modo bucle** para monitoreo continuo
- **Argumentos flexibles** para personalización
- **Salida colorizada** para mejor legibilidad

### 📊 Métricas Capturadas

- **HTTP Status Code** (200, 404, 500, etc.)
- **Tiempo total** de la request  
- **Tamaño** de la respuesta en bytes
- **Body completo** de la respuesta (JSON, HTML, etc.)
- **Todo el output de curl** sin modificaciones

### 🛡️ Manejo de Errores

- **DNS failures** (dominio no existe)
- **Connection failures** (servidor no disponible)
- **Timeouts** (servidor lento)
- **SSL errors** (certificados inválidos)
- **URLs vacías** o archivos faltantes

## 🧪 Pruebas

```bash
# Verificar que todo funciona
./examples/test_setup.sh

# Probar una ejecución
./solucion/web_monitor.sh --verbose

# Verificar resultados
ls -la results/
```

## 🎓 Propósito Educativo

Este script demuestra:

- **Lectura de archivos** y directorios en bash
- **Validación robusta** de datos de entrada  
- **Requests HTTP** con `curl` y captura de métricas
- **Manejo de errores** profesional
- **Organización de archivos** por fecha
- **Logging estructurado** con niveles
- **Parseo de argumentos** de línea de comandos
- **Uso de funciones** para código modular

## 🔗 Referencias

- Pistas de implementación: `../examples/bash_hints.sh`
- Verificación del setup: `../examples/test_setup.sh`
- Configuración de ejemplo: `../config/`

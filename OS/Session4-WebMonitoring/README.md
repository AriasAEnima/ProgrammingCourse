# 🌐 Session4: Monitoreo Web Automatizado

## 📖 Descripción del Proyecto

Sistema automatizado para **monitorear múltiples sitios web** de forma periódica, consultando URLs configuradas y almacenando los resultados organizados por fecha y sitio.

## 🎯 Objetivo Principal

Crear un sistema que:
1. **Revise periódicamente** una carpeta de configuración
2. **Consulte URLs** definidas en archivos de texto
3. **Almacene resultados** organizados por fecha y sitio
4. **Genere logs** detallados de todas las operaciones

## 📋 Especificación de la Tarea

### 🗂️ Estructura de Entrada (Configuración)
```
config/
├── web-site-1/
│   └── url.txt          # Contiene: https://example1.com
├── web-site-2/
│   └── url.txt          # Contiene: https://example2.com
└── web-site-3/
    └── url.txt          # Contiene: https://api.example3.com/health
```

### 📁 Estructura de Salida (Resultados)
```
results/
├── web-site-1/
│   ├── 2025-08-25/
│   │   ├── 2025-08-25-0930.txt    # Consulta 09:30
│   │   ├── 2025-08-25-1030.txt    # Consulta 10:30
│   │   └── 2025-08-25-1130.txt    # Consulta 11:30
│   └── 2025-08-26/
│       └── 2025-08-26-0930.txt
├── web-site-2/
│   └── 2025-08-25/
│       ├── 2025-08-25-0930.txt
│       └── 2025-08-25-1030.txt
└── logs/
    ├── monitoring.log              # Log principal
    └── errors.log                  # Solo errores
```

### 📝 Contenido de Archivos de Resultado
```
=== WEB MONITORING RESULT ===
URL: https://example1.com
Timestamp: 2025-08-25 09:30:15
Status Code: 200
Response Time: 1.234s
Content Length: 15420 bytes

=== HEADERS ===
Content-Type: text/html; charset=UTF-8
Server: nginx/1.18.0
Last-Modified: Mon, 25 Aug 2025 08:30:00 GMT

=== RESPONSE BODY ===
<!DOCTYPE html>
<html>...
```

## 🔧 Componentes del Sistema

### 1. **Monitor Principal** (`01_web_monitor.sh`)
- Función principal de monitoreo
- Lectura de configuración
- Coordinación de consultas
- Generación de reportes

### 2. **Consultor de URLs** (`02_url_checker.sh`) 
- Realizar peticiones HTTP/HTTPS
- Medir tiempos de respuesta
- Capturar headers y contenido
- Manejar errores y timeouts

### 3. **Organizador de Resultados** (`03_result_organizer.sh`)
- Crear estructura de directorios por fecha
- Generar nombres de archivo con timestamp
- Rotar resultados antiguos
- Comprimir archivos históricos

### 4. **Configurador Automático** (`04_monitor_setup.sh`)
- Inicializar estructura de proyecto
- Configurar tareas programadas (cron)
- Crear archivos de configuración
- Validar dependencias

## 📊 Flujo de Trabajo

### 🔄 Proceso Principal
1. **Escanear** directorio de configuración
2. **Leer** archivos `url.txt` de cada sitio
3. **Consultar** cada URL configurada
4. **Guardar** resultado en estructura organizada
5. **Registrar** operación en logs
6. **Generar** reporte de estado

### ⏰ Programación Temporal
- **Frecuencia**: Configurable (cada 30min, 1h, 2h, etc.)
- **Cron**: Integración automática
- **Recuperación**: Reintentos en caso de fallo
- **Persistencia**: Mantener histórico configurable

## 🛠️ Casos de Uso y Ejemplos

### Caso 1: **Monitoreo de Disponibilidad**
```bash
# URLs a monitorear
config/ecommerce-site/url.txt     → https://shop.example.com
config/api-backend/url.txt        → https://api.example.com/health
config/cdn-assets/url.txt         → https://cdn.example.com/status

# Verificar que respondan HTTP 200
# Medir tiempo de respuesta
# Alertar si > 5 segundos o error
```

### Caso 2: **Monitoreo de Contenido**
```bash
# Verificar cambios en páginas específicas
config/news-site/url.txt          → https://news.site.com/latest
config/price-monitor/url.txt      → https://store.com/product/123

# Detectar cambios en contenido
# Guardar snapshots diarios
# Comparar con versión anterior
```

### Caso 3: **APIs y Servicios**
```bash
# Monitorear endpoints de API
config/auth-service/url.txt       → https://auth.api.com/ping
config/payment-gateway/url.txt    → https://payments.api.com/status

# Verificar respuestas JSON válidas
# Medir latencia de APIs
# Validar estructura de respuesta
```

## 🎯 Funcionalidades Avanzadas

### 📈 **Métricas y Análisis**
- Tiempo de respuesta promedio
- Porcentaje de disponibilidad
- Detección de tendencias
- Alertas inteligentes

### 🔔 **Notificaciones**
- Email para errores críticos
- Webhooks para integraciones
- Reportes diarios automáticos
- Dashboard simple en HTML

### 🔧 **Configuración Flexible**
- Headers HTTP personalizados
- Timeouts configurables
- User-agents específicos
- Autenticación básica/Bearer tokens

### 🗃️ **Gestión de Datos**
- Rotación automática de logs
- Compresión de resultados antiguos
- Exportación a CSV/JSON
- Limpieza de archivos temporales

## 📚 Conocimientos Aplicados

### De Sesiones Anteriores
- **Session1**: Scripts bash, manejo de archivos
- **Session2**: Argumentos, configuración
- **Session3**: Cron, automatización

### Nuevos Conceptos
- **curl**: Peticiones HTTP avanzadas
- **jq**: Procesamiento de JSON (opcional)
- **date**: Manipulación de fechas y timestamps
- **find**: Búsqueda y organización de archivos

## 🧪 Casos de Prueba

### Pruebas Básicas
1. ✅ Leer URLs de configuración
2. ✅ Realizar petición HTTP simple
3. ✅ Crear estructura de directorios
4. ✅ Generar archivo con timestamp

### Pruebas de Errores
1. ❌ URL inválida o no alcanzable
2. ❌ Timeout de conexión
3. ❌ Directorio sin permisos
4. ❌ Disco lleno

### Pruebas de Integración
1. 🔄 Ejecutar ciclo completo de monitoreo
2. 🔄 Verificar programación con cron
3. 🔄 Validar rotación de archivos
4. 🔄 Comprobar alertas y notificaciones

## 🏗️ Plan de Implementación

### Fase 1: **Core Básico**
- Lector de configuración
- Consultor HTTP simple
- Organizador de archivos
- Logging básico

### Fase 2: **Automatización**
- Integración con cron
- Manejo de errores robusto
- Configuración avanzada
- Validaciones

### Fase 3: **Características Avanzadas**
- Métricas y análisis
- Notificaciones
- Dashboard
- Optimizaciones

## 💡 Decisiones de Diseño

### ¿Por qué esta estructura?
- **Separación por sitio**: Facilita análisis individual
- **Organización por fecha**: Permite análisis temporal
- **Timestamp en archivo**: Identificación única
- **Logs centralizados**: Debugging y auditoría

### ¿Qué herramientas usar?
- **curl**: Universalmente disponible, potente
- **bash**: Scripting nativo, sin dependencias
- **cron**: Programación estándar
- **jq**: Para APIs JSON (opcional)

---

## 🚀 Próximos Pasos

1. **Implementar** el monitor básico
2. **Crear** ejemplos de configuración
3. **Desarrollar** organizador de resultados  
4. **Integrar** con sistema de cron
5. **Probar** con sitios reales
6. **Optimizar** y agregar características

## 📁 Archivos del Proyecto

### 🎯 Para Practicar
- **`examples/bash_hints.sh`** - Pistas y esqueletos para completar  
- **`examples/test_setup.sh`** - Verificación del entorno

### ✅ Solución Completa
- **`solucion/web_monitor.sh`** - Implementación completa del proyecto
- **`solucion/bash_patterns.sh`** - Patrones bash utilizados
- **`solucion/README.md`** - Documentación detallada de la solución

### ⚙️ Configuración
- **`config/*/url.txt`** - URLs de sitios a monitorear

**¿Listo para comenzar la implementación?** 🌐

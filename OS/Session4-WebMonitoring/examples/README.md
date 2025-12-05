# 🧪 Ejemplos y Casos de Prueba

Esta carpeta contiene ejemplos prácticos y casos de prueba para el sistema de monitoreo web.

## 📁 Archivos en esta Carpeta

- **`bash_hints.sh`** - 🎯 Pistas y esqueletos para practicar patrones bash
- **`test_setup.sh`** - 🧪 Verificación automática del entorno y configuración  
- **`README.md`** - 📖 Esta documentación

### 🔗 Ver Soluciones Completas

Para la **implementación completa** del proyecto:
```bash
# Script principal del proyecto
../solucion/web_monitor.sh --help

# Patrones bash utilizados  
../solucion/bash_patterns.sh help
```

## 📋 Tipos de Ejemplos

### 🎯 **Casos de Uso Comunes**

#### 1. **Monitoreo de E-commerce**
```bash
# Configuración típica para tienda online
config/
├── homepage/url.txt          → https://tienda.com
├── product-page/url.txt      → https://tienda.com/producto/123
├── checkout/url.txt          → https://tienda.com/checkout
├── api-inventory/url.txt     → https://api.tienda.com/inventory
└── payment-gateway/url.txt   → https://payments.tienda.com/status
```

#### 2. **Monitoreo de Aplicación Web**
```bash
# Configuración para app completa
config/
├── frontend/url.txt          → https://app.company.com
├── api-auth/url.txt          → https://api.company.com/auth/health
├── api-users/url.txt         → https://api.company.com/users/ping
├── database-health/url.txt   → https://api.company.com/db/status
└── cdn-assets/url.txt        → https://cdn.company.com/health
```

#### 3. **Monitoreo de Microservicios**
```bash
# Configuración para arquitectura distribuida
config/
├── gateway/url.txt           → https://gateway.service.com/health
├── user-service/url.txt      → https://users.service.com/ping
├── order-service/url.txt     → https://orders.service.com/ping
├── inventory-service/url.txt → https://inventory.service.com/ping
└── notification-service/url.txt → https://notify.service.com/ping
```

## 📊 Ejemplos de Resultados Esperados

### ✅ **Resultado Exitoso**
```
results/ecommerce-main/2025-08-25/2025-08-25-1430.txt
=== WEB MONITORING RESULT ===
URL: https://httpbin.org/delay/1
Timestamp: 2025-08-25 14:30:15
Status Code: 200
Response Time: 1.234s
Content Length: 342 bytes

=== HEADERS ===
Content-Type: application/json
Server: nginx/1.18.0
Access-Control-Allow-Origin: *

=== RESPONSE BODY ===
{
  "args": {},
  "headers": {
    "Host": "httpbin.org",
    "User-Agent": "curl/7.68.0"
  },
  "origin": "192.168.1.100",
  "url": "https://httpbin.org/delay/1"
}
```

### ❌ **Resultado con Error**
```
results/api-backend/2025-08-25/2025-08-25-1430.txt
=== WEB MONITORING RESULT ===
URL: https://unreachable-site.com/api
Timestamp: 2025-08-25 14:30:45
Status Code: CONNECTION_FAILED
Response Time: 30.000s (timeout)
Error: Could not resolve host: unreachable-site.com

=== CURL INFO ===
Exit Code: 6
Error Message: Couldn't resolve host name
```

## 🧪 Scripts de Prueba

### **test_basic_monitoring.sh**
```bash
#!/bin/bash
# Prueba básica del sistema de monitoreo

echo "🧪 Ejecutando pruebas básicas..."

# 1. Verificar estructura de configuración
test_config_structure() {
    echo "📁 Verificando estructura de config..."
    for site in ecommerce-main api-backend cdn-static news-portal; do
        if [ -f "config/$site/url.txt" ]; then
            echo "✅ $site configurado"
        else
            echo "❌ $site falta configuración"
        fi
    done
}

# 2. Probar conectividad
test_connectivity() {
    echo "🌐 Probando conectividad..."
    for site in config/*/; do
        site_name=$(basename "$site")
        url=$(cat "$site/url.txt")
        echo "Testing $site_name: $url"
        
        if curl -s --head "$url" >/dev/null; then
            echo "✅ $site_name: Conectividad OK"
        else
            echo "❌ $site_name: Error de conectividad"
        fi
    done
}

# 3. Verificar herramientas necesarias
test_dependencies() {
    echo "🔧 Verificando dependencias..."
    for tool in curl date mkdir; do
        if command -v "$tool" >/dev/null; then
            echo "✅ $tool disponible"
        else
            echo "❌ $tool no encontrado"
        fi
    done
}

# Ejecutar todas las pruebas
test_config_structure
test_connectivity  
test_dependencies

echo "🎉 Pruebas completadas"
```

### **test_error_scenarios.sh**
```bash
#!/bin/bash
# Prueba escenarios de error

echo "🚨 Probando manejo de errores..."

# Crear configuración temporal con URLs problemáticas
mkdir -p config/test-errors

# URL que devuelve 404
echo "https://httpbin.org/status/404" > config/test-errors/url.txt

# URL que devuelve 500
echo "https://httpbin.org/status/500" > config/test-timeout/url.txt

# URL inexistente
echo "https://sitio-que-no-existe-12345.com" > config/test-unreachable/url.txt

echo "Configuración de prueba creada en config/test-*"
echo "Ejecuta el monitor para ver cómo maneja estos errores"
```

## 📈 Casos de Análisis

### **Análisis de Rendimiento**
```bash
# Monitorear sitios con diferentes tiempos de respuesta
config/fast-site/url.txt      → https://httpbin.org/delay/0.1
config/medium-site/url.txt    → https://httpbin.org/delay/1
config/slow-site/url.txt      → https://httpbin.org/delay/3
```

### **Análisis de Disponibilidad**  
```bash
# Monitorear diferentes códigos de estado
config/site-ok/url.txt        → https://httpbin.org/status/200
config/site-redirect/url.txt  → https://httpbin.org/status/301
config/site-notfound/url.txt  → https://httpbin.org/status/404
config/site-error/url.txt     → https://httpbin.org/status/500
```

### **Análisis de Contenido**
```bash
# Monitorear diferentes tipos de respuesta
config/json-api/url.txt       → https://httpbin.org/json
config/html-page/url.txt      → https://httpbin.org/html
config/xml-feed/url.txt       → https://httpbin.org/xml
```

## 🎯 Objetivos de Aprendizaje

Al trabajar con estos ejemplos aprenderás:

1. **📊 Análisis de Métricas**
   - Tiempo de respuesta promedio
   - Porcentaje de disponibilidad  
   - Detección de patrones y tendencias

2. **🔍 Debugging**
   - Identificar problemas de conectividad
   - Analizar códigos de error HTTP
   - Troubleshooting de timeouts

3. **📈 Optimización**
   - Configurar timeouts apropiados
   - Ajustar frecuencia de monitoreo
   - Balancear entre precisión y recursos

4. **🚨 Alertas**
   - Definir umbrales críticos
   - Configurar notificaciones
   - Crear respuestas automáticas

## 🚀 Ejercicios Prácticos

### Ejercicio 1: **Setup Básico**
1. Configura 3 sitios diferentes
2. Ejecuta una ronda de monitoreo
3. Analiza los resultados generados

### Ejercicio 2: **Manejo de Errores**
1. Configura URLs que fallan intencionalmente
2. Observa cómo el sistema maneja errores
3. Verifica que los logs capturen información útil

### Ejercicio 3: **Automatización**
1. Configura cron para ejecutar cada 15 minutos
2. Deja corriendo por algunas horas
3. Analiza los patrones en los datos generados

### Ejercicio 4: **Análisis de Tendencias**
1. Monitorea el mismo sitio por varios días
2. Identifica patrones de rendimiento
3. Crea un reporte de disponibilidad

---

## 📚 Recursos Útiles

- **httpbin.org**: Servicio de pruebas HTTP
- **curl manual**: `man curl` para opciones avanzadas  
- **cron timing**: https://crontab.guru para expresiones cron
- **HTTP status codes**: https://httpstatuses.com para referencia

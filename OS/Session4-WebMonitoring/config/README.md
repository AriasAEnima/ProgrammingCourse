# 📁 Configuración de Sitios Web

Esta carpeta contiene la configuración de sitios web a monitorear. Cada subdirectorio representa un sitio diferente.

## 🗂️ Estructura

```
config/
├── ecommerce-main/
│   └── url.txt              # URL del sitio e-commerce principal
├── api-backend/
│   └── url.txt              # URL de la API backend
├── cdn-static/
│   └── url.txt              # URL del CDN de archivos estáticos
└── news-portal/
    └── url.txt              # URL del portal de noticias
```

## 📋 Sitios de Ejemplo Incluidos

### 🛒 **ecommerce-main**
- **URL**: `https://httpbin.org/delay/1`
- **Propósito**: Simula un sitio e-commerce con latencia
- **Qué prueba**: Tiempo de respuesta y tolerancia a delays

### 🔌 **api-backend** 
- **URL**: `https://httpbin.org/json`
- **Propósito**: Simula una API que devuelve JSON
- **Qué prueba**: Respuestas JSON válidas y estructura de APIs

### 📦 **cdn-static**
- **URL**: `https://httpbin.org/headers`
- **Propósito**: Simula un CDN que devuelve headers
- **Qué prueba**: Headers HTTP y información de servidor

### 📰 **news-portal**
- **URL**: `https://httpbin.org/user-agent`
- **Propósito**: Simula un portal que detecta user-agent
- **Qué prueba**: Configuración de headers personalizados

## 🧪 ¿Por qué httpbin.org?

[httpbin.org](https://httpbin.org) es un servicio de pruebas HTTP que:

- ✅ **Siempre disponible**: Servicio estable para pruebas
- ✅ **Diferentes respuestas**: JSON, HTML, headers, delays
- ✅ **Sin limitaciones**: No requiere autenticación
- ✅ **Predecible**: Respuestas consistentes para testing

## 🔧 Cómo Agregar Sitios

### 1. Crear nuevo directorio
```bash
mkdir config/mi-nuevo-sitio
```

### 2. Crear archivo de URL
```bash
echo "https://mi-sitio.com" > config/mi-nuevo-sitio/url.txt
```

### 3. (Opcional) Configuración avanzada
```bash
# Para configuración futura (headers, timeouts, etc.)
echo "timeout=30" > config/mi-nuevo-sitio/config.txt
echo "user-agent=MonitorBot/1.0" >> config/mi-nuevo-sitio/config.txt
```

## 🎯 URLs Recomendadas para Pruebas

### Testing Básico
- `https://httpbin.org/get` - GET request simple
- `https://httpbin.org/status/200` - Respuesta HTTP 200
- `https://httpbin.org/delay/2` - Delay de 2 segundos

### Testing de Errores
- `https://httpbin.org/status/404` - Error 404
- `https://httpbin.org/status/500` - Error 500
- `https://httpbin.org/status/503` - Servicio no disponible

### Testing Avanzado
- `https://httpbin.org/json` - Respuesta JSON
- `https://httpbin.org/html` - Respuesta HTML
- `https://httpbin.org/xml` - Respuesta XML
- `https://httpbin.org/gzip` - Compresión GZIP

## 🚨 Sitios Reales

Para usar sitios reales, simplemente reemplaza las URLs:

```bash
# Ejemplo con sitios reales
echo "https://google.com" > config/search-engine/url.txt
echo "https://github.com" > config/code-repo/url.txt
echo "https://stackoverflow.com" > config/dev-community/url.txt
```

⚠️ **Nota**: Ten cuidado con la frecuencia de monitoreo en sitios reales para no sobrecargar sus servidores.

## 📊 Próximos Pasos

1. **Ejecutar** el monitor: `./01_web_monitor.sh`
2. **Verificar** resultados en `results/`
3. **Configurar** cron para automatización
4. **Personalizar** sitios según tus necesidades

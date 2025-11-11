# 🔗 Ejemplos de PATH + QUERY Parameters

Este archivo muestra ejemplos prácticos de cómo usar el endpoint `/tasks/<id>/details` que combina **path parameters** y **query parameters**.

## 📍 Conceptos Clave

### PATH Parameter
```
/tasks/{task_id}/details
         ↑
    Path Parameter
```
- Se incluye directamente en la URL
- Es **requerido** para que la ruta funcione
- En nuestro caso: `task_id` identifica qué tarea queremos

### QUERY Parameters
```
/tasks/1/details?include_metadata=true&format=full&lang=en
                 ↑
            Query Parameters
```
- Van después del `?` en la URL
- Son **opcionales** en la mayoría de casos
- Se separan con `&`
- Formato: `clave=valor`

## 🧪 Ejemplos Prácticos

### 1. Sin Query Parameters (Básico)
```bash
curl http://localhost:5000/tasks/1/details
```

**Resultado:**
```json
{
  "task": {
    "id": "1",
    "title": "Aprender Flask",
    "description": "Completar el tutorial de Flask API",
    "completed": false,
    "created_at": "2024-01-15T10:00:00Z"
  },
  "request_info": {
    "path_parameter": "1",
    "query_parameters": {},
    "format": "json"
  }
}
```

### 2. Con Metadata (Un Query Parameter)
```bash
curl "http://localhost:5000/tasks/1/details?include_metadata=true"
```

**Resultado:**
```json
{
  "task": {
    "id": "1",
    "title": "Aprender Flask",
    "description": "Completar el tutorial de Flask API",
    "completed": false,
    "created_at": "2024-01-15T10:00:00Z",
    "metadata": {
      "request_timestamp": "2024-01-15T15:30:00Z",
      "task_age_days": 5,
      "path_parameter": "1",
      "query_parameters": {
        "include_metadata": "true"
      },
      "endpoint": "/tasks/1/details"
    }
  },
  "request_info": {
    "path_parameter": "1",
    "query_parameters": {
      "include_metadata": "true"
    },
    "format": "json"
  }
}
```

### 3. Formato Summary (Respuesta Simplificada)
```bash
curl "http://localhost:5000/tasks/1/details?format=summary"
```

**Resultado:**
```json
{
  "task_id": "1",
  "summary": "Tarea 'Aprender Flask' - ⏳ Pendiente",
  "details": "Creada el 2024-01-15",
  "format": "summary"
}
```

### 4. Formato Summary en Inglés
```bash
curl "http://localhost:5000/tasks/1/details?format=summary&lang=en"
```

**Resultado:**
```json
{
  "task_id": "1", 
  "summary": "Task 'Aprender Flask' - ⏳ Pending",
  "details": "Created on 2024-01-15",
  "format": "summary"
}
```

### 5. Formato Completo con Análisis
```bash
curl "http://localhost:5000/tasks/1/details?format=full"
```

**Resultado:**
```json
{
  "basic_info": {
    "id": "1",
    "title": "Aprender Flask",
    "description": "Completar el tutorial de Flask API",
    "completed": false,
    "created_at": "2024-01-15T10:00:00Z"
  },
  "analysis": {
    "word_count": 6,
    "title_length": 14,
    "age_days": 5,
    "status_emoji": "⏳",
    "priority_suggestion": "Normal"
  },
  "request_info": {
    "path_param_received": "1",
    "query_params_received": {
      "format": "full"
    },
    "total_query_params": 1
  }
}
```

### 6. Campos Específicos + Metadata
```bash
curl "http://localhost:5000/tasks/1/details?fields=title,completed&include_metadata=true"
```

**Resultado:**
```json
{
  "task": {
    "title": "Aprender Flask",
    "completed": false,
    "metadata": {
      "request_timestamp": "2024-01-15T15:35:00Z",
      "task_age_days": 5,
      "path_parameter": "1",
      "query_parameters": {
        "fields": "title,completed",
        "include_metadata": "true"
      },
      "endpoint": "/tasks/1/details"
    }
  },
  "request_info": {
    "path_parameter": "1",
    "query_parameters": {
      "fields": "title,completed",
      "include_metadata": "true"
    },
    "format": "json"
  }
}
```

### 7. Todos los Query Parameters Combinados
```bash
curl "http://localhost:5000/tasks/1/details?format=summary&lang=es&include_metadata=true"
```

**Nota:** El `include_metadata` se ignora en formato summary, pero demuestra cómo combinar múltiples parámetros.

## 🔧 Parámetros Disponibles

| Parámetro | Tipo | Valores | Default | Descripción |
|-----------|------|---------|---------|-------------|
| `include_metadata` | Query | `true`/`false` | `false` | Incluye información adicional sobre la petición |
| `format` | Query | `json`/`summary`/`full` | `json` | Formato de la respuesta |
| `lang` | Query | `es`/`en` | `es` | Idioma de los mensajes (solo formato summary) |
| `fields` | Query | Lista separada por comas | todos | Campos específicos a incluir |

## 🚨 Manejo de Errores

### Tarea No Encontrada
```bash
curl http://localhost:5000/tasks/999/details
```

**Resultado (404):**
```json
{
  "error": "Tarea no encontrada",
  "message": "No existe una tarea con ID: 999"
}
```

### Formato Inválido
```bash
curl "http://localhost:5000/tasks/1/details?format=invalid"
```

**Resultado (400):**
```json
{
  "error": "Formato inválido",
  "message": "Los formatos válidos son: json, summary, full"
}
```

## 🌟 Diferencias Importantes

### PATH vs QUERY Parameters

```bash
# PATH Parameter (REQUERIDO)
/tasks/1/details
       ↑
   Sin esto la ruta no existe

# QUERY Parameters (OPCIONALES)
/tasks/1/details?format=summary
                ↑
   Sin esto funciona igual, usa defaults
```

## 💡 Tips Prácticos

1. **Orden de query parameters no importa:**
   ```bash
   ?format=full&lang=en    # ✅ Funciona
   ?lang=en&format=full    # ✅ También funciona
   ```

2. **URL encoding para espacios:**
   ```bash
   # Si tuvieras campos con espacios
   ?fields=title,description%20text
   ```

3. **Combinaciones inteligentes:**
   ```bash
   # Para debugging: formato completo con metadata
   ?format=full&include_metadata=true
   
   # Para UI simple: solo resumen en español
   ?format=summary&lang=es
   
   # Para API móvil: solo campos necesarios
   ?fields=title,completed
   ```

## 🔗 Usando con JavaScript

```javascript
// Función helper para construir URLs
function buildTaskDetailsUrl(taskId, options = {}) {
  let url = `http://localhost:5000/tasks/${taskId}/details`;
  
  const params = new URLSearchParams();
  if (options.includeMetadata) params.append('include_metadata', 'true');
  if (options.format) params.append('format', options.format);
  if (options.lang) params.append('lang', options.lang);
  if (options.fields) params.append('fields', options.fields.join(','));
  
  const queryString = params.toString();
  return queryString ? `${url}?${queryString}` : url;
}

// Ejemplos de uso
const urls = [
  buildTaskDetailsUrl('1'), // básico
  buildTaskDetailsUrl('1', { format: 'summary', lang: 'en' }),
  buildTaskDetailsUrl('1', { 
    includeMetadata: true, 
    fields: ['title', 'completed'] 
  })
];

urls.forEach(url => {
  fetch(url)
    .then(response => response.json())
    .then(data => console.log(data));
});
```

---

¡Ahora puedes experimentar con todas las combinaciones de path y query parameters! 🎯

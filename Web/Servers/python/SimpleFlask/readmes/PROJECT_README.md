# Flask MongoDB API - Proyecto Reestructurado

## 📋 Descripción
API REST con Flask, MongoDB y autenticación JWT, completamente reestructurado siguiendo mejores prácticas.

## 🏗️ Estructura del Proyecto

```
SimpleFlask/
├── run.py                      # 🚀 Punto de entrada principal
├── config.py                   # ⚙️ Configuraciones centralizadas
├── requirements.txt            # 📦 Dependencias
├── app/                        # 📱 Aplicación Flask
│   ├── __init__.py            # 🏭 Factory pattern
│   ├── models.py              # 🗄️ Base de datos y modelos
│   ├── utils.py               # 🔧 Utilidades JWT
│   └── routes/                # 🛣️ Blueprints organizados
│       ├── __init__.py        
│       ├── auth.py            # 🔐 Autenticación
│       ├── desk.py            # 📋 Escritorios
│       ├── pages.py           # 🎨 Páginas HTML
│       └── misc.py            # 🧪 Endpoints de prueba
├── templates/                  # 📄 Templates HTML
│   └── welcome.html           
├── static/                     # 🎨 Archivos estáticos
│   └── css/
│       └── style.css          
└── readmes/                       # 📚 Documentación
    ├── MONGODB_SETUP.md
    ├── PROJECT_README.md
    └── .....
```

## 🚀 Instalación y Configuración

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar MongoDB
Sigue las instrucciones en `MONGODB_SETUP.md`

### 3. Variables de entorno (opcional)
```bash
# PowerShell
$env:FLASK_CONFIG = "development"      # development, production, testing
$env:MONGO_URI = "mongodb://localhost:27017/"
$env:DATABASE_NAME = "flask_app"
$env:JWT_SECRET_KEY = "tu-clave-secreta"
```

### 4. Ejecutar la aplicación
```bash
python run.py
```

## 🌐 Endpoints

### Autenticación
- `POST /auth/login` - Iniciar sesión

### Escritorios
- `GET /desk` - Listar escritorios (requiere auth)
- `GET /desk/<id>/` - Obtener escritorio específico (requiere auth)
- `POST /desk` - Crear escritorio (requiere admin)

### Páginas HTML
- `GET /welcome` - Página de bienvenida con estilos

### Pruebas
- `GET /shapes/status/200` - Status 200
- `GET /shapes/status/500` - Status 500
- `GET /shapes/<id>/` - Par/Impar

## 🔐 Credenciales de Prueba

```json
{
  "admin": {
    "username": "admin1",
    "password": "admin123"
  },
  "manager": {
    "username": "manager", 
    "password": "manager123"
  }
}
```

## 🧪 Ejemplo de Uso

### Login
```bash
curl -X POST http://localhost:8003/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin1", "password": "admin123"}'
```

### Listar escritorios
```bash
curl -X GET http://localhost:8003/desk \
  -H "Authorization: Bearer <tu-token>"
```

## 📁 Archivos Principales

- **`run.py`**: Punto de entrada principal de la aplicación
- **`config.py`**: Configuraciones para diferentes entornos
- **`app/__init__.py`**: Factory pattern para crear la app Flask
- **`app/models.py`**: Funciones de base de datos y modelos
- **`app/utils.py`**: Decoradores JWT y utilidades
- **`app/routes/`**: Blueprints organizados por funcionalidad

## 🔧 Desarrollo

### Agregar nueva ruta
1. Crear archivo en `app/routes/`
2. Definir blueprint
3. Registrar en `app/__init__.py`

### Agregar nueva página HTML
1. Crear template en `templates/`
2. Agregar ruta en `app/routes/pages.py`
3. Estilos en `static/css/`

### Modificar configuración
Editar `config.py` para diferentes entornos

## 🏆 Beneficios de la Reestructuración

- ✅ **Modular**: Cada funcionalidad separada
- ✅ **Escalable**: Fácil agregar nuevas características
- ✅ **Mantenible**: Código organizado y limpio
- ✅ **Testeable**: Componentes independientes
- ✅ **Profesional**: Sigue estándares de la industria
- ✅ **Configurable**: Múltiples entornos
- ✅ **Reutilizable**: Componentes independientes
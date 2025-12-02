# staticpages/views.py
from django.http import HttpResponse

def home(request):
    """Vista que devuelve HTML fijo - Catálogo de muebles"""
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>🪑 Catálogo de Muebles - Home</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f5f5dc; }
            .container { max-width: 800px; margin: 0 auto; background: white; 
                        padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            nav a { margin-right: 15px; text-decoration: none; color: #8B4513; font-weight: bold; }
            h1 { color: #654321; }
            .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }
            .product { border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <nav>
                <a href="/static-pages/">🏠 Home</a>
                <a href="/static-pages/about/">ℹ️ About</a>
                <a href="/static-pages/contact/">📧 Contact</a>
                <a href="/dynamic-pages/">🎨 Catálogo Dinámico</a>
                <a href="/api/furniture/">🔌 API</a>
            </nav>
            
            <h1>🪑 Bienvenido a Furniture Catalog</h1>
            <p><strong>¿Qué es contenido estático?</strong></p>
            <ul>
                <li>✅ HTML completamente fijo</li>
                <li>✅ No consulta base de datos</li>
                <li>✅ Respuesta muy rápida</li>
                <li>✅ Ideal para landing pages</li>
            </ul>
            
            <h3>🛋️ Muebles Destacados (Estáticos)</h3>
            <div class="product-grid">
                <div class="product">
                    <h4>Silla Moderna</h4>
                    <p>Altura: 90cm | Ancho: 50cm</p>
                    <p>Material: Madera de roble</p>
                </div>
                <div class="product">
                    <h4>Mesa de Comedor</h4>
                    <p>Altura: 75cm | Ancho: 150cm</p>
                    <p>Material: Pino barnizado</p>
                </div>
            </div>
            
            <p><em>Esta página está definida directamente en el código Python.</em></p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

def about(request):
    """Página About estática"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>📋 Acerca de Furniture Catalog</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f5f5dc; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; }
            h1 { color: #654321; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📋 Acerca de Furniture Catalog</h1>
            <p>Somos un catálogo digital de muebles que demuestra diferentes enfoques web con Django.</p>
            <p><strong>Características:</strong></p>
            <ul>
                <li>🪑 Catálogo de muebles con MongoDB</li>
                <li>📄 Páginas estáticas (esta página)</li>
                <li>🎨 Templates dinámicos desde base de datos</li>
                <li>🔌 API REST para integración</li>
            </ul>
            <a href="/static-pages/">← Volver al Home</a>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

def contact(request):
    """Formulario de contacto estático"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>📧 Contacto</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f5f5dc; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; }
            .form-group { margin: 15px 0; }
            input, textarea { width: 300px; padding: 8px; }
            button { background: #8B4513; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            h1 { color: #654321; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📧 Contacto - Furniture Catalog</h1>
            <p><strong>⚠️ Formulario estático</strong> - No procesa datos realmente.</p>
            
            <form>
                <div class="form-group">
                    <label>Nombre:</label><br>
                    <input type="text" placeholder="Tu nombre">
                </div>
                <div class="form-group">
                    <label>Email:</label><br>
                    <input type="email" placeholder="tu@email.com">
                </div>
                <div class="form-group">
                    <label>¿Qué mueble te interesa?:</label><br>
                    <textarea rows="4" placeholder="Describe el mueble que buscas..."></textarea>
                </div>
                <button type="button" onclick="alert('¡Formulario estático! En la versión dinámica esto funcionaría.')">
                    📤 Enviar Consulta
                </button>
            </form>
            
            <p><a href="/static-pages/">← Volver al Home</a></p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(_):
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


def about(_):
    """Página About estática"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>📋 Acerca de</title>
        <style>body { font-family: Arial; margin: 40px; }</style>
    </head>
    <body>
        <h1>📋 Acerca del Catálogo de Muebles</h1>
        <p>Esta es una página estática creada con Django.</p>
        <p><strong>Características:</strong></p>
        <ul>
            <li>No usa base de datos</li>
            <li>HTML fijo definido en views.py</li>
            <li>Respuesta inmediata</li>
        </ul>
        <a href="/static-pages/">← Volver al Home</a>
    </body>
    </html>
    """
    return HttpResponse(html_content)
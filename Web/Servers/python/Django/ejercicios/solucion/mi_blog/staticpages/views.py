# staticpages/views.py
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """Vista estática - Home page con HTML fijo"""
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📄 Contenido Estático - Home</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f8ff; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .highlight { background: #fffacd; padding: 10px; border-left: 4px solid #ffa500; }
            nav a { margin-right: 15px; text-decoration: none; color: #007cba; }
            nav a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <nav>
                <a href="/static-pages/">🏠 Home</a>
                <a href="/static-pages/about/">ℹ️ About</a>
                <a href="/static-pages/contact/">📧 Contact</a>
                <a href="/dynamic-pages/">🎨 Dynamic Pages</a>
                <a href="/api/v1/blogentries/list/">🔌 API JSON</a>
            </nav>
            
            <h1>📄 Contenido Estático</h1>
            <div class="highlight">
                <h3>🎯 ¿Qué es contenido estático?</h3>
                <p><strong>HTML fijo</strong> que no cambia según la base de datos. Ideal para:</p>
                <ul>
                    <li>Landing pages</li>
                    <li>Páginas "Acerca de"</li>
                    <li>Documentación</li>
                    <li>Términos y condiciones</li>
                </ul>
            </div>
            
            <h2>✨ Características de esta página:</h2>
            <ul>
                <li>✅ No consulta base de datos</li>
                <li>✅ HTML completamente fijo</li>
                <li>✅ Respuesta muy rápida</li>
                <li>✅ Fácil de cachear</li>
            </ul>
            
            <p><em>Este contenido está definido directamente en el código Python (views.py) y nunca cambia.</em></p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

def about(request):
    """Vista estática - Página About"""
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>📋 Acerca de - Contenido Estático</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f8ff; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            nav a { margin-right: 15px; text-decoration: none; color: #007cba; }
        </style>
    </head>
    <body>
        <div class="container">
            <nav>
                <a href="/static-pages/">🏠 Home</a>
                <a href="/static-pages/about/">ℹ️ About</a>
                <a href="/static-pages/contact/">📧 Contact</a>
            </nav>
            
            <h1>📋 Acerca de Mi Blog Django</h1>
            <p>Esta es una página estática que demuestra cómo Django puede servir contenido HTML fijo.</p>
            
            <h2>🎓 Proyecto Educativo</h2>
            <p>Este blog demuestra 3 enfoques diferentes en Django:</p>
            <ol>
                <li><strong>📄 Contenido Estático</strong> - HTML fijo (esta página)</li>
                <li><strong>🎨 Templates Dinámicos</strong> - HTML generado desde BD</li>
                <li><strong>🔌 API JSON</strong> - Datos en formato JSON</li>
            </ol>
            
            <p><em>Página generada estáticamente el: $(date)</em></p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

def contact(request):
    """Vista estática - Formulario de contacto (HTML fijo)"""
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>📧 Contacto - Contenido Estático</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f8ff; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            nav a { margin-right: 15px; text-decoration: none; color: #007cba; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #005a87; }
            .warning { background: #fff3cd; padding: 10px; border: 1px solid #ffeaa7; border-radius: 4px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <nav>
                <a href="/static-pages/">🏠 Home</a>
                <a href="/static-pages/about/">ℹ️ About</a>
                <a href="/static-pages/contact/">📧 Contact</a>
            </nav>
            
            <h1>📧 Contacto</h1>
            
            <div class="warning">
                ⚠️ <strong>Formulario estático:</strong> Este formulario no procesa datos reales. 
                Es solo HTML para demostrar contenido estático.
            </div>
            
            <form>
                <div class="form-group">
                    <label for="name">Nombre:</label>
                    <input type="text" id="name" name="name" placeholder="Tu nombre completo">
                </div>
                
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" placeholder="tu@email.com">
                </div>
                
                <div class="form-group">
                    <label for="message">Mensaje:</label>
                    <textarea id="message" name="message" rows="5" placeholder="Escribe tu mensaje aquí..."></textarea>
                </div>
                
                <button type="button" onclick="alert('¡Formulario estático! No se envía realmente.')">
                    📤 Enviar Mensaje
                </button>
            </form>
            
            <p><em>💡 En una app real, esto sería procesado por una vista dinámica.</em></p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

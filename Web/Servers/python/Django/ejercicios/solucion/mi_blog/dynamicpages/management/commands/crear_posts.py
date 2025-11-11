# dynamicpages/management/commands/crear_posts.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dynamicpages.models import BlogEntry

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Crear usuario si no existe
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user('demo', 'demo@example.com', 'demo123')
        
        autor = User.objects.get(username='demo')
        
        # Crear posts de ejemplo
        posts_ejemplo = [
            {
                'titulo': 'Mi primer post en Django',
                'contenido': 'Este es mi primer post usando Django. ¡Es increíble lo fácil que es!'
            },
            {
                'titulo': 'Aprendiendo Python web',
                'contenido': 'Django hace que el desarrollo web sea muy productivo y divertido.'
            },
            {
                'titulo': 'Modelos y base de datos',
                'contenido': 'Los modelos de Django hacen muy fácil trabajar con bases de datos.'
            }
        ]
        
        for post_data in posts_ejemplo:            
            BlogEntry.objects.get_or_create(
                titulo=post_data['titulo'],
                defaults={
                    'contenido': post_data['contenido'],
                    'autor': autor
                }
            )
        
        self.stdout.write('✅ Posts de ejemplo creados!')
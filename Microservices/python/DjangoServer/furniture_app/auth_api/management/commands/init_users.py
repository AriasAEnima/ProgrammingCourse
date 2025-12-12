"""
Comando para inicializar usuarios en MongoDB
"""
from django.core.management.base import BaseCommand
from auth_api.models import User


class Command(BaseCommand):
    help = 'Inicializa usuarios por defecto en MongoDB'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Inicializando usuarios...')
        User.initialize_users()
        self.stdout.write(self.style.SUCCESS('✅ Usuarios inicializados correctamente'))


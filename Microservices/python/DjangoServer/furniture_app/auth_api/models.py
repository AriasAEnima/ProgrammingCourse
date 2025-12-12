"""
Modelos de Usuario para autenticación con MongoDB
"""
from mongoengine import Document, StringField, DateTimeField
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(Document):
    """
    Modelo de Usuario almacenado en MongoDB
    
    Campos:
        - user_id: ID único del usuario
        - username: Nombre de usuario (único)
        - password_hash: Hash de la contraseña
        - role: Rol del usuario (admin, manager, user)
        - created_at: Fecha de creación
    """
    user_id = StringField(required=True, unique=True)
    username = StringField(required=True, unique=True, max_length=100)
    password_hash = StringField(required=True)
    role = StringField(required=True, choices=['admin', 'manager', 'user'], default='user')
    created_at = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'users',
        'ordering': ['-created_at']
    }
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def set_password(self, password: str) -> None:
        """Establece el hash de la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def initialize_users(cls):
        """Inicializa usuarios por defecto si no existen"""
        if cls.objects.count() == 0:
            # Crear usuario admin
            admin = cls(
                user_id='user-1',
                username='admin1',
                role='admin'
            )
            admin.set_password('admin123')
            admin.save()
            
            # Crear usuario manager
            manager = cls(
                user_id='user-2',
                username='manager',
                role='manager'
            )
            manager.set_password('manager123')
            manager.save()
            
            print("✅ Usuarios iniciales creados en MongoDB")
    
    @classmethod
    def authenticate(cls, username: str, password: str):
        """
        Autentica un usuario
        
        Returns:
            User object si las credenciales son correctas, None si no
        """
        try:
            user = cls.objects.get(username=username)
            if user.check_password(password):
                return user
            return None
        except cls.DoesNotExist:
            return None



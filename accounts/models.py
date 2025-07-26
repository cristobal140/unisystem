from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilUsuario(models.Model):
    """Perfil extendido para usuarios del sistema"""
    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('trabajador', 'Trabajador'),
        ('tecnico', 'Técnico'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='trabajador')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_rol_display()}"
    
    @property
    def es_administrador(self):
        return self.rol == 'administrador'
    
    @property
    def es_trabajador(self):
        return self.rol == 'trabajador'
    
    @property
    def es_tecnico(self):
        return self.rol == 'tecnico'

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crear perfil automáticamente cuando se crea un usuario"""
    if created:
        PerfilUsuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guardar perfil cuando se actualiza el usuario"""
    if hasattr(instance, 'perfilusuario'):
        instance.perfilusuario.save()
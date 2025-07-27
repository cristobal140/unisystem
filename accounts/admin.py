from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'

class UserAdminCustom(UserAdmin):
    inlines = (PerfilUsuarioInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdminCustom, self).get_inline_instances(request, obj)

# Desregistrar el User admin original y registrar el customizado
admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol', 'telefono', 'activo', 'fecha_ingreso']
    list_filter = ['rol', 'activo', 'fecha_ingreso']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
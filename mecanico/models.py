# Importación de módulos necesarios de Django
from django.db import models  # Para definir modelos de base de datos
from django.contrib.auth.models import User  # Para usar el modelo de usuario de Django
from django.utils import timezone  # Para trabajar con fechas y horas
from django.core.validators import MinValueValidator  # Para validar valores mínimos en campos numéricos

# Modelo para clasificar elementos mecánicos en categorías
class Categoria(models.Model):
    # Campo de texto para el nombre de la categoría, único
    nombre = models.CharField(max_length=100, unique=True)
    # Campo de texto opcional para descripción
    descripcion = models.TextField(blank=True, null=True)
    # Campo booleano para indicar si la categoría está activa
    activo = models.BooleanField(default=True)
    # Fecha de creación automática al guardar el registro
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Nombre singular y plural para el modelo en el panel de administración
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        # Ordenar las categorías por nombre
        ordering = ['nombre']
    
    def __str__(self):
        # Representación en texto del modelo
        return self.nombre

# Modelo para definir ubicaciones físicas de almacenamiento
class Ubicacion(models.Model):
    # Nombre de la ubicación
    nombre = models.CharField(max_length=100)
    # Descripción opcional de la ubicación
    descripcion = models.TextField(blank=True, null=True)
    # Campo booleano para indicar si la ubicación está activa
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

# Modelo para representar elementos mecánicos en el inventario
class ElementoMecanico(models.Model):
    # Opciones para el campo de unidad de medida
    UNIDAD_MEDIDA_CHOICES = [
        ('unidad', 'Unidad'),
        ('metro', 'Metro'),
        ('litro', 'Litro'),
        ('kilogramo', 'Kilogramo'),
        ('caja', 'Caja'),
        ('juego', 'Juego'),
    ]
    
    # Código único del elemento
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único del elemento")
    # Nombre del elemento
    nombre = models.CharField(max_length=200)
    # Relación con la categoría del elemento
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    # Descripción opcional del elemento
    descripcion = models.TextField(blank=True, null=True)
    # Características físicas del elemento
    medidas = models.CharField(max_length=100, blank=True, null=True, help_text="Ej: 15x10x5 cm")
    material = models.CharField(max_length=100, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    # Información de stock y ubicación
    cantidad_actual = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.IntegerField(default=5, validators=[MinValueValidator(0)])
    unidad_medida = models.CharField(max_length=20, choices=UNIDAD_MEDIDA_CHOICES, default='unidad')
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT)
    # Precios de compra y venta
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Metadatos adicionales
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.PROTECT, related_name='elementos_creados')
    
    class Meta:
        verbose_name = "Elemento Mecánico"
        verbose_name_plural = "Elementos Mecánicos"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def stock_bajo(self):
        # Propiedad para verificar si el stock está por debajo del mínimo
        return self.cantidad_actual <= self.stock_minimo
    
    @property
    def valor_total_stock(self):
        # Propiedad para calcular el valor total del stock actual
        if self.precio_compra:
            return self.cantidad_actual * self.precio_compra
        return 0

# Modelo para registrar movimientos de stock (entradas, salidas, etc.)
class MovimientoStock(models.Model):
    # Opciones para el tipo de movimiento
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste de inventario'),
        ('devolucion', 'Devolución'),
    ]
    
    # Relación con el elemento mecánico afectado
    elemento = models.ForeignKey(ElementoMecanico, on_delete=models.CASCADE, related_name='movimientos')
    # Tipo de movimiento
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO_CHOICES)
    # Cantidad involucrada en el movimiento
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    # Motivo del movimiento
    motivo = models.TextField()
    # Stock antes y después del movimiento
    stock_anterior = models.IntegerField()
    stock_nuevo = models.IntegerField()
    # Metadatos del movimiento
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.tipo_movimiento.title()} - {self.elemento.nombre} ({self.cantidad})"

# Modelo para representar clientes del taller mecánico
class Cliente(models.Model):
    # Información básica del cliente
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    rut = models.CharField(max_length=12, unique=True, blank=True, null=True)
    # Estado del cliente
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

# Modelo para definir tipos de máquinas que se reparan
class TipoMaquina(models.Model):
    """Tipos de máquinas que se reparan"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Tipo de Máquina"
        verbose_name_plural = "Tipos de Máquinas"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class OrdenTrabajo(models.Model):
    """Órdenes de trabajo para reparaciones"""
    ESTADO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('presupuesto', 'Presupuesto'),
        ('confirmacion', 'Confirmación'),
        ('en_proceso', 'En Proceso'),
        ('terminado', 'Terminado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    numero_orden = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    tipo_maquina = models.ForeignKey(TipoMaquina, on_delete=models.PROTECT)
    
    # Detalles de la máquina
    marca_maquina = models.CharField(max_length=100, blank=True, null=True)
    modelo_maquina = models.CharField(max_length=100, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True)
    ano_maquina = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1900)])

    # Detalles del trabajo
    motivo_ingreso = models.TextField()
    descripcion_trabajo = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ingreso')
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_estimada_entrega = models.DateTimeField(null=True, blank=True)
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)
    
    # Costos
    costo_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Metadatos
    tecnico_asignado = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ordenes_creadas')
    
    class Meta:
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
        ordering = ['-fecha_ingreso']
    
    def __str__(self):
        return f"OT-{self.numero_orden} - {self.cliente.nombre}"

class ElementoUsadoOrden(models.Model):
    """Elementos utilizados en una orden de trabajo"""
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='elementos_usados')
    elemento = models.ForeignKey(ElementoMecanico, on_delete=models.PROTECT)
    cantidad_usada = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    fecha_uso = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = "Elemento Usado en Orden"
        verbose_name_plural = "Elementos Usados en Órdenes"
    
    def __str__(self):
        return f"{self.elemento.nombre} - OT {self.orden.numero_orden}"
    
    @property
    def subtotal(self):
        return self.cantidad_usada * self.precio_unitario

class AgendaDomicilio(models.Model):
    """Agenda para servicios a domicilio"""
    ESTADO_VISITA_CHOICES = [
        ('programada', 'Programada'),
        ('en_camino', 'En Camino'),
        ('revisado', 'Revisado en Domicilio'),
        ('trasladado', 'Trasladado a Taller'),
        ('no_revisado', 'No se Pudo Revisar'),
        ('cancelada', 'Cancelada'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    fecha_visita = models.DateTimeField()
    direccion_visita = models.TextField()
    tipo_maquina = models.ForeignKey(TipoMaquina, on_delete=models.PROTECT)
    descripcion_problema = models.TextField()
    
    estado_visita = models.CharField(max_length=20, choices=ESTADO_VISITA_CHOICES, default='programada')
    tecnico_asignado = models.ForeignKey(User, on_delete=models.PROTECT)
    
    # Resultado de la visita
    observaciones_visita = models.TextField(blank=True, null=True)
    orden_generada = models.OneToOneField(OrdenTrabajo, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.PROTECT, related_name='visitas_creadas')
    
    class Meta:
        verbose_name = "Agenda de Domicilio"
        verbose_name_plural = "Agenda de Domicilios"
        ordering = ['fecha_visita']
    
    def __str__(self):
        return f"{self.cliente.nombre} - {self.fecha_visita.strftime('%d/%m/%Y %H:%M')}"

class HistorialCambios(models.Model):
    """Auditoría de cambios en el sistema"""
    ACCION_CHOICES = [
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('activar', 'Activar'),
        ('desactivar', 'Desactivar'),
    ]
    
    tabla = models.CharField(max_length=50)  # Nombre del modelo afectado
    objeto_id = models.CharField(max_length=50)  # ID del objeto modificado
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    descripcion = models.TextField()  # Descripción del cambio
    
    # Datos del cambio
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    
    # Metadatos
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Historial de Cambios"
        verbose_name_plural = "Historial de Cambios"
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.accion.title()} - {self.tabla} ({self.fecha_cambio.strftime('%d/%m/%Y %H:%M')})"
import uuid
from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class PadronColegio(models.Model):
    """
    Padrón oficial del Colegio de Arquitectos de Córdoba para validar
    si una matrícula está registrada y vigente antes de permitir el registro.
    """
    ESTADO_CHOICES = [
        ('HABILITADA', 'Matrícula Habilitada - Vigente'),
        ('SUSPENDIDA', 'Matrícula Suspendida / Mora'),
        ('INACTIVA', 'Matrícula Inactiva / Baja'),
    ]

    numero_matricula = models.CharField(max_length=50, unique=True)
    nombre_titular = models.CharField(max_length=200)
    dni = models.CharField(max_length=20, blank=True)
    estado_vigencia = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='HABILITADA')
    vigente_hasta = models.DateField(default=date(2027, 12, 31))

    class Meta:
        verbose_name = 'Padrón de Arquitecto'
        verbose_name_plural = 'Padrón de Arquitectos'
        ordering = ['numero_matricula']

    def __str__(self):
        return f"{self.numero_matricula} - {self.nombre_titular} ({self.estado_vigencia})"

    @property
    def esta_vigente(self):
        return self.estado_vigencia == 'HABILITADA' and (self.vigente_hasta >= date.today())


class Sede(models.Model):
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    direccion = models.CharField(max_length=255)
    horario_atencion = models.CharField(max_length=150, default='Lun a Vie · 09:00 – 17:00 h')
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)
    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class Herramienta(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='herramientas')
    sede_predeterminada = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True, related_name='herramientas')
    descripcion = models.TextField()
    especificaciones = models.TextField(blank=True)
    imagen = models.CharField(max_length=255, default='assets/equipos/default.png')
    stock_total = models.PositiveIntegerField(default=1)
    stock_disponible = models.PositiveIntegerField(default=1)
    requiere_capacitacion = models.BooleanField(default=False)
    aviso_capacitacion = models.CharField(max_length=255, default='Requiere capacitación previa')
    dias_max_prestamo = models.PositiveIntegerField(default=3)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Herramienta'
        verbose_name_plural = 'Herramientas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (Stock Total: {self.stock_disponible}/{self.stock_total})"


class StockSede(models.Model):
    """
    Control de stock individual por sede: Córdoba, Villa Allende y Jesús María.
    Permite al administrador gestionar existencias en cada punto.
    """
    herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE, related_name='stock_sedes')
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='stock_herramientas')
    stock_total = models.PositiveIntegerField(default=1)
    stock_disponible = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('herramienta', 'sede')
        verbose_name = 'Stock por Sede'
        verbose_name_plural = 'Stock por Sedes'
        ordering = ['sede', 'herramienta']

    def __str__(self):
        return f"{self.herramienta.nombre} en {self.sede.nombre}: {self.stock_disponible}/{self.stock_total}"


class Matriculado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='matriculado')
    nombre_completo = models.CharField(max_length=200, default='Arq. Damián Coronda')
    numero_matricula = models.CharField(max_length=50, default='M1', unique=True)
    estado_matricula = models.CharField(max_length=100, default='Matrícula Habilitada - M1')
    email = models.EmailField(default='damian.coronda@colegioarq.org.ar')
    telefono = models.CharField(max_length=50, default='+54 9 351 555-0192')
    habilitado = models.BooleanField(default=True)
    capacitaciones_aprobadas = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = 'Matriculado'
        verbose_name_plural = 'Matriculados'

    def __str__(self):
        return f"{self.nombre_completo} ({self.estado_matricula})"

    @property
    def reservas_activas_count(self):
        return self.reservas.filter(estado__in=['CONFIRMADA', 'RETIRADA']).count()


class UsuarioPerfil(models.Model):
    """
    Perfil ampliado de usuario para roles: Arquitecto o Administrador de Pañol.
    """
    ROL_CHOICES = [
        ('ARQUITECTO', 'Arquitecto Matriculado'),
        ('ADMIN_PANOL', 'Administrador de Pañol / Sedes'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=30, choices=ROL_CHOICES, default='ARQUITECTO')
    matriculado = models.ForeignKey(Matriculado, on_delete=models.SET_NULL, null=True, blank=True, related_name='perfiles')
    numero_matricula = models.CharField(max_length=50, blank=True, default='')
    estado_matricula = models.CharField(max_length=100, blank=True, default='')
    sede_asignada = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True, related_name='administradores')

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('CONFIRMADA', 'Confirmada'),
        ('RETIRADA', 'Retirada'),
        ('DEVUELTA', 'Devuelta'),
        ('CANCELADA', 'Cancelada'),
    ]

    codigo = models.CharField(max_length=30, unique=True, blank=True)
    matriculado = models.ForeignKey(Matriculado, on_delete=models.CASCADE, related_name='reservas')
    herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE, related_name='reservas')
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='reservas')
    fecha_inicio = models.DateField()
    fecha_devolucion = models.DateField()
    dias_solicitados = models.PositiveIntegerField(default=1)
    comodato_aceptado = models.BooleanField(default=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='CONFIRMADA')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_creacion']

    def save(self, *args, **kwargs):
        if not self.codigo:
            short_id = uuid.uuid4().hex[:6].upper()
            self.codigo = f"R1-{date.today().strftime('%y%m%d')}-{short_id}"
        
        if self.fecha_inicio and self.fecha_devolucion:
            diff = (self.fecha_devolucion - self.fecha_inicio).days + 1
            self.dias_solicitados = max(1, diff)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.herramienta.nombre} ({self.matriculado.nombre_completo})"


class ControlDevolucion(models.Model):
    """
    Control de condiciones de herramientas devueltas por parte del usuario admin/pañol.
    """
    ESTADO_CONDICION_CHOICES = [
        ('OPTIMO', 'Óptimo estado (sin observaciones)'),
        ('BUENO', 'Buen estado (desgaste normal de obra)'),
        ('CON_DANO', 'Con daño técnico / requiere reparación'),
        ('INCOMPLETO', 'Incompleto / faltante de accesorios o valija'),
    ]

    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='control_devolucion')
    fecha_inspeccion = models.DateTimeField(auto_now_add=True)
    estado_condicion = models.CharField(max_length=30, choices=ESTADO_CONDICION_CHOICES, default='OPTIMO')
    checklist_baterias = models.BooleanField(default=True, verbose_name="Baterías y cargador completos")
    checklist_accesorios = models.BooleanField(default=True, verbose_name="Accesorios completos")
    checklist_limpieza = models.BooleanField(default=True, verbose_name="Limpieza adecuada")
    checklist_maletin = models.BooleanField(default=True, verbose_name="Maletín / valija en condiciones")
    observaciones = models.TextField(blank=True)
    inspeccionado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Control de Devolución'
        verbose_name_plural = 'Controles de Devolución'

    def __str__(self):
        return f"Control {self.reserva.codigo} - {self.get_estado_condicion_display()}"

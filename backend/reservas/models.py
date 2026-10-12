import uuid
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta


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
        return f"{self.nombre} (Stock: {self.stock_disponible}/{self.stock_total})"


class Matriculado(models.Model):
    nombre_completo = models.CharField(max_length=200, default='Arq. Damián Coronda')
    numero_matricula = models.CharField(max_length=50, default='M1')
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
        
        # Calculate days if not provided
        if self.fecha_inicio and self.fecha_devolucion:
            diff = (self.fecha_devolucion - self.fecha_inicio).days + 1
            self.dias_solicitados = max(1, diff)

        super().save(*args, **kwargs)

    def clean(self):
        # Validation 1: Comodato must be accepted
        if not self.comodato_aceptado:
            raise ValidationError("Debe aceptar el Contrato de Comodato para formalizar la reserva.")

        # Validation 2: Max 3 days
        if self.fecha_inicio and self.fecha_devolucion:
            if self.fecha_devolucion < self.fecha_inicio:
                raise ValidationError("La fecha de devolución no puede ser anterior a la de inicio.")
            diff = (self.fecha_devolucion - self.fecha_inicio).days + 1
            if diff > 3:
                raise ValidationError(f"El préstamo no puede superar el límite de 3 días (solicitado: {diff} días).")

        # Validation 3: Maximum 2 simultaneous active reservations per architect
        if self.matriculado:
            activas = self.matriculado.reservas.filter(estado__in=['CONFIRMADA', 'RETIRADA'])
            if self.pk:
                activas = activas.exclude(pk=self.pk)
            if activas.count() >= 2:
                raise ValidationError("Ha alcanzado el límite máximo permitido de 2 equipos reservados en simultáneo.")

        # Validation 4: Stock check
        if self.herramienta and not self.pk:
            if self.herramienta.stock_disponible <= 0:
                raise ValidationError(f"No hay stock disponible para '{self.herramienta.nombre}'.")

    def __str__(self):
        return f"{self.codigo} - {self.herramienta.nombre} ({self.matriculado.nombre_completo})"

from rest_framework import serializers
from django.db import transaction
from .models import Sede, Categoria, Herramienta, Matriculado, Reserva


class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = ['id', 'nombre', 'slug', 'direccion', 'horario_atencion', 'telefono', 'email', 'activa']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug', 'descripcion', 'orden']


class HerramientaSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    categoria_slug = serializers.CharField(source='categoria.slug', read_only=True)
    sede_nombre = serializers.CharField(source='sede_predeterminada.nombre', read_only=True)

    class Meta:
        model = Herramienta
        fields = [
            'id', 'nombre', 'slug', 'categoria', 'categoria_nombre', 'categoria_slug',
            'sede_predeterminada', 'sede_nombre', 'descripcion', 'especificaciones',
            'imagen', 'stock_total', 'stock_disponible', 'requiere_capacitacion',
            'aviso_capacitacion', 'dias_max_prestamo', 'activa'
        ]


class MatriculadoSerializer(serializers.ModelSerializer):
    reservas_activas_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Matriculado
        fields = [
            'id', 'nombre_completo', 'numero_matricula', 'estado_matricula',
            'email', 'telefono', 'habilitado', 'capacitaciones_aprobadas',
            'reservas_activas_count'
        ]


class ReservaSerializer(serializers.ModelSerializer):
    matriculado_detalle = MatriculadoSerializer(source='matriculado', read_only=True)
    herramienta_detalle = HerramientaSerializer(source='herramienta', read_only=True)
    sede_detalle = SedeSerializer(source='sede', read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'codigo', 'matriculado', 'matriculado_detalle',
            'herramienta', 'herramienta_detalle', 'sede', 'sede_detalle',
            'fecha_inicio', 'fecha_devolucion', 'dias_solicitados',
            'comodato_aceptado', 'estado', 'fecha_creacion', 'observaciones'
        ]
        read_only_fields = ['codigo', 'fecha_creacion', 'dias_solicitados']

    def validate(self, attrs):
        comodato = attrs.get('comodato_aceptado', True)
        if not comodato:
            raise serializers.ValidationError({
                "comodato_aceptado": "Es obligatorio aceptar el Contrato de Comodato para formalizar la reserva."
            })

        fecha_inicio = attrs.get('fecha_inicio')
        fecha_devolucion = attrs.get('fecha_devolucion')
        if fecha_inicio and fecha_devolucion:
            if fecha_devolucion < fecha_inicio:
                raise serializers.ValidationError({
                    "fecha_devolucion": "La fecha de devolución no puede ser anterior a la fecha de inicio."
                })
            dias = (fecha_devolucion - fecha_inicio).days + 1
            if dias > 3:
                raise serializers.ValidationError({
                    "fecha_devolucion": f"El período de reserva no puede superar los 3 días corridos (solicitados: {dias} días)."
                })

        matriculado = attrs.get('matriculado')
        if matriculado:
            activas = matriculado.reservas.filter(estado__in=['CONFIRMADA', 'RETIRADA']).count()
            if activas >= 2:
                raise serializers.ValidationError({
                    "non_field_errors": "Has alcanzado el límite máximo de 2 reservas activas simultáneas."
                })

        herramienta = attrs.get('herramienta')
        if herramienta and herramienta.stock_disponible <= 0:
            raise serializers.ValidationError({
                "herramienta": f"No hay stock disponible en este momento para '{herramienta.nombre}'."
            })

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            reserva = super().create(validated_data)
            # Reduce tool stock
            herramienta = reserva.herramienta
            if herramienta.stock_disponible > 0:
                herramienta.stock_disponible -= 1
                herramienta.save(update_fields=['stock_disponible'])
            return reserva

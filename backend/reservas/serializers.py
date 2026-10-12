from datetime import date
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import (
    Sede,
    Categoria,
    Herramienta,
    StockSede,
    Matriculado,
    UsuarioPerfil,
    Reserva,
    ControlDevolucion,
    PadronColegio
)


class PadronSerializer(serializers.ModelSerializer):
    esta_vigente = serializers.BooleanField(read_only=True)

    class Meta:
        model = PadronColegio
        fields = ['numero_matricula', 'nombre_titular', 'estado_vigencia', 'vigente_hasta', 'esta_vigente']


class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = ['id', 'nombre', 'slug', 'direccion', 'horario_atencion', 'telefono', 'email', 'activa']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug', 'descripcion', 'orden']


class StockSedeSerializer(serializers.ModelSerializer):
    herramienta_nombre = serializers.CharField(source='herramienta.nombre', read_only=True)
    herramienta_imagen = serializers.CharField(source='herramienta.imagen', read_only=True)
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)

    class Meta:
        model = StockSede
        fields = [
            'id', 'herramienta', 'herramienta_nombre', 'herramienta_imagen',
            'sede', 'sede_nombre', 'stock_total', 'stock_disponible'
        ]


class HerramientaSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    categoria_slug = serializers.CharField(source='categoria.slug', read_only=True)
    sede_nombre = serializers.CharField(source='sede_predeterminada.nombre', read_only=True)
    stock_sedes = StockSedeSerializer(many=True, read_only=True)

    class Meta:
        model = Herramienta
        fields = [
            'id', 'nombre', 'slug', 'categoria', 'categoria_nombre', 'categoria_slug',
            'sede_predeterminada', 'sede_nombre', 'descripcion', 'especificaciones',
            'imagen', 'stock_total', 'stock_disponible', 'stock_sedes',
            'requiere_capacitacion', 'aviso_capacitacion', 'dias_max_prestamo', 'activa'
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


class ControlDevolucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlDevolucion
        fields = [
            'id', 'reserva', 'fecha_inspeccion', 'estado_condicion',
            'checklist_baterias', 'checklist_accesorios', 'checklist_limpieza',
            'checklist_maletin', 'observaciones', 'inspeccionado_por'
        ]
        read_only_fields = ['fecha_inspeccion']


class ReservaSerializer(serializers.ModelSerializer):
    matriculado_detalle = MatriculadoSerializer(source='matriculado', read_only=True)
    herramienta_detalle = HerramientaSerializer(source='herramienta', read_only=True)
    sede_detalle = SedeSerializer(source='sede', read_only=True)
    control_devolucion = ControlDevolucionSerializer(read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'codigo', 'matriculado', 'matriculado_detalle',
            'herramienta', 'herramienta_detalle', 'sede', 'sede_detalle',
            'fecha_inicio', 'fecha_devolucion', 'dias_solicitados',
            'comodato_aceptado', 'estado', 'fecha_creacion', 'observaciones',
            'control_devolucion'
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
        sede = attrs.get('sede')
        if herramienta and sede:
            # Check stock in the selected sede
            stock_sede = StockSede.objects.filter(herramienta=herramienta, sede=sede).first()
            if stock_sede and stock_sede.stock_disponible <= 0:
                raise serializers.ValidationError({
                    "herramienta": f"No hay stock disponible de '{herramienta.nombre}' en la sede {sede.nombre}."
                })
            elif not stock_sede and herramienta.stock_disponible <= 0:
                raise serializers.ValidationError({
                    "herramienta": f"No hay stock disponible para '{herramienta.nombre}'."
                })

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            reserva = super().create(validated_data)
            # Reduce tool stock in the specific sede
            stock_sede = StockSede.objects.filter(herramienta=reserva.herramienta, sede=reserva.sede).first()
            if stock_sede and stock_sede.stock_disponible > 0:
                stock_sede.stock_disponible -= 1
                stock_sede.save(update_fields=['stock_disponible'])

            # Also reduce global tool stock
            herramienta = reserva.herramienta
            if herramienta.stock_disponible > 0:
                herramienta.stock_disponible -= 1
                herramienta.save(update_fields=['stock_disponible'])

            return reserva


# Auth Serializers
class LoginSerializer(serializers.Serializer):
    username_or_matricula = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user_input = attrs.get('username_or_matricula')
        password = attrs.get('password')

        # Try finding by username, email, or matricula
        user = None
        if '@' in user_input:
            user = User.objects.filter(email__iexact=user_input).first()
        else:
            # Check if it's a matricula
            matriculado = Matriculado.objects.filter(numero_matricula__iexact=user_input).first()
            if matriculado and matriculado.user:
                user = matriculado.user
            else:
                user = User.objects.filter(username__iexact=user_input).first()

        if user and user.check_password(password):
            attrs['user'] = user
            return attrs

        raise serializers.ValidationError("Credenciales inválidas. Verifique usuario/matrícula y contraseña.")


class RegistroMatriculadoSerializer(serializers.Serializer):
    numero_matricula = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    telefono = serializers.CharField(max_length=50, required=False, default='')

    def validate_numero_matricula(self, value):
        val = value.strip().upper()
        # 1. Corroborar vigencia en el Padrón Oficial
        padron = PadronColegio.objects.filter(numero_matricula__iexact=val).first()
        if not padron:
            raise serializers.ValidationError(
                f"La matrícula '{val}' no existe en el Padrón Oficial del Colegio de Arquitectos."
            )
        if not padron.esta_vigente:
            raise serializers.ValidationError(
                f"La matrícula '{val}' no se encuentra habilitada (Estado: {padron.get_estado_vigencia_display()}). Regularice su situación para acceder al préstamo."
            )

        # 2. Corroborar que no esté ya registrada en el sistema
        if Matriculado.objects.filter(numero_matricula__iexact=val, user__isnull=False).exists():
            raise serializers.ValidationError(
                f"La matrícula '{val}' ya posee una cuenta registrada. Puede iniciar sesión directamente."
            )

        return val

    def validate_email(self, value):
        val = value.strip().lower()
        if User.objects.filter(email__iexact=val).exists():
            raise serializers.ValidationError("El correo electrónico ya está registrado.")
        return val

    def create(self, validated_data):
        mat_num = validated_data['numero_matricula']
        email = validated_data['email']
        pwd = validated_data['password']
        tel = validated_data.get('telefono', '')

        padron = PadronColegio.objects.get(numero_matricula__iexact=mat_num)

        with transaction.atomic():
            user = User.objects.create_user(
                username=mat_num.lower(),
                email=email,
                password=pwd,
                first_name=padron.nombre_titular
            )

            matriculado, _ = Matriculado.objects.update_or_create(
                numero_matricula=mat_num,
                defaults={
                    'user': user,
                    'nombre_completo': padron.nombre_titular,
                    'estado_matricula': padron.get_estado_vigencia_display(),
                    'email': email,
                    'telefono': tel or '+54 9 351 000-0000',
                    'habilitado': True
                }
            )

            UsuarioPerfil.objects.create(
                user=user,
                rol='ARQUITECTO',
                matriculado=matriculado,
                numero_matricula=mat_num,
                estado_matricula=matriculado.estado_matricula
            )

            return user

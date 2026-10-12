from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction
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
from .serializers import (
    SedeSerializer,
    CategoriaSerializer,
    HerramientaSerializer,
    StockSedeSerializer,
    MatriculadoSerializer,
    ReservaSerializer,
    ControlDevolucionSerializer,
    LoginSerializer,
    RegistroMatriculadoSerializer,
    PadronSerializer
)


class SedeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sede.objects.filter(activa=True)
    serializer_class = SedeSerializer


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all().order_by('orden', 'nombre')
    serializer_class = CategoriaSerializer


class HerramientaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Herramienta.objects.filter(activa=True)
    serializer_class = HerramientaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        categoria = self.request.query_params.get('categoria', None)
        buscar = self.request.query_params.get('buscar', None)
        sede_id = self.request.query_params.get('sede', None)

        if categoria and categoria != 'todas' and categoria != 'Todas':
            qs = qs.filter(Q(categoria__slug=categoria) | Q(categoria__nombre__iexact=categoria))

        if buscar:
            qs = qs.filter(
                Q(nombre__icontains=buscar) |
                Q(descripcion__icontains=buscar) |
                Q(categoria__nombre__icontains=buscar)
            )

        return qs


class StockSedeViewSet(viewsets.ModelViewSet):
    """
    Control de Stock en las 3 sedes: Córdoba (Laprida 40), Villa Allende y Jesús María.
    """
    queryset = StockSede.objects.all().select_related('herramienta', 'sede')
    serializer_class = StockSedeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        sede_id = self.request.query_params.get('sede', None)
        if sede_id:
            qs = qs.filter(sede_id=sede_id)
        return qs

    @action(detail=True, methods=['patch'])
    def ajustar_stock(self, request, pk=None):
        stock_sede = self.get_object()
        nuevo_total = request.data.get('stock_total')
        nuevo_disponible = request.data.get('stock_disponible')

        if nuevo_total is not None:
            stock_sede.stock_total = max(0, int(nuevo_total))
        if nuevo_disponible is not None:
            stock_sede.stock_disponible = max(0, min(stock_sede.stock_total, int(nuevo_disponible)))

        stock_sede.save()

        # Recalcular stock global de la herramienta
        herramienta = stock_sede.herramienta
        totales = StockSede.objects.filter(herramienta=herramienta)
        herramienta.stock_total = sum(s.stock_total for s in totales)
        herramienta.stock_disponible = sum(s.stock_disponible for s in totales)
        herramienta.save()

        return Response(self.get_serializer(stock_sede).data)


class MatriculadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Matriculado.objects.all()
    serializer_class = MatriculadoSerializer

    @action(detail=False, methods=['get'])
    def actual(self, request):
        matriculado = Matriculado.objects.first()
        if not matriculado:
            matriculado = Matriculado.objects.create(
                nombre_completo='Arq. Damián Coronda',
                numero_matricula='M1',
                estado_matricula='Matrícula Habilitada - M1'
            )
        serializer = self.get_serializer(matriculado)
        return Response(serializer.data)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all().order_by('-fecha_creacion')
    serializer_class = ReservaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        matriculado_id = self.request.query_params.get('matriculado', None)
        estado = self.request.query_params.get('estado', None)
        sede_id = self.request.query_params.get('sede', None)

        if matriculado_id:
            qs = qs.filter(matriculado_id=matriculado_id)
        if estado:
            qs = qs.filter(estado=estado)
        if sede_id:
            qs = qs.filter(sede_id=sede_id)
        return qs

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.estado in ['DEVUELTA', 'CANCELADA']:
            return Response(
                {"error": f"La reserva ya se encuentra {reserva.estado.lower()}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Restaurar stock de la sede
            stock_sede = StockSede.objects.filter(herramienta=reserva.herramienta, sede=reserva.sede).first()
            if stock_sede:
                stock_sede.stock_disponible = min(stock_sede.stock_total, stock_sede.stock_disponible + 1)
                stock_sede.save(update_fields=['stock_disponible'])

            # Restaurar stock global
            herramienta = reserva.herramienta
            herramienta.stock_disponible = min(herramienta.stock_total, herramienta.stock_disponible + 1)
            herramienta.save(update_fields=['stock_disponible'])

            reserva.estado = 'CANCELADA'
            reserva.save(update_fields=['estado'])

        return Response(self.get_serializer(reserva).data)

    @action(detail=True, methods=['post'])
    def controlar_devolucion(self, request, pk=None):
        """
        Endpoint para el usuario Administrador / Pañol:
        Controla que la herramienta se devuelva en condiciones y actualiza el stock de la sede.
        """
        reserva = self.get_object()
        if reserva.estado == 'DEVUELTA':
            return Response(
                {"error": "Esta reserva ya fue devuelta previamente."},
                status=status.HTTP_400_BAD_REQUEST
            )

        estado_condicion = request.data.get('estado_condicion', 'OPTIMO')
        checklist_baterias = bool(request.data.get('checklist_baterias', True))
        checklist_accesorios = bool(request.data.get('checklist_accesorios', True))
        checklist_limpieza = bool(request.data.get('checklist_limpieza', True))
        checklist_maletin = bool(request.data.get('checklist_maletin', True))
        observaciones = request.data.get('observaciones', '')

        with transaction.atomic():
            # Crear o actualizar registro de inspección de devolución
            control, _ = ControlDevolucion.objects.update_or_create(
                reserva=reserva,
                defaults={
                    'estado_condicion': estado_condicion,
                    'checklist_baterias': checklist_baterias,
                    'checklist_accesorios': checklist_accesorios,
                    'checklist_limpieza': checklist_limpieza,
                    'checklist_maletin': checklist_maletin,
                    'observaciones': observaciones,
                }
            )

            reserva.estado = 'DEVUELTA'
            reserva.save(update_fields=['estado'])

            # Si la herramienta quedó en condición operativa (ÓPTIMO o BUENO), se reintegra al stock disponible
            if estado_condicion in ['OPTIMO', 'BUENO']:
                stock_sede = StockSede.objects.filter(herramienta=reserva.herramienta, sede=reserva.sede).first()
                if stock_sede:
                    stock_sede.stock_disponible = min(stock_sede.stock_total, stock_sede.stock_disponible + 1)
                    stock_sede.save(update_fields=['stock_disponible'])

                herramienta = reserva.herramienta
                herramienta.stock_disponible = min(herramienta.stock_total, herramienta.stock_disponible + 1)
                herramienta.save(update_fields=['stock_disponible'])

        return Response({
            "mensaje": f"Devolución registrada con éxito. Estado: {control.get_estado_condicion_display()}",
            "reserva": self.get_serializer(reserva).data
        })


# API Views de Autenticación y Validación de Matrícula
class VerificarMatriculaView(APIView):
    """
    Verifica si una matrícula existe y está vigente en el Padrón Oficial del Colegio.
    """
    def get(self, request):
        matricula = request.query_params.get('matricula', '').strip().upper()
        if not matricula:
            return Response({"error": "Debe proporcionar un número de matrícula."}, status=status.HTTP_400_BAD_REQUEST)

        padron = PadronColegio.objects.filter(numero_matricula__iexact=matricula).first()
        if not padron:
            return Response({
                "valida": False,
                "mensaje": f"La matrícula '{matricula}' no fue encontrada en el Padrón Oficial de la Regional 1."
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "valida": padron.esta_vigente,
            "numero_matricula": padron.numero_matricula,
            "nombre_titular": padron.nombre_titular,
            "estado_vigencia": padron.get_estado_vigencia_display(),
            "vigente_hasta": padron.vigente_hasta,
            "mensaje": "Matrícula habilitada y vigente." if padron.esta_vigente else "Matrícula no habilitada (posee deuda o suspensión)."
        })


class RegistroView(APIView):
    """
    Registro de profesional matriculado con corroboración obligatoria de matrícula vigente.
    """
    def post(self, request):
        serializer = RegistroMatriculadoSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            matriculado = user.matriculado
            return Response({
                "mensaje": "Registro completado con éxito. Matrícula habilitada en el sistema.",
                "usuario": {
                    "id": user.id,
                    "username": user.username,
                    "nombre": matriculado.nombre_completo,
                    "matricula": matriculado.numero_matricula,
                    "estado_matricula": matriculado.estado_matricula,
                    "rol": "ARQUITECTO"
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Inicio de sesión para Arquitectos o Administradores de Pañol.
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            perfil = getattr(user, 'perfil', None)
            matriculado = getattr(user, 'matriculado', None)

            rol = perfil.rol if perfil else ('ADMIN_PANOL' if user.is_staff else 'ARQUITECTO')
            nombre = matriculado.nombre_completo if matriculado else (user.first_name or user.username)
            matricula = matriculado.numero_matricula if matriculado else (perfil.numero_matricula if perfil else '')
            estado = matriculado.estado_matricula if matriculado else (perfil.estado_matricula if perfil else 'Administrador de Sede')

            return Response({
                "mensaje": "Inicio de sesión exitoso.",
                "usuario": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "nombre": nombre,
                    "matricula": matricula,
                    "estado_matricula": estado,
                    "rol": rol
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Sede, Categoria, Herramienta, Matriculado, Reserva
from .serializers import (
    SedeSerializer,
    CategoriaSerializer,
    HerramientaSerializer,
    MatriculadoSerializer,
    ReservaSerializer
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

        if sede_id:
            qs = qs.filter(Q(sede_predeterminada_id=sede_id) | Q(sede_predeterminada__isnull=True))

        return qs


class MatriculadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Matriculado.objects.all()
    serializer_class = MatriculadoSerializer

    @action(detail=False, methods=['get'])
    def actual(self, request):
        """Devuelve el matriculado autenticado/activo para el módulo"""
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
        if matriculado_id:
            qs = qs.filter(matriculado_id=matriculado_id)
        return qs

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.estado in ['DEVUELTA', 'CANCELADA']:
            return Response(
                {"error": f"La reserva ya se encuentra {reserva.estado.lower()}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Devolver stock
        herramienta = reserva.herramienta
        herramienta.stock_disponible = min(herramienta.stock_total, herramienta.stock_disponible + 1)
        herramienta.save(update_fields=['stock_disponible'])

        reserva.estado = 'CANCELADA'
        reserva.save(update_fields=['estado'])

        return Response(self.get_serializer(reserva).data)

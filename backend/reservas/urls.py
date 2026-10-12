from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SedeViewSet,
    CategoriaViewSet,
    HerramientaViewSet,
    StockSedeViewSet,
    MatriculadoViewSet,
    ReservaViewSet,
    VerificarMatriculaView,
    RegistroView,
    LoginView
)

router = DefaultRouter()
router.register(r'sedes', SedeViewSet, basename='sede')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'herramientas', HerramientaViewSet, basename='herramienta')
router.register(r'stock-sedes', StockSedeViewSet, basename='stock-sede')
router.register(r'matriculados', MatriculadoViewSet, basename='matriculado')
router.register(r'reservas', ReservaViewSet, basename='reserva')

urlpatterns = [
    # Autenticación y Verificación de Matrículas
    path('auth/verificar-matricula/', VerificarMatriculaView.as_view(), name='verificar-matricula'),
    path('auth/registro/', RegistroView.as_view(), name='registro'),
    path('auth/login/', LoginView.as_view(), name='login'),
    # Enrutamiento REST
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SedeViewSet,
    CategoriaViewSet,
    HerramientaViewSet,
    MatriculadoViewSet,
    ReservaViewSet
)

router = DefaultRouter()
router.register(r'sedes', SedeViewSet, basename='sede')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'herramientas', HerramientaViewSet, basename='herramienta')
router.register(r'matriculados', MatriculadoViewSet, basename='matriculado')
router.register(r'reservas', ReservaViewSet, basename='reserva')

urlpatterns = [
    path('', include(router.urls)),
]

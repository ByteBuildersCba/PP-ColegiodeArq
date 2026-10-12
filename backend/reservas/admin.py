from django.contrib import admin
from .models import Sede, Categoria, Herramienta, Matriculado, Reserva


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'horario_atencion', 'activa')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'orden')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'stock_disponible', 'stock_total', 'requiere_capacitacion', 'activa')
    list_filter = ('categoria', 'requiere_capacitacion', 'activa')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Matriculado)
class MatriculadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'numero_matricula', 'estado_matricula', 'habilitado')
    search_fields = ('nombre_completo', 'numero_matricula')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'matriculado', 'herramienta', 'sede', 'fecha_inicio', 'fecha_devolucion', 'estado')
    list_filter = ('estado', 'sede')
    search_fields = ('codigo', 'matriculado__nombre_completo', 'herramienta__nombre')

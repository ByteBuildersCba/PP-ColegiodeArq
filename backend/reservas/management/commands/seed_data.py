from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from reservas.models import (
    Sede,
    Categoria,
    Herramienta,
    StockSede,
    Matriculado,
    UsuarioPerfil,
    Reserva,
    PadronColegio
)


class Command(BaseCommand):
    help = 'Carga los datos iniciales de Sedes, Padrón, Herramientas por Sedes y Usuarios para Caja de Herramientas R1'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Iniciando carga de datos iniciales...'))

        # 1. Padrón Oficial de Arquitectos
        padron_data = [
            {'numero_matricula': 'M1', 'nombre_titular': 'Arq. Damián Coronda', 'dni': '28.450.123', 'estado_vigencia': 'HABILITADA'},
            {'numero_matricula': 'M2045', 'nombre_titular': 'Arq. María Eugenia Silva', 'dni': '32.114.582', 'estado_vigencia': 'HABILITADA'},
            {'numero_matricula': 'M3180', 'nombre_titular': 'Arq. Lucas Benítez', 'dni': '34.901.233', 'estado_vigencia': 'HABILITADA'},
            {'numero_matricula': 'M4521', 'nombre_titular': 'Arq. Florencia Rossi', 'dni': '30.887.412', 'estado_vigencia': 'HABILITADA'},
            {'numero_matricula': 'M9999', 'nombre_titular': 'Arq. Roberto Morales', 'dni': '22.341.900', 'estado_vigencia': 'SUSPENDIDA'},
        ]

        for p in padron_data:
            PadronColegio.objects.update_or_create(
                numero_matricula=p['numero_matricula'],
                defaults=p
            )
        self.stdout.write(self.style.SUCCESS(f'  - Padrón oficial cargado ({len(padron_data)} arquitectos)'))

        # 2. Sedes
        sedes_data = [
            {
                'nombre': 'Laprida 40 - Córdoba',
                'slug': 'cordoba',
                'direccion': 'Mariano Moreno / Laprida 40, B° Güemes, Córdoba Capital',
                'horario_atencion': 'Lun a Vie · 09:00 – 17:00 h',
                'telefono': '+54 351 468-4500',
                'email': 'regional1@colegio-arquitectos.com.ar',
            },
            {
                'nombre': 'Villa Allende',
                'slug': 'villa-allende',
                'direccion': 'Av. Goycoechea 850, Villa Allende, Córdoba',
                'horario_atencion': 'Mar y Jue · 10:00 – 15:00 h',
                'telefono': '+54 3543 43-2100',
                'email': 'villaallende@colegio-arquitectos.com.ar',
            },
            {
                'nombre': 'Jesús María',
                'slug': 'jesus-maria',
                'direccion': 'San Martín 450, Jesús María, Córdoba',
                'horario_atencion': 'Mié y Vie · 09:00 – 14:00 h',
                'telefono': '+54 3525 42-1500',
                'email': 'jesusmaria@colegio-arquitectos.com.ar',
            },
        ]

        sedes_dict = {}
        for s in sedes_data:
            sede_obj, _ = Sede.objects.update_or_create(slug=s['slug'], defaults=s)
            sedes_dict[s['slug']] = sede_obj

        # 3. Categorías
        categorias_data = [
            {'nombre': 'Medición y topografía', 'slug': 'medicion-y-topografia', 'orden': 1},
            {'nombre': 'Instalaciones Eléctricas', 'slug': 'instalaciones-electricas', 'orden': 2},
            {'nombre': 'Instalaciones de Gas', 'slug': 'instalaciones-de-gas', 'orden': 3},
            {'nombre': 'Instalaciones varias', 'slug': 'instalaciones-varias', 'orden': 4},
        ]

        categorias_dict = {}
        for c in categorias_data:
            cat_obj, _ = Categoria.objects.update_or_create(slug=c['slug'], defaults=c)
            categorias_dict[c['slug']] = cat_obj

        # 4. Herramientas
        herramientas_data = [
            {
                'nombre': 'Nivel Láser Multilínea',
                'slug': 'nivel-laser-multilinea',
                'categoria': categorias_dict['medicion-y-topografia'],
                'sede_predeterminada': sedes_dict['cordoba'],
                'descripcion': 'Proyección 360° de líneas horizontales y verticales con trípode.',
                'imagen': 'assets/equipos/nivel-laser.png',
                'stock_total': 7,
                'stock_disponible': 7,
                'requiere_capacitacion': False,
            },
            {
                'nombre': 'Telurímetro',
                'slug': 'telurimetro',
                'categoria': categorias_dict['instalaciones-electricas'],
                'sede_predeterminada': sedes_dict['cordoba'],
                'descripcion': 'Medición de resistencia de puesta a tierra con jabalinas y cables.',
                'imagen': 'assets/equipos/telurimetro.png',
                'stock_total': 4,
                'stock_disponible': 4,
                'requiere_capacitacion': True,
                'aviso_capacitacion': 'Requiere capacitación previa',
            },
            {
                'nombre': 'Esclerómetro',
                'slug': 'esclerometro',
                'categoria': categorias_dict['instalaciones-varias'],
                'sede_predeterminada': sedes_dict['cordoba'],
                'descripcion': 'Ensayo no destructivo de resistencia superficial del hormigón.',
                'imagen': 'assets/equipos/esclerometro.png',
                'stock_total': 5,
                'stock_disponible': 5,
                'requiere_capacitacion': True,
                'aviso_capacitacion': 'Requiere capacitación previa',
            },
            {
                'nombre': 'Distanciómetro Láser',
                'slug': 'distanciometro-laser',
                'categoria': categorias_dict['medicion-y-topografia'],
                'sede_predeterminada': sedes_dict['cordoba'],
                'descripcion': 'Medición de distancias de hasta 100 m con cálculo de áreas.',
                'imagen': 'assets/equipos/distanciometro.png',
                'stock_total': 10,
                'stock_disponible': 10,
                'requiere_capacitacion': False,
            },
            {
                'nombre': 'Pinza Amperométrica',
                'slug': 'pinza-amperometrica',
                'categoria': categorias_dict['instalaciones-electricas'],
                'sede_predeterminada': sedes_dict['cordoba'],
                'descripcion': 'Medición de corriente, tensión y continuidad en tableros.',
                'imagen': 'assets/equipos/pinza-amperometrica.png',
                'stock_total': 8,
                'stock_disponible': 8,
                'requiere_capacitacion': False,
            },
            {
                'nombre': 'Detector de Fugas de Gas',
                'slug': 'detector-de-fugas-de-gas',
                'categoria': categorias_dict['instalaciones-de-gas'],
                'sede_predeterminada': sedes_dict['cordoba'],
                'descripcion': 'Detección de gases combustibles con sonda flexible y alarma.',
                'imagen': 'assets/equipos/detector-gas.png',
                'stock_total': 5,
                'stock_disponible': 5,
                'requiere_capacitacion': False,
            },
            {
                'nombre': 'Kit Manómetro Prueba Hermeticidad',
                'slug': 'kit-manometro-prueba-hermeticidad',
                'categoria': categorias_dict['instalaciones-de-gas'],
                'sede_predeterminada': sedes_dict['cordoba'],
                'descripcion': 'Prueba de hermeticidad en cañerías de gas según normativa.',
                'imagen': 'assets/equipos/manometro.png',
                'stock_total': 4,
                'stock_disponible': 4,
                'requiere_capacitacion': True,
                'aviso_capacitacion': 'Requiere capacitación previa',
            },
            {
                'nombre': 'Cámara Termográfica',
                'slug': 'camara-termografica',
                'categoria': categorias_dict['instalaciones-varias'],
                'sede_predeterminada': sedes_dict['cordoba'],
                'descripcion': 'Detección de puentes térmicos, humedades y fallas eléctricas.',
                'imagen': 'assets/equipos/camara-termografica.png',
                'stock_total': 3,
                'stock_disponible': 3,
                'requiere_capacitacion': False,
            },
        ]

        herramientas_dict = {}
        for h in herramientas_data:
            herramienta_obj, _ = Herramienta.objects.update_or_create(slug=h['slug'], defaults=h)
            herramientas_dict[h['slug']] = herramienta_obj

        # 5. Stock distribuido en las 3 Sedes (Córdoba, Villa Allende, Jesús María)
        # Distribución representativa:
        distribucion_stock = [
            # Nivel Láser (Córdoba: 4, Villa Allende: 2, Jesús María: 1)
            ('nivel-laser-multilinea', 'cordoba', 4, 4),
            ('nivel-laser-multilinea', 'villa-allende', 2, 2),
            ('nivel-laser-multilinea', 'jesus-maria', 1, 1),
            # Telurímetro (Córdoba: 2, Villa Allende: 1, Jesús María: 1)
            ('telurimetro', 'cordoba', 2, 2),
            ('telurimetro', 'villa-allende', 1, 1),
            ('telurimetro', 'jesus-maria', 1, 1),
            # Esclerómetro (Córdoba: 3, Villa Allende: 1, Jesús María: 1)
            ('esclerometro', 'cordoba', 3, 3),
            ('esclerometro', 'villa-allende', 1, 1),
            ('esclerometro', 'jesus-maria', 1, 1),
            # Distanciómetro (Córdoba: 6, Villa Allende: 2, Jesús María: 2)
            ('distanciometro-laser', 'cordoba', 6, 6),
            ('distanciometro-laser', 'villa-allende', 2, 2),
            ('distanciometro-laser', 'jesus-maria', 2, 2),
            # Pinza Amperométrica (Córdoba: 5, Villa Allende: 2, Jesús María: 1)
            ('pinza-amperometrica', 'cordoba', 5, 5),
            ('pinza-amperometrica', 'villa-allende', 2, 2),
            ('pinza-amperometrica', 'jesus-maria', 1, 1),
            # Detector de Gas (Córdoba: 3, Villa Allende: 1, Jesús María: 1)
            ('detector-de-fugas-de-gas', 'cordoba', 3, 3),
            ('detector-de-fugas-de-gas', 'villa-allende', 1, 1),
            ('detector-de-fugas-de-gas', 'jesus-maria', 1, 1),
            # Manómetro (Córdoba: 2, Villa Allende: 1, Jesús María: 1)
            ('kit-manometro-prueba-hermeticidad', 'cordoba', 2, 2),
            ('kit-manometro-prueba-hermeticidad', 'villa-allende', 1, 1),
            ('kit-manometro-prueba-hermeticidad', 'jesus-maria', 1, 1),
            # Cámara Termográfica (Córdoba: 2, Villa Allende: 1, Jesús María: 0)
            ('camara-termografica', 'cordoba', 2, 2),
            ('camara-termografica', 'villa-allende', 1, 1),
            ('camara-termografica', 'jesus-maria', 0, 0),
        ]

        for h_slug, s_slug, total, disp in distribucion_stock:
            h_obj = herramientas_dict[h_slug]
            s_obj = sedes_dict[s_slug]
            StockSede.objects.update_or_create(
                herramienta=h_obj,
                sede=s_obj,
                defaults={'stock_total': total, 'stock_disponible': disp}
            )

        self.stdout.write(self.style.SUCCESS('  - Stock cargado en las 3 sedes (Córdoba, Villa Allende, Jesús María)'))

        # 6. Usuarios del Sistema
        # A) Usuario Arquitecto Matriculado Demo
        user_arq, _ = User.objects.update_or_create(
            username='m1',
            defaults={
                'email': 'damian.coronda@colegioarq.org.ar',
                'first_name': 'Arq. Damián Coronda',
                'is_staff': False
            }
        )
        user_arq.set_password('colegio123')
        user_arq.save()

        matriculado, _ = Matriculado.objects.update_or_create(
            numero_matricula='M1',
            defaults={
                'user': user_arq,
                'nombre_completo': 'Arq. Damián Coronda',
                'estado_matricula': 'Matrícula Habilitada - M1',
                'email': 'damian.coronda@colegioarq.org.ar',
                'telefono': '+54 9 351 555-0192',
                'habilitado': True,
                'capacitaciones_aprobadas': ['telurimetro', 'esclerometro', 'manometro']
            }
        )

        UsuarioPerfil.objects.update_or_create(
            user=user_arq,
            defaults={
                'rol': 'ARQUITECTO',
                'matriculado': matriculado,
                'numero_matricula': 'M1',
                'estado_matricula': 'Matrícula Habilitada - M1'
            }
        )
        self.stdout.write(f"  - Usuario Arquitecto: m1 (pass: colegio123)")

        # B) Usuario Admin de Pañol / Sedes
        user_admin, _ = User.objects.update_or_create(
            username='admin.panol',
            defaults={
                'email': 'admin.panol@colegioarq.org.ar',
                'first_name': 'Administrador de Pañol R1',
                'is_staff': True,
                'is_superuser': True
            }
        )
        user_admin.set_password('admin123')
        user_admin.save()

        UsuarioPerfil.objects.update_or_create(
            user=user_admin,
            defaults={
                'rol': 'ADMIN_PANOL',
                'numero_matricula': 'ADM-R1',
                'estado_matricula': 'Administrador General de Pañol',
                'sede_asignada': sedes_dict['cordoba']
            }
        )
        self.stdout.write(f"  - Usuario Admin Pañol: admin.panol (pass: admin123)")

        # C) Reserva de prueba activa para que el admin pueda probar devolución inmediatamente
        hoy = date.today()
        reserva_demo, _ = Reserva.objects.update_or_create(
            codigo='R1-26-DEMO1',
            defaults={
                'matriculado': matriculado,
                'herramienta': herramientas_dict['nivel-laser-multilinea'],
                'sede': sedes_dict['cordoba'],
                'fecha_inicio': hoy - timedelta(days=2),
                'fecha_devolucion': hoy,
                'dias_solicitados': 3,
                'comodato_aceptado': True,
                'estado': 'CONFIRMADA',
                'observaciones': 'Reserva de prueba lista para recepción y control en pañol.'
            }
        )
        self.stdout.write(f"  - Reserva de prueba creada: {reserva_demo.codigo}")

        self.stdout.write(self.style.SUCCESS('¡Datos y usuarios iniciales cargados exitosamente!'))

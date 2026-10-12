from django.core.management.base import BaseCommand
from reservas.models import Sede, Categoria, Herramienta, Matriculado


class Command(BaseCommand):
    help = 'Carga los datos iniciales de Sedes, Categorías, Herramientas y Matriculado para Caja de Herramientas R1'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Iniciando carga de datos iniciales...'))

        # 1. Sedes
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
            sede_obj, _ = Sede.objects.update_or_create(
                slug=s['slug'],
                defaults=s
            )
            sedes_dict[s['slug']] = sede_obj
            self.stdout.write(f"  - Sede: {sede_obj.nombre}")

        sede_principal = sedes_dict['cordoba']

        # 2. Categorías
        categorias_data = [
            {'nombre': 'Medición y topografía', 'slug': 'medicion-y-topografia', 'orden': 1},
            {'nombre': 'Instalaciones Eléctricas', 'slug': 'instalaciones-electricas', 'orden': 2},
            {'nombre': 'Instalaciones de Gas', 'slug': 'instalaciones-de-gas', 'orden': 3},
            {'nombre': 'Instalaciones varias', 'slug': 'instalaciones-varias', 'orden': 4},
        ]

        categorias_dict = {}
        for c in categorias_data:
            cat_obj, _ = Categoria.objects.update_or_create(
                slug=c['slug'],
                defaults=c
            )
            categorias_dict[c['slug']] = cat_obj
            self.stdout.write(f"  - Categoría: {cat_obj.nombre}")

        # 3. Herramientas
        herramientas_data = [
            {
                'nombre': 'Nivel Láser Multilínea',
                'slug': 'nivel-laser-multilinea',
                'categoria': categorias_dict['medicion-y-topografia'],
                'sede_predeterminada': sede_principal,
                'descripcion': 'Proyección 360° de líneas horizontales y verticales con trípode profesional regulable.',
                'imagen': 'assets/equipos/nivel-laser.png',
                'stock_total': 4,
                'stock_disponible': 4,
                'requiere_capacitacion': False,
            },
            {
                'nombre': 'Telurímetro',
                'slug': 'telurimetro',
                'categoria': categorias_dict['instalaciones-electricas'],
                'sede_predeterminada': sede_principal,
                'descripcion': 'Medición de resistencia de puesta a tierra con kit de jabalinas auxiliares y cables calibrados.',
                'imagen': 'assets/equipos/telurimetro.png',
                'stock_total': 2,
                'stock_disponible': 2,
                'requiere_capacitacion': True,
                'aviso_capacitacion': 'Requiere capacitación previa',
            },
            {
                'nombre': 'Esclerómetro',
                'slug': 'esclerometro',
                'categoria': categorias_dict['instalaciones-varias'],
                'sede_predeterminada': sede_principal,
                'descripcion': 'Ensayo no destructivo para estimación de resistencia a compresión superficial del hormigón armado.',
                'imagen': 'assets/equipos/esclerometro.png',
                'stock_total': 3,
                'stock_disponible': 3,
                'requiere_capacitacion': True,
                'aviso_capacitacion': 'Requiere capacitación previa',
            },
            {
                'nombre': 'Distanciómetro Láser',
                'slug': 'distanciometro-laser',
                'categoria': categorias_dict['medicion-y-topografia'],
                'sede_predeterminada': sede_principal,
                'descripcion': 'Medición de distancias con alcance de hasta 100 m, cálculo indirecto de Pitágoras, áreas y volúmenes.',
                'imagen': 'assets/equipos/distanciometro.png',
                'stock_total': 6,
                'stock_disponible': 6,
                'requiere_capacitacion': False,
            },
            {
                'nombre': 'Pinza Amperométrica',
                'slug': 'pinza-amperometrica',
                'categoria': categorias_dict['instalaciones-electricas'],
                'sede_predeterminada': sede_principal,
                'descripcion': 'Medición precisa de corriente CA/CC, tensión, continuidad y resistencia en tableros seccionales.',
                'imagen': 'assets/equipos/pinza-amperometrica.png',
                'stock_total': 5,
                'stock_disponible': 5,
                'requiere_capacitacion': False,
            },
            {
                'nombre': 'Detector de Fugas de Gas',
                'slug': 'detector-de-fugas-de-gas',
                'categoria': categorias_dict['instalaciones-de-gas'],
                'sede_predeterminada': sede_principal,
                'descripcion': 'Detección de gases combustibles con sonda de cuello de ganso flexible, display digital y alarma sonora.',
                'imagen': 'assets/equipos/detector-gas.png',
                'stock_total': 3,
                'stock_disponible': 3,
                'requiere_capacitacion': False,
            },
            {
                'nombre': 'Kit Manómetro Prueba Hermeticidad',
                'slug': 'kit-manometro-prueba-hermeticidad',
                'categoria': categorias_dict['instalaciones-de-gas'],
                'sede_predeterminada': sede_principal,
                'descripcion': 'Prueba de hermeticidad y detección de caídas de presión en cañerías internas de gas según normativa ENARGAS.',
                'imagen': 'assets/equipos/manometro.png',
                'stock_total': 2,
                'stock_disponible': 2,
                'requiere_capacitacion': True,
                'aviso_capacitacion': 'Requiere capacitación previa',
            },
            {
                'nombre': 'Cámara Termográfica',
                'slug': 'camara-termografica',
                'categoria': categorias_dict['instalaciones-varias'],
                'sede_predeterminada': sede_principal,
                'descripcion': 'Inspección térmica infrarroja para detección de puentes térmicos en envolventes, humedades y sobrecalentamiento.',
                'imagen': 'assets/equipos/camara-termografica.png',
                'stock_total': 1,
                'stock_disponible': 1,
                'requiere_capacitacion': False,
            },
        ]

        for h in herramientas_data:
            herramienta_obj, _ = Herramienta.objects.update_or_create(
                slug=h['slug'],
                defaults=h
            )
            self.stdout.write(f"  - Herramienta: {herramienta_obj.nombre} (Stock: {herramienta_obj.stock_disponible})")

        # 4. Matriculado demo
        matriculado, _ = Matriculado.objects.update_or_create(
            numero_matricula='M1',
            defaults={
                'nombre_completo': 'Arq. Damián Coronda',
                'estado_matricula': 'Matrícula Habilitada - M1',
                'email': 'damian.coronda@colegioarq.org.ar',
                'telefono': '+54 9 351 555-0192',
                'habilitado': True,
                'capacitaciones_aprobadas': ['telurimetro', 'esclerometro', 'manometro']
            }
        )
        self.stdout.write(f"  - Matriculado cargado: {matriculado.nombre_completo}")

        self.stdout.write(self.style.SUCCESS('¡Datos iniciales cargados exitosamente!'))

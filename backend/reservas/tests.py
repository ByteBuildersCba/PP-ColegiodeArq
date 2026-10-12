from datetime import date, timedelta
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Sede, Categoria, Herramienta, Matriculado, Reserva


class ReservasAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.sede = Sede.objects.create(
            nombre='Laprida 40 - Córdoba',
            slug='cordoba',
            direccion='Laprida 40',
            horario_atencion='Lun a Vie · 09:00 – 17:00 h'
        )
        self.categoria = Categoria.objects.create(
            nombre='Medición y topografía',
            slug='medicion-y-topografia'
        )
        self.herramienta = Herramienta.objects.create(
            nombre='Nivel Láser Multilínea',
            slug='nivel-laser',
            categoria=self.categoria,
            sede_predeterminada=self.sede,
            descripcion='Nivel profesional',
            stock_total=4,
            stock_disponible=4
        )
        self.matriculado = Matriculado.objects.create(
            nombre_completo='Arq. Damián Coronda',
            numero_matricula='M1',
            estado_matricula='Matrícula Habilitada - M1'
        )

    def test_listar_herramientas(self):
        response = self.client.get('/api/herramientas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Nivel Láser Multilínea')

    def test_crear_reserva_valida_descuenta_stock(self):
        hoy = date.today()
        f_fin = hoy + timedelta(days=2) # 3 días en total

        payload = {
            'matriculado': self.matriculado.id,
            'herramienta': self.herramienta.id,
            'sede': self.sede.id,
            'fecha_inicio': hoy.isoformat(),
            'fecha_devolucion': f_fin.isoformat(),
            'comodato_aceptado': True
        }

        response = self.client.post('/api/reservas/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['codigo'].startswith('R1-'))

        # Comprobar que el stock disponible disminuyó
        self.herramienta.refresh_from_db()
        self.assertEqual(self.herramienta.stock_disponible, 3)

    def test_error_prestamo_mas_de_3_dias(self):
        hoy = date.today()
        f_fin = hoy + timedelta(days=4) # 5 días (excede límite)

        payload = {
            'matriculado': self.matriculado.id,
            'herramienta': self.herramienta.id,
            'sede': self.sede.id,
            'fecha_inicio': hoy.isoformat(),
            'fecha_devolucion': f_fin.isoformat(),
            'comodato_aceptado': True
        }

        response = self.client.post('/api/reservas/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_devolucion', response.data)

    def test_error_limite_maximo_2_reservas_simultaneas(self):
        hoy = date.today()
        f_fin = hoy + timedelta(days=1)

        # Crear 2 reservas activas
        Reserva.objects.create(
            matriculado=self.matriculado,
            herramienta=self.herramienta,
            sede=self.sede,
            fecha_inicio=hoy,
            fecha_devolucion=f_fin,
            comodato_aceptado=True,
            estado='CONFIRMADA'
        )
        Reserva.objects.create(
            matriculado=self.matriculado,
            herramienta=self.herramienta,
            sede=self.sede,
            fecha_inicio=hoy,
            fecha_devolucion=f_fin,
            comodato_aceptado=True,
            estado='CONFIRMADA'
        )

        # Intentar tercera reserva
        payload = {
            'matriculado': self.matriculado.id,
            'herramienta': self.herramienta.id,
            'sede': self.sede.id,
            'fecha_inicio': hoy.isoformat(),
            'fecha_devolucion': f_fin.isoformat(),
            'comodato_aceptado': True
        }

        response = self.client.post('/api/reservas/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

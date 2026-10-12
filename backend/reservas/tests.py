from datetime import date, timedelta
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import (
    Sede,
    Categoria,
    Herramienta,
    StockSede,
    Matriculado,
    Reserva,
    PadronColegio,
    ControlDevolucion
)


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
        self.stock_sede = StockSede.objects.create(
            herramienta=self.herramienta,
            sede=self.sede,
            stock_total=4,
            stock_disponible=4
        )
        self.matriculado = Matriculado.objects.create(
            nombre_completo='Arq. Damián Coronda',
            numero_matricula='M1',
            estado_matricula='Matrícula Habilitada - M1'
        )
        # Padrón
        self.padron_valido = PadronColegio.objects.create(
            numero_matricula='M2045',
            nombre_titular='Arq. María Eugenia Silva',
            estado_vigencia='HABILITADA'
        )
        self.padron_suspendido = PadronColegio.objects.create(
            numero_matricula='M9999',
            nombre_titular='Arq. Roberto Morales',
            estado_vigencia='SUSPENDIDA'
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
        self.stock_sede.refresh_from_db()
        self.assertEqual(self.stock_sede.stock_disponible, 3)

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

    def test_verificar_matricula_vigente_vs_suspendida(self):
        # Matrícula vigente
        res_ok = self.client.get('/api/auth/verificar-matricula/?matricula=M2045')
        self.assertEqual(res_ok.status_code, status.HTTP_200_OK)
        self.assertTrue(res_ok.data['valida'])
        self.assertEqual(res_ok.data['nombre_titular'], 'Arq. María Eugenia Silva')

        # Matrícula suspendida
        res_susp = self.client.get('/api/auth/verificar-matricula/?matricula=M9999')
        self.assertEqual(res_susp.status_code, status.HTTP_200_OK)
        self.assertFalse(res_susp.data['valida'])

        # Matrícula inexistente
        res_none = self.client.get('/api/auth/verificar-matricula/?matricula=M0000')
        self.assertEqual(res_none.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_controlar_devolucion_herramienta(self):
        hoy = date.today()
        reserva = Reserva.objects.create(
            matriculado=self.matriculado,
            herramienta=self.herramienta,
            sede=self.sede,
            fecha_inicio=hoy - timedelta(days=2),
            fecha_devolucion=hoy,
            comodato_aceptado=True,
            estado='CONFIRMADA'
        )
        self.herramienta.stock_disponible = 3
        self.herramienta.save()
        self.stock_sede.stock_disponible = 3
        self.stock_sede.save()

        # Admin controla devolución
        payload_devolucion = {
            'estado_condicion': 'OPTIMO',
            'checklist_baterias': True,
            'checklist_accesorios': True,
            'checklist_limpieza': True,
            'checklist_maletin': True,
            'observaciones': 'Equipo entregado completo y probado.'
        }
        res = self.client.post(f'/api/reservas/{reserva.id}/controlar_devolucion/', payload_devolucion, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'DEVUELTA')
        self.assertTrue(hasattr(reserva, 'control_devolucion'))

        # Stock reintegrado
        self.herramienta.refresh_from_db()
        self.assertEqual(self.herramienta.stock_disponible, 4)
        self.stock_sede.refresh_from_db()
        self.assertEqual(self.stock_sede.stock_disponible, 4)

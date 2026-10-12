# Caja de Herramientas R1 — Colegio de Arquitectos de Córdoba (Regional 1)

Módulo web de reserva e instrumental técnico para profesionales matriculados del **Colegio de Arquitectos de la Provincia de Córdoba (Regional 1)**.

---

## 🎨 Especificaciones Visuales y Paleta de Colores

Diseñado con un estilo limpio, sobrio y moderno pensado para arquitectos, respetando la identidad institucional del CAPC:

| Elemento / Sección | Código HEX | Descripción |
| :--- | :--- | :--- |
| **Gris Claro de Sección** | `#EFEFEF` | Fondo principal de la aplicación y bloque inferior de condiciones |
| **Gris de Menú Desplegable** | `#E5E3DF` | Fondo del menú desplegable institucional de la lista "HERRAMIENTAS" |
| **Blanco Puro** | `#FFFFFF` | Fondo del Header superior, barra institucional y tarjetas |
| **Verde WhatsApp** | `#25D366` | Botón flotante de atención y soporte técnico directo |
| **Azul Institucional CAPC** | `#004B87` | Botones de acción principal (Reservar, Autogestión) y acentos |

---

## 🏗️ Arquitectura del Proyecto

El repositorio está estructurado en dos módulos desacoplados:

```
PP-ColegiodeArq/
├── backend/                  # API REST en Python / Django
│   ├── config/               # Configuración central (settings, urls, wsgi)
│   ├── reservas/             # App de lógica de negocio (modelos, serializers, vistas, tests)
│   │   ├── models.py         # Sede, Categoria, Herramienta, Matriculado, Reserva
│   │   ├── serializers.py    # Serializadores con reglas de validación y descuento de stock
│   │   ├── views.py          # ViewSets REST con filtros y cancelación
│   │   ├── tests.py          # Pruebas automatizadas de reglas de negocio
│   │   └── management/
│   │       └── commands/
│   │           └── seed_data.py # Carga de datos oficiales de sedes y herramientas
│   ├── requirements.txt      # Django 5, DRF, django-cors-headers
│   └── manage.py
│
└── frontend/                 # Aplicación Web en Angular / TypeScript / Bootstrap
    ├── src/
    │   ├── app/
    │   │   ├── components/
    │   │   │   ├── header/            # Logo, matriculado, selector de sede y horarios
    │   │   │   ├── filtros/           # Buscador reactivo y categorías
    │   │   │   ├── catalogo/          # Grilla de tarjetas de instrumental con stock
    │   │   │   ├── reserva-drawer/    # Panel lateral deslizable (fechas, comodato, cupo)
    │   │   │   ├── comodato-modal/    # Modal con texto legal del Contrato de Comodato
    │   │   │   ├── mis-reservas-modal/# Consulta y cancelación de reservas del matriculado
    │   │   │   └── whatsapp-button/   # Botón flotante verde (#25D366)
    │   │   ├── models/                # Interfaces TypeScript de dominio
    │   │   ├── services/              # HerramientasService (Signals reactivos + API + Fallback)
    │   │   ├── app.ts / app.html
    │   ├── styles.css                 # Variables globales y utilidades
    ├── public/assets/
    │   ├── logo-carq-cba.png          # Isotipo oficial CAPC
    │   └── equipos/                   # Fotografías de alta resolución del instrumental
    └── package.json                   # Angular 22, Bootstrap 5, Bootstrap Icons
```

---

## 🚀 Puesta en Marcha

### 1. Backend (Django REST Framework)

Requisitos: Python 3.10+

```bash
cd backend

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones y cargar datos de prueba oficiales
python manage.py migrate
python manage.py seed_data

# Ejecutar el servidor de desarrollo en el puerto 8000
python manage.py runserver
```

Endpoints principales:
- `http://127.0.0.1:8000/api/herramientas/`
- `http://127.0.0.1:8000/api/sedes/`
- `http://127.0.0.1:8000/api/reservas/`
- `http://127.0.0.1:8000/api/matriculados/actual/`
- `http://127.0.0.1:8000/admin/` (Panel de Administración)

Para ejecutar la suite de pruebas del backend:
```bash
python manage.py test
```

---

### 2. Frontend (Angular 22 + TypeScript + Bootstrap)

Requisitos: Node.js 18+ y npm

```bash
cd frontend

# Instalar dependencias
npm install --legacy-peer-deps

# Iniciar servidor de desarrollo
npm start
# o
npx ng serve
```

La aplicación estará disponible en: `http://localhost:4200/`

*Nota: La aplicación Angular cuenta con sincronización automática con la API de Django y fallback reactivo local transparente si se corre de forma aislada.*

---

## 📋 Reglas de Negocio Implementadas (Versión 1)

1. **Límite de tiempo:** Cada préstamo permite una duración de hasta **3 días corridos** como máximo.
2. **Cupo por profesional:** Cada matriculado puede solicitar hasta **2 herramientas simultáneas**. Al alcanzar el límite, el sistema bloquea nuevas reservas informando al usuario.
3. **Contrato de Comodato:** Checkbox de aceptación vinculante previa con acceso a la lectura de las cláusulas legales.
4. **Sedes activas y horarios dinámicos:** Al cambiar de sede (`Laprida 40 - Córdoba`, `Villa Allende`, `Jesús María`), se actualizan los horarios de atención y la dirección de retiro.
5. **Alerta de capacitación:** Herramientas con requerimiento técnico (como *Telurímetro* o *Esclerómetro*) exhiben aviso destacado de capacitación previa.

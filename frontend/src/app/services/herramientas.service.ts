import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, catchError, tap } from 'rxjs';
import { Herramienta, Categoria, Sede, Matriculado, Reserva, ReservaPayload } from '../models/herramienta.model';

@Injectable({
  providedIn: 'root'
})
export class HerramientasService {
  private readonly apiUrl = 'http://127.0.0.1:8000/api';

  // Sedes
  readonly sedes = signal<Sede[]>([
    {
      id: 1,
      nombre: 'Laprida 40 - Córdoba',
      slug: 'cordoba',
      direccion: 'Mariano Moreno / Laprida 40, B° Güemes, Córdoba Capital',
      horario_atencion: 'Lun a Vie · 09:00 – 17:00 h',
      telefono: '+54 351 468-4500',
      email: 'regional1@colegio-arquitectos.com.ar'
    },
    {
      id: 2,
      nombre: 'Villa Allende',
      slug: 'villa-allende',
      direccion: 'Av. Goycoechea 850, Villa Allende, Córdoba',
      horario_atencion: 'Mar y Jue · 10:00 – 15:00 h',
      telefono: '+54 3543 43-2100',
      email: 'villaallende@colegio-arquitectos.com.ar'
    },
    {
      id: 3,
      nombre: 'Jesús María',
      slug: 'jesus-maria',
      direccion: 'San Martín 450, Jesús María, Córdoba',
      horario_atencion: 'Mié y Vie · 09:00 – 14:00 h',
      telefono: '+54 3525 42-1500',
      email: 'jesusmaria@colegio-arquitectos.com.ar'
    }
  ]);

  readonly sedeSeleccionada = signal<Sede>(this.sedes()[0]);

  // Categorías
  readonly categorias = signal<Categoria[]>([
    { id: 1, nombre: 'Todas', slug: 'todas', orden: 0 },
    { id: 2, nombre: 'Medición y topografía', slug: 'medicion-y-topografia', orden: 1 },
    { id: 3, nombre: 'Instalaciones Eléctricas', slug: 'instalaciones-electricas', orden: 2 },
    { id: 4, nombre: 'Instalaciones de Gas', slug: 'instalaciones-de-gas', orden: 3 },
    { id: 5, nombre: 'Instalaciones varias', slug: 'instalaciones-varias', orden: 4 }
  ]);

  readonly categoriaSeleccionada = signal<string>('Todas');
  readonly terminoBusqueda = signal<string>('');

  // Usuario / Matriculado
  readonly matriculado = signal<Matriculado>({
    id: 1,
    nombre_completo: 'Arq. Damián Coronda',
    numero_matricula: 'M1',
    estado_matricula: 'Matrícula Habilitada - M1',
    email: 'damian.coronda@colegioarq.org.ar',
    telefono: '+54 9 351 555-0192',
    habilitado: true,
    reservas_activas_count: 0
  });

  // Catálogo inicial de herramientas (fallback y estado reactivo)
  readonly herramientas = signal<Herramienta[]>([
    {
      id: 1,
      nombre: 'Nivel Láser Multilínea',
      slug: 'nivel-laser-multilinea',
      categoria_nombre: 'Medición y topografía',
      categoria_slug: 'medicion-y-topografia',
      descripcion: 'Proyección 360° de líneas horizontales y verticales con trípode.',
      imagen: 'assets/equipos/nivel-laser.png',
      stock_total: 4,
      stock_disponible: 4,
      requiere_capacitacion: false,
      aviso_capacitacion: '',
      dias_max_prestamo: 3,
      activa: true
    },
    {
      id: 2,
      nombre: 'Telurímetro',
      slug: 'telurimetro',
      categoria_nombre: 'Instalaciones Eléctricas',
      categoria_slug: 'instalaciones-electricas',
      descripcion: 'Medición de resistencia de puesta a tierra con jabalinas y cables.',
      imagen: 'assets/equipos/telurimetro.png',
      stock_total: 2,
      stock_disponible: 2,
      requiere_capacitacion: true,
      aviso_capacitacion: 'Requiere capacitación previa',
      dias_max_prestamo: 3,
      activa: true
    },
    {
      id: 3,
      nombre: 'Esclerómetro',
      slug: 'esclerometro',
      categoria_nombre: 'Instalaciones varias',
      categoria_slug: 'instalaciones-varias',
      descripcion: 'Ensayo no destructivo de resistencia superficial del hormigón.',
      imagen: 'assets/equipos/esclerometro.png',
      stock_total: 3,
      stock_disponible: 3,
      requiere_capacitacion: true,
      aviso_capacitacion: 'Requiere capacitación previa',
      dias_max_prestamo: 3,
      activa: true
    },
    {
      id: 4,
      nombre: 'Distanciómetro Láser',
      slug: 'distanciometro-laser',
      categoria_nombre: 'Medición y topografía',
      categoria_slug: 'medicion-y-topografia',
      descripcion: 'Medición de distancias de hasta 100 m con cálculo de áreas.',
      imagen: 'assets/equipos/distanciometro.png',
      stock_total: 6,
      stock_disponible: 6,
      requiere_capacitacion: false,
      aviso_capacitacion: '',
      dias_max_prestamo: 3,
      activa: true
    },
    {
      id: 5,
      nombre: 'Pinza Amperométrica',
      slug: 'pinza-amperometrica',
      categoria_nombre: 'Instalaciones Eléctricas',
      categoria_slug: 'instalaciones-electricas',
      descripcion: 'Medición de corriente, tensión y continuidad en tableros.',
      imagen: 'assets/equipos/pinza-amperometrica.png',
      stock_total: 5,
      stock_disponible: 5,
      requiere_capacitacion: false,
      aviso_capacitacion: '',
      dias_max_prestamo: 3,
      activa: true
    },
    {
      id: 6,
      nombre: 'Detector de Fugas de Gas',
      slug: 'detector-de-fugas-de-gas',
      categoria_nombre: 'Instalaciones de Gas',
      categoria_slug: 'instalaciones-de-gas',
      descripcion: 'Detección de gases combustibles con sonda flexible y alarma.',
      imagen: 'assets/equipos/detector-gas.png',
      stock_total: 3,
      stock_disponible: 3,
      requiere_capacitacion: false,
      aviso_capacitacion: '',
      dias_max_prestamo: 3,
      activa: true
    },
    {
      id: 7,
      nombre: 'Kit Manómetro Prueba Hermeticidad',
      slug: 'kit-manometro-prueba-hermeticidad',
      categoria_nombre: 'Instalaciones de Gas',
      categoria_slug: 'instalaciones-de-gas',
      descripcion: 'Prueba de hermeticidad en cañerías de gas según normativa.',
      imagen: 'assets/equipos/manometro.png',
      stock_total: 2,
      stock_disponible: 2,
      requiere_capacitacion: true,
      aviso_capacitacion: 'Requiere capacitación previa',
      dias_max_prestamo: 3,
      activa: true
    },
    {
      id: 8,
      nombre: 'Cámara Termográfica',
      slug: 'camara-termografica',
      categoria_nombre: 'Instalaciones varias',
      categoria_slug: 'instalaciones-varias',
      descripcion: 'Detección de puentes térmicos, humedades y fallas eléctricas.',
      imagen: 'assets/equipos/camara-termografica.png',
      stock_total: 1,
      stock_disponible: 1,
      requiere_capacitacion: false,
      aviso_capacitacion: '',
      dias_max_prestamo: 3,
      activa: true
    }
  ]);

  // Lista de reservas activas del usuario
  readonly reservas = signal<Reserva[]>([]);

  // Computed: cantidad de reservas activas
  readonly reservasActivasCount = computed(() => {
    return this.reservas().filter(r => r.estado === 'CONFIRMADA' || r.estado === 'RETIRADA').length;
  });

  // Computed: límite máximo alcanzado (máx 2 equipos)
  readonly puedeReservar = computed(() => {
    return this.reservasActivasCount() < 2;
  });

  // Computed: herramientas filtradas según búsqueda y categoría
  readonly herramientasFiltradas = computed(() => {
    const cat = this.categoriaSeleccionada();
    const query = this.terminoBusqueda().toLowerCase().trim();

    return this.herramientas().filter(h => {
      const matchCat = (cat === 'Todas' || h.categoria_nombre.toLowerCase() === cat.toLowerCase());
      const matchQuery = !query ||
        h.nombre.toLowerCase().includes(query) ||
        h.descripcion.toLowerCase().includes(query) ||
        h.categoria_nombre.toLowerCase().includes(query);
      return matchCat && matchQuery;
    });
  });

  constructor(private http: HttpClient) {
    this.cargarDatosDesdeBackend();
  }

  cargarDatosDesdeBackend(): void {
    // Intentar sincronizar herramientas con el backend Django
    this.http.get<Herramienta[]>(`${this.apiUrl}/herramientas/`).pipe(
      catchError(() => of(null))
    ).subscribe(data => {
      if (data && data.length > 0) {
        this.herramientas.set(data);
      }
    });

    // Intentar sincronizar sedes
    this.http.get<Sede[]>(`${this.apiUrl}/sedes/`).pipe(
      catchError(() => of(null))
    ).subscribe(data => {
      if (data && data.length > 0) {
        this.sedes.set(data);
        this.sedeSeleccionada.set(data[0]);
      }
    });

    // Intentar sincronizar matriculado
    this.http.get<Matriculado>(`${this.apiUrl}/matriculados/actual/`).pipe(
      catchError(() => of(null))
    ).subscribe(data => {
      if (data) {
        this.matriculado.set(data);
      }
    });
  }

  setSede(sede: Sede): void {
    this.sedeSeleccionada.set(sede);
  }

  setCategoria(cat: string): void {
    this.categoriaSeleccionada.set(cat);
  }

  setBusqueda(query: string): void {
    this.terminoBusqueda.set(query);
  }

  confirmarReserva(
    herramienta: Herramienta,
    fechaInicio: string,
    fechaDevolucion: string,
    comodatoAceptado: boolean
  ): Observable<Reserva> {
    if (this.reservasActivasCount() >= 2) {
      throw new Error('Has alcanzado el límite máximo permitido de 2 equipos reservados en simultáneo.');
    }

    if (!comodatoAceptado) {
      throw new Error('Debes aceptar los términos del Contrato de Comodato.');
    }

    if (herramienta.stock_disponible <= 0) {
      throw new Error('No hay stock disponible de este equipo.');
    }

    const sedeActual = this.sedeSeleccionada();
    const matriculadoActual = this.matriculado();

    // Calcular días
    const f1 = new Date(fechaInicio);
    const f2 = new Date(fechaDevolucion);
    const diffDays = Math.round((f2.getTime() - f1.getTime()) / (1000 * 3600 * 24)) + 1;

    if (diffDays > 3) {
      throw new Error('El préstamo de herramientas no puede exceder el límite de 3 días.');
    }

    const payload: ReservaPayload = {
      matriculado: matriculadoActual.id,
      herramienta: herramienta.id,
      sede: sedeActual.id,
      fecha_inicio: fechaInicio,
      fecha_devolucion: fechaDevolucion,
      comodato_aceptado: comodatoAceptado
    };

    const codigoGenerado = `R1-${new Date().getFullYear().toString().slice(-2)}${Math.floor(1000 + Math.random() * 9000)}`;

    const nuevaReserva: Reserva = {
      id: Date.now(),
      codigo: codigoGenerado,
      herramienta: { ...herramienta },
      sede: { ...sedeActual },
      matriculado: { ...matriculadoActual },
      fecha_inicio: fechaInicio,
      fecha_devolucion: fechaDevolucion,
      dias_solicitados: Math.max(1, diffDays),
      comodato_aceptado: true,
      estado: 'CONFIRMADA',
      fecha_creacion: new Date().toISOString()
    };

    // Intentar enviar al backend Django si está disponible
    return new Observable<Reserva>(observer => {
      this.http.post<any>(`${this.apiUrl}/reservas/`, payload).pipe(
        catchError(() => of(null))
      ).subscribe(backendReserva => {
        if (backendReserva && backendReserva.codigo) {
          nuevaReserva.codigo = backendReserva.codigo;
          nuevaReserva.id = backendReserva.id;
        }

        // Descontar stock local reactivo
        this.herramientas.update(items =>
          items.map(item =>
            item.id === herramienta.id
              ? { ...item, stock_disponible: Math.max(0, item.stock_disponible - 1) }
              : item
          )
        );

        // Agregar reserva a la lista activa
        this.reservas.update(res => [nuevaReserva, ...res]);

        observer.next(nuevaReserva);
        observer.complete();
      });
    });
  }

  cancelarReserva(reserva: Reserva): void {
    // Restaurar stock
    this.herramientas.update(items =>
      items.map(item =>
        item.id === reserva.herramienta.id
          ? { ...item, stock_disponible: Math.min(item.stock_total, item.stock_disponible + 1) }
          : item
      )
    );

    // Actualizar estado de la reserva
    this.reservas.update(items =>
      items.map(r => r.codigo === reserva.codigo ? { ...r, estado: 'CANCELADA' } : r)
    );

    // Intentar notificar al backend
    if (reserva.id) {
      this.http.post(`${this.apiUrl}/reservas/${reserva.id}/cancelar/`, {}).pipe(
        catchError(() => of(null))
      ).subscribe();
    }
  }
}

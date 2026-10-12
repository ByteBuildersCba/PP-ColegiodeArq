export interface Sede {
  id: number;
  nombre: string;
  slug: string;
  direccion: string;
  horario_atencion: string;
  telefono: string;
  email: string;
}

export interface Categoria {
  id: number;
  nombre: string;
  slug: string;
  orden?: number;
}

export interface StockSede {
  id: number;
  herramienta: number;
  herramienta_nombre: string;
  herramienta_imagen: string;
  sede: number;
  sede_nombre: string;
  stock_total: number;
  stock_disponible: number;
}

export interface Herramienta {
  id: number;
  nombre: string;
  slug: string;
  categoria?: number;
  categoria_nombre: string;
  categoria_slug: string;
  sede_nombre?: string;
  descripcion: string;
  especificaciones?: string;
  imagen: string;
  stock_total: number;
  stock_disponible: number;
  stock_sedes?: StockSede[];
  requiere_capacitacion: boolean;
  aviso_capacitacion: string;
  dias_max_prestamo: number;
  activa: boolean;
}

export interface Matriculado {
  id: number;
  nombre_completo: string;
  numero_matricula: string;
  estado_matricula: string;
  email: string;
  telefono: string;
  habilitado: boolean;
  capacitaciones_aprobadas?: string[];
  reservas_activas_count: number;
}

export interface Usuario {
  id: number;
  username: string;
  email: string;
  nombre: string;
  matricula: string;
  estado_matricula: string;
  rol: 'ARQUITECTO' | 'ADMIN_PANOL';
  sede_asignada?: number;
}

export interface ControlDevolucion {
  id?: number;
  reserva?: number;
  fecha_inspeccion?: string;
  estado_condicion: 'OPTIMO' | 'BUENO' | 'CON_DANO' | 'INCOMPLETO';
  checklist_baterias: boolean;
  checklist_accesorios: boolean;
  checklist_limpieza: boolean;
  checklist_maletin: boolean;
  observaciones?: string;
}

export interface Reserva {
  id?: number;
  codigo: string;
  matriculado_id?: number;
  matriculado?: Matriculado;
  herramienta: Herramienta;
  sede: Sede;
  fecha_inicio: string;
  fecha_devolucion: string;
  dias_solicitados: number;
  comodato_aceptado: boolean;
  estado: 'CONFIRMADA' | 'RETIRADA' | 'DEVUELTA' | 'CANCELADA';
  fecha_creacion: string;
  observaciones?: string;
  control_devolucion?: ControlDevolucion;
}

export interface ReservaPayload {
  matriculado: number;
  herramienta: number;
  sede: number;
  fecha_inicio: string;
  fecha_devolucion: string;
  comodato_aceptado: boolean;
}

export interface VerificacionMatriculaRespuesta {
  valida: boolean;
  numero_matricula?: string;
  nombre_titular?: string;
  estado_vigencia?: string;
  vigente_hasta?: string;
  mensaje: string;
}

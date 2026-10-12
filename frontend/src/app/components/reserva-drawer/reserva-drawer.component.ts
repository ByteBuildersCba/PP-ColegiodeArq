import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HerramientasService } from '../../services/herramientas.service';
import { Herramienta, Reserva } from '../../models/herramienta.model';

@Component({
  selector: 'app-reserva-drawer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reserva-drawer.component.html',
  styleUrls: ['./reserva-drawer.component.css']
})
export class ReservaDrawerComponent implements OnChanges {
  @Input() visible = false;
  @Input() herramienta: Herramienta | null = null;
  @Output() cerrar = new EventEmitter<void>();
  @Output() verComodato = new EventEmitter<void>();
  @Output() reservaConfirmada = new EventEmitter<Reserva>();

  fechaInicio = '';
  fechaDevolucion = '';
  comodatoAceptado = false;
  errorMensaje = '';
  cargando = false;

  // Estado posterior a la confirmación exitosa
  reservaExitosa: Reserva | null = null;

  constructor(public herramientasService: HerramientasService) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['visible'] && this.visible) {
      this.resetFormulario();
    }
  }

  resetFormulario(): void {
    this.reservaExitosa = null;
    this.errorMensaje = '';
    this.comodatoAceptado = false;

    // Sugerir fecha de inicio para mañana o siguiente día hábil
    const hoy = new Date();
    const manana = new Date(hoy);
    manana.setDate(hoy.getDate() + 1);

    // Formato YYYY-MM-DD
    this.fechaInicio = this.formatDate(manana);

    // Fecha devolución sugerida: 2 días después (dentro de los 3 días máx)
    const devolucion = new Date(manana);
    devolucion.setDate(manana.getDate() + 2);
    this.fechaDevolucion = this.formatDate(devolucion);
  }

  get minFechaInicio(): string {
    const hoy = new Date();
    return this.formatDate(hoy);
  }

  get minFechaDevolucion(): string {
    return this.fechaInicio || this.minFechaInicio;
  }

  get maxFechaDevolucion(): string {
    if (!this.fechaInicio) return '';
    const f = new Date(this.fechaInicio);
    f.setDate(f.getDate() + 2); // Hasta 3 días contando el de inicio
    return this.formatDate(f);
  }

  get diasCalculados(): number {
    if (!this.fechaInicio || !this.fechaDevolucion) return 0;
    const f1 = new Date(this.fechaInicio);
    const f2 = new Date(this.fechaDevolucion);
    const diff = Math.round((f2.getTime() - f1.getTime()) / (1000 * 3600 * 24)) + 1;
    return Math.max(0, diff);
  }

  get diasExcedidos(): boolean {
    return this.diasCalculados > 3;
  }

  onFechaInicioChange(): void {
    if (this.fechaInicio) {
      const f1 = new Date(this.fechaInicio);
      const f2 = new Date(f1);
      f2.setDate(f1.getDate() + 2); // 3 días en total
      this.fechaDevolucion = this.formatDate(f2);
    }
  }

  confirmar(): void {
    if (!this.herramienta) return;
    this.errorMensaje = '';

    if (!this.comodatoAceptado) {
      this.errorMensaje = 'Debes aceptar los términos del Contrato de Comodato para continuar.';
      return;
    }

    if (this.diasCalculados <= 0) {
      this.errorMensaje = 'La fecha de devolución debe ser igual o posterior a la fecha de inicio.';
      return;
    }

    if (this.diasCalculados > 3) {
      this.errorMensaje = `El plazo máximo de préstamo es de 3 días (solicitado: ${this.diasCalculados} días).`;
      return;
    }

    if (this.herramientasService.reservasActivasCount() >= 2) {
      this.errorMensaje = 'Has alcanzado el límite de 2 equipos reservados en simultáneo.';
      return;
    }

    this.cargando = true;

    try {
      this.herramientasService.confirmarReserva(
        this.herramienta,
        this.fechaInicio,
        this.fechaDevolucion,
        this.comodatoAceptado
      ).subscribe({
        next: (reserva) => {
          this.cargando = false;
          this.reservaExitosa = reserva;
          this.reservaConfirmada.emit(reserva);
        },
        error: (err) => {
          this.cargando = false;
          this.errorMensaje = err?.message || 'Error al procesar la reserva.';
        }
      });
    } catch (err: any) {
      this.cargando = false;
      this.errorMensaje = err?.message || 'Error al procesar la reserva.';
    }
  }

  onCerrar(): void {
    this.cerrar.emit();
  }

  private formatDate(d: Date): string {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
}

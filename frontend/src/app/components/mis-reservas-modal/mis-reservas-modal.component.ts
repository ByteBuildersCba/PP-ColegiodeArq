import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HerramientasService } from '../../services/herramientas.service';
import { Reserva } from '../../models/herramienta.model';

@Component({
  selector: 'app-mis-reservas-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (visible) {
      <div class="modal-backdrop fade show" (click)="cerrar.emit()"></div>
      <div class="modal fade show d-block" tabindex="-1" role="dialog" aria-labelledby="misReservasTitle" aria-modal="true">
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
          <div class="modal-content border-0 shadow-lg">
            <div class="modal-header bg-light">
              <div>
                <h5 class="modal-title fw-bold text-dark d-flex align-items-center gap-2" id="misReservasTitle">
                  <i class="bi bi-clock-history text-primary"></i>
                  Mis Solicitudes de Préstamo
                </h5>
                <span class="text-muted small">
                  {{ herramientasService.matriculado().nombre_completo }} — Matrícula: {{ herramientasService.matriculado().numero_matricula }}
                </span>
              </div>
              <button type="button" class="btn-close" (click)="cerrar.emit()" aria-label="Cerrar"></button>
            </div>
            <div class="modal-body p-4">
              <!-- Cuota de reservas -->
              <div class="d-flex align-items-center justify-content-between p-3 rounded-3 bg-light border mb-4">
                <div>
                  <span class="fw-bold text-dark d-block">Cupo de Préstamos Simultáneos</span>
                  <span class="text-muted small">Límite reglamentario: 2 equipos activos</span>
                </div>
                <div class="text-end">
                  <span class="fs-4 fw-bold text-primary">{{ herramientasService.reservasActivasCount() }}</span>
                  <span class="text-muted fs-6"> / 2</span>
                </div>
              </div>

              @if (herramientasService.reservas().length === 0) {
                <div class="text-center py-4 text-muted">
                  <i class="bi bi-inbox fs-1 d-block mb-2 text-secondary"></i>
                  <p class="m-0">No tienes reservas activas registradas en esta sesión.</p>
                  <small>Selecciona un equipo del catálogo para iniciar un préstamo.</small>
                </div>
              } @else {
                <div class="d-flex flex-column gap-3">
                  @for (reserva of herramientasService.reservas(); track reserva.codigo) {
                    <div class="card border p-3" [class.border-success-subtle]="reserva.estado === 'CONFIRMADA'">
                      <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-start gap-2 mb-2">
                        <div>
                          <span class="badge bg-primary font-monospace me-2">{{ reserva.codigo }}</span>
                          <span class="badge" [ngClass]="{
                            'bg-success': reserva.estado === 'CONFIRMADA',
                            'bg-info': reserva.estado === 'RETIRADA',
                            'bg-secondary': reserva.estado === 'DEVUELTA',
                            'bg-danger': reserva.estado === 'CANCELADA'
                          }">
                            {{ reserva.estado }}
                          </span>
                          <h6 class="fw-bold text-dark mt-2 mb-0">{{ reserva.herramienta.nombre }}</h6>
                        </div>
                        @if (reserva.estado === 'CONFIRMADA') {
                          <button
                            type="button"
                            class="btn btn-outline-danger btn-sm align-self-sm-start"
                            (click)="cancelar(reserva)">
                            <i class="bi bi-x-circle me-1"></i> Cancelar Reserva
                          </button>
                        }
                      </div>

                      <div class="row g-2 text-xs text-secondary mt-1 pt-2 border-top">
                        <div class="col-sm-4">
                          <strong>Sede de retiro:</strong><br>{{ reserva.sede.nombre }}
                        </div>
                        <div class="col-sm-4">
                          <strong>Período:</strong><br>{{ reserva.fecha_inicio }} al {{ reserva.fecha_devolucion }} ({{ reserva.dias_solicitados }} días)
                        </div>
                        <div class="col-sm-4">
                          <strong>Horario atención:</strong><br>{{ reserva.sede.horario_atencion }}
                        </div>
                      </div>
                    </div>
                  }
                </div>
              }
            </div>
            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary btn-sm" (click)="cerrar.emit()">Cerrar</button>
            </div>
          </div>
        </div>
      </div>
    }
  `
})
export class MisReservasModalComponent {
  @Input() visible = false;
  @Output() cerrar = new EventEmitter<void>();

  constructor(public herramientasService: HerramientasService) {}

  cancelar(reserva: Reserva): void {
    if (confirm(`¿Estás seguro de cancelar la reserva ${reserva.codigo} de "${reserva.herramienta.nombre}"?`)) {
      this.herramientasService.cancelarReserva(reserva);
    }
  }
}

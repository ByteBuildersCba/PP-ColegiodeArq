import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HerramientasService } from '../../services/herramientas.service';
import { AuthService } from '../../services/auth.service';
import { Reserva, StockSede, ControlDevolucion } from '../../models/herramienta.model';

@Component({
  selector: 'app-admin-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="admin-panel-container bg-white rounded-3 shadow-sm border p-4 mb-5">
      
      <!-- Encabezado del Panel de Administración -->
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 pb-3 mb-4 border-bottom">
        <div>
          <span class="badge bg-dark text-uppercase font-monospace text-xs mb-1">
            <i class="bi bi-shield-lock-fill text-warning me-1"></i> Modo Administración de Pañol
          </span>
          <h2 class="fs-4 fw-bold text-dark m-0">Gestión de Sedes, Stock y Devoluciones</h2>
          <p class="text-secondary small m-0">Control centralizado para Córdoba (Laprida 40), Villa Allende y Jesús María</p>
        </div>

        <!-- Pestañas de Navegación del Admin -->
        <ul class="nav nav-pills admin-nav-tabs">
          <li class="nav-item">
            <button
              type="button"
              class="nav-link"
              [class.active]="tabActiva === 'devoluciones'"
              (click)="tabActiva = 'devoluciones'">
              <i class="bi bi-clipboard-check-fill me-1"></i> Control de Devoluciones
              <span class="badge bg-danger ms-1" *ngIf="reservasPendientes.length > 0">{{ reservasPendientes.length }}</span>
            </button>
          </li>
          <li class="nav-item">
            <button
              type="button"
              class="nav-link"
              [class.active]="tabActiva === 'stock'"
              (click)="tabActiva = 'stock'">
              <i class="bi bi-boxes me-1"></i> Stock en 3 Sedes
            </button>
          </li>
        </ul>
      </div>

      <!-- SECCIÓN 1: CONTROL DE DEVOLUCIONES DE HERRAMIENTAS -->
      @if (tabActiva === 'devoluciones') {
        <section>
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h3 class="fs-6 fw-bold text-dark m-0 text-uppercase tracking-wide">
              Préstamos Activos y Devolución de Instrumental
            </h3>
            <span class="text-muted small">
              {{ herramientasService.reservas().length }} solicitudes registradas en el sistema
            </span>
          </div>

          <div class="table-responsive">
            <table class="table table-hover align-middle table-admin">
              <thead class="table-light">
                <tr>
                  <th scope="col">Código</th>
                  <th scope="col">Equipo Solicitado</th>
                  <th scope="col">Matriculado</th>
                  <th scope="col">Sede Retiro</th>
                  <th scope="col">Período Préstamo</th>
                  <th scope="col">Estado</th>
                  <th scope="col" class="text-end">Acción de Pañol</th>
                </tr>
              </thead>
              <tbody>
                @for (reserva of herramientasService.reservas(); track reserva.codigo) {
                  <tr>
                    <td>
                      <span class="badge bg-secondary-subtle text-secondary-emphasis font-monospace fw-bold">
                        {{ reserva.codigo }}
                      </span>
                    </td>
                    <td>
                      <div class="d-flex align-items-center gap-2">
                        <img
                          [src]="reserva.herramienta.imagen"
                          [alt]="reserva.herramienta.nombre"
                          class="rounded-1 object-fit-cover admin-thumb-tool"
                          (error)="reserva.herramienta.imagen = 'assets/equipos/default.png'"
                        />
                        <span class="fw-semibold text-dark small">{{ reserva.herramienta.nombre }}</span>
                      </div>
                    </td>
                    <td>
                      <div class="small">
                        <span class="fw-semibold text-dark d-block">
                          {{ reserva.matriculado?.nombre_completo || 'Arq. Matriculado' }}
                        </span>
                        <span class="text-muted text-xs">
                          {{ reserva.matriculado?.numero_matricula || 'M1' }}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span class="badge bg-light text-dark border small">{{ reserva.sede.nombre }}</span>
                    </td>
                    <td>
                      <span class="small text-secondary">
                        {{ reserva.fecha_inicio }} al {{ reserva.fecha_devolucion }}
                      </span>
                    </td>
                    <td>
                      <span class="badge" [ngClass]="{
                        'bg-warning-subtle text-warning-emphasis': reserva.estado === 'CONFIRMADA',
                        'bg-info-subtle text-info-emphasis': reserva.estado === 'RETIRADA',
                        'bg-success-subtle text-success-emphasis': reserva.estado === 'DEVUELTA',
                        'bg-danger-subtle text-danger-emphasis': reserva.estado === 'CANCELADA'
                      }">
                        {{ reserva.estado }}
                      </span>
                    </td>
                    <td class="text-end">
                      @if (reserva.estado === 'CONFIRMADA' || reserva.estado === 'RETIRADA') {
                        <button
                          type="button"
                          class="btn btn-sm btn-capc-primary py-1 px-2.5"
                          (click)="abrirModalControl(reserva)">
                          <i class="bi bi-check2-circle me-1"></i> Controlar Devolución
                        </button>
                      } @else if (reserva.estado === 'DEVUELTA') {
                        <span class="text-success small fw-semibold">
                          <i class="bi bi-patch-check-fill me-1"></i> Recibida OK
                        </span>
                      } @else {
                        <span class="text-muted small">Cancelada</span>
                      }
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="7" class="text-center py-4 text-muted small">
                      No hay solicitudes registradas para inspección.
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </section>
      }

      <!-- SECCIÓN 2: CONTROL DE STOCK EN LAS 3 SEDES -->
      @if (tabActiva === 'stock') {
        <section>
          <!-- Selector de Sede para Control de Stock -->
          <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-3 p-3 rounded-3 bg-light border mb-4 sede-toolbar">
            <div class="d-flex align-items-center gap-2">
              <i class="bi bi-geo-alt-fill text-primary fs-5"></i>
              <span class="fw-bold text-dark text-uppercase small">Sede a Supervisar:</span>
              <div class="btn-group" role="group">
                @for (s of herramientasService.sedes(); track s.id) {
                  <button
                    type="button"
                    class="btn btn-sm"
                    [class.btn-primary]="sedeFiltroStock === s.id"
                    [class.btn-outline-secondary]="sedeFiltroStock !== s.id"
                    (click)="sedeFiltroStock = s.id">
                    {{ s.nombre }}
                  </button>
                }
              </div>
            </div>

            <div class="text-muted small">
              Sede activa: <strong>{{ getSedeNombre(sedeFiltroStock) }}</strong>
            </div>
          </div>

          <!-- Tabla de Stock por Herramienta en la Sede Seleccionada -->
          <div class="table-responsive">
            <table class="table table-hover align-middle table-admin">
              <thead class="table-light">
                <tr>
                  <th scope="col">Equipo</th>
                  <th scope="col">Sede</th>
                  <th scope="col" class="text-center">Stock Disponible</th>
                  <th scope="col" class="text-center">Stock Total</th>
                  <th scope="col">Estado</th>
                  <th scope="col" class="text-end">Ajuste de Stock</th>
                </tr>
              </thead>
              <tbody>
                @for (stock of stockFiltrado; track stock.id) {
                  <tr>
                    <td>
                      <div class="d-flex align-items-center gap-3">
                        <img
                          [src]="stock.herramienta_imagen"
                          [alt]="stock.herramienta_nombre"
                          class="rounded-1 object-fit-cover admin-thumb-tool"
                          (error)="stock.herramienta_imagen = 'assets/equipos/default.png'"
                        />
                        <span class="fw-bold text-dark small">{{ stock.herramienta_nombre }}</span>
                      </div>
                    </td>
                    <td>
                      <span class="badge bg-light text-dark border">{{ stock.sede_nombre }}</span>
                    </td>
                    <td class="text-center">
                      <span class="fs-6 fw-bold" [class.text-danger]="stock.stock_disponible === 0" [class.text-success]="stock.stock_disponible > 0">
                        {{ stock.stock_disponible }}
                      </span>
                    </td>
                    <td class="text-center text-secondary small fw-semibold">
                      {{ stock.stock_total }}
                    </td>
                    <td>
                      @if (stock.stock_disponible === 0) {
                        <span class="badge bg-danger">Agotado en sede</span>
                      } @else if (stock.stock_disponible <= 1) {
                        <span class="badge bg-warning text-dark">Stock Crítico</span>
                      } @else {
                        <span class="badge bg-success-subtle text-success-emphasis">Operativo</span>
                      }
                    </td>
                    <td class="text-end">
                      <div class="btn-group btn-group-sm">
                        <button
                          type="button"
                          class="btn btn-outline-danger"
                          title="Restar una unidad disponible"
                          [disabled]="stock.stock_disponible <= 0"
                          (click)="ajustarStock(stock, -1)">
                          <i class="bi bi-dash"></i>
                        </button>
                        <button
                          type="button"
                          class="btn btn-outline-success"
                          title="Sumar una unidad disponible"
                          [disabled]="stock.stock_disponible >= stock.stock_total"
                          (click)="ajustarStock(stock, 1)">
                          <i class="bi bi-plus"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </section>
      }

    </div>

    <!-- MODAL DE INSPECCIÓN TÉCNICA DE DEVOLUCIÓN -->
    @if (modalControlVisible && reservaAControlar) {
      <div class="modal-backdrop fade show" (click)="cerrarModalControl()"></div>
      <div class="modal fade show d-block" tabindex="-1" role="dialog" aria-modal="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow-lg">
            
            <div class="modal-header bg-light border-bottom">
              <div>
                <h5 class="modal-title fw-bold text-dark d-flex align-items-center gap-2 m-0">
                  <i class="bi bi-clipboard2-check-fill text-primary"></i>
                  Control y Recepción de Instrumental
                </h5>
                <span class="text-muted small">Reserva: {{ reservaAControlar.codigo }}</span>
              </div>
              <button type="button" class="btn-close" (click)="cerrarModalControl()" aria-label="Cerrar"></button>
            </div>

            <div class="modal-body p-4">
              <!-- Datos del equipo y matriculado -->
              <div class="card p-3 bg-light border mb-3">
                <div class="d-flex justify-content-between mb-1">
                  <span class="text-xs text-muted">EQUIPO</span>
                  <span class="text-xs text-muted">SEDE</span>
                </div>
                <div class="d-flex justify-content-between">
                  <strong class="text-dark">{{ reservaAControlar.herramienta.nombre }}</strong>
                  <span class="badge bg-secondary">{{ reservaAControlar.sede.nombre }}</span>
                </div>
                <div class="text-xs text-secondary mt-1">
                  Prestado a: {{ reservaAControlar.matriculado?.nombre_completo || 'Arq. Damián Coronda' }}
                </div>
              </div>

              <!-- Selector de Condición General -->
              <div class="mb-3">
                <label class="form-label small fw-bold text-dark">Estado General del Equipo al Devolver:</label>
                <select class="form-select form-select-sm" [(ngModel)]="controlData.estado_condicion">
                  <option value="OPTIMO">Óptimo estado (sin observaciones)</option>
                  <option value="BUENO">Buen estado (desgaste normal de obra)</option>
                  <option value="CON_DANO">Con daño técnico / rotura (requiere service)</option>
                  <option value="INCOMPLETO">Incompleto / faltante de piezas o maletín</option>
                </select>
              </div>

              <!-- Checklist Técnico de Pañol -->
              <div class="mb-3 p-3 rounded-2 border bg-white">
                <span class="d-block small fw-bold text-dark mb-2">Checklist de Verificación en Mostrador:</span>
                
                <div class="form-check mb-1.5">
                  <input class="form-check-input" type="checkbox" id="chk-baterias" [(ngModel)]="controlData.checklist_baterias">
                  <label class="form-check-label text-dark small" for="chk-baterias">
                    Baterías, cargador y cables de conexión completos y sanos
                  </label>
                </div>

                <div class="form-check mb-1.5">
                  <input class="form-check-input" type="checkbox" id="chk-accesorios" [(ngModel)]="controlData.checklist_accesorios">
                  <label class="form-check-label text-dark small" for="chk-accesorios">
                    Accesorios, sondas, jabalinas y manuales de uso incluidos
                  </label>
                </div>

                <div class="form-check mb-1.5">
                  <input class="form-check-input" type="checkbox" id="chk-limpieza" [(ngModel)]="controlData.checklist_limpieza">
                  <label class="form-check-label text-dark small" for="chk-limpieza">
                    Limpieza general adecuada (libre de mezcla, polvo o barro)
                  </label>
                </div>

                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="chk-maletin" [(ngModel)]="controlData.checklist_maletin">
                  <label class="form-check-label text-dark small" for="chk-maletin">
                    Valija / maletín rígido con trabas de seguridad en condiciones
                  </label>
                </div>
              </div>

              <!-- Observaciones adicionales -->
              <div class="mb-3">
                <label class="form-label small fw-bold text-dark">Observaciones del Inspector de Pañol:</label>
                <textarea
                  class="form-control form-control-sm"
                  rows="2"
                  placeholder="Detalles sobre el estado, calibración o faltantes (opcional)"
                  [(ngModel)]="controlData.observaciones">
                </textarea>
              </div>

              <div class="alert alert-info py-2 px-3 text-xs mb-0">
                <i class="bi bi-info-circle-fill me-1"></i>
                Al confirmar la devolución en estado <strong>Óptimo</strong> o <strong>Bueno</strong>, la unidad se reintegrará automáticamente al stock disponible de la sede {{ reservaAControlar.sede.nombre }}.
              </div>

            </div>

            <div class="modal-footer bg-light border-top">
              <button type="button" class="btn btn-secondary btn-sm" (click)="cerrarModalControl()">Cancelar</button>
              <button
                type="button"
                class="btn btn-capc-primary btn-sm fw-bold"
                (click)="confirmarDevolucion()">
                <i class="bi bi-check2-circle me-1"></i> Confirmar y Reintegrar Stock
              </button>
            </div>

          </div>
        </div>
      </div>
    }
  `,
  styles: [`
    .admin-panel-container {
      border-color: #e5e3df !important;
    }
    .admin-nav-tabs .nav-link {
      font-size: 0.82rem;
      font-weight: 700;
      color: #475569;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      margin-left: 0.35rem;
    }
    .admin-nav-tabs .nav-link.active {
      background-color: #004b87;
      color: #ffffff;
      border-color: #004b87;
    }
    .admin-thumb-tool {
      width: 36px;
      height: 36px;
    }
    .table-admin th {
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .text-xs {
      font-size: 0.72rem;
    }
  `]
})
export class AdminPanelComponent {
  tabActiva: 'devoluciones' | 'stock' = 'devoluciones';
  sedeFiltroStock = 1; // 1: Laprida 40 - Córdoba

  modalControlVisible = false;
  reservaAControlar: Reserva | null = null;

  controlData: ControlDevolucion = {
    estado_condicion: 'OPTIMO',
    checklist_baterias: true,
    checklist_accesorios: true,
    checklist_limpieza: true,
    checklist_maletin: true,
    observaciones: ''
  };

  constructor(
    public herramientasService: HerramientasService,
    public authService: AuthService
  ) {}

  get reservasPendientes(): Reserva[] {
    return this.herramientasService.reservas().filter(r => r.estado === 'CONFIRMADA' || r.estado === 'RETIRADA');
  }

  get stockFiltrado(): StockSede[] {
    return this.herramientasService.stockSedes().filter(s => s.sede === this.sedeFiltroStock);
  }

  getSedeNombre(id: number): string {
    const s = this.herramientasService.sedes().find(x => x.id === id);
    return s ? s.nombre : '';
  }

  abrirModalControl(reserva: Reserva): void {
    this.reservaAControlar = reserva;
    this.controlData = {
      estado_condicion: 'OPTIMO',
      checklist_baterias: true,
      checklist_accesorios: true,
      checklist_limpieza: true,
      checklist_maletin: true,
      observaciones: ''
    };
    this.modalControlVisible = true;
  }

  cerrarModalControl(): void {
    this.modalControlVisible = false;
    this.reservaAControlar = null;
  }

  confirmarDevolucion(): void {
    if (!this.reservaAControlar) return;

    this.herramientasService.controlarDevolucion(this.reservaAControlar, this.controlData).subscribe(() => {
      this.cerrarModalControl();
    });
  }

  ajustarStock(stock: StockSede, delta: number): void {
    const nuevoDisp = Math.max(0, Math.min(stock.stock_total, stock.stock_disponible + delta));
    this.herramientasService.ajustarStockSede(stock.id, stock.stock_total, nuevoDisp);
  }
}

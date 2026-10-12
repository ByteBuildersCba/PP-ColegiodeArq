import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-comodato-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (visible) {
      <div class="modal-backdrop fade show" (click)="cerrar.emit()"></div>
      <div class="modal fade show d-block" tabindex="-1" role="dialog" aria-labelledby="comodatoTitle" aria-modal="true">
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
          <div class="modal-content border-0 shadow-lg">
            <div class="modal-header bg-light">
              <h5 class="modal-title fw-bold text-dark d-flex align-items-center gap-2" id="comodatoTitle">
                <i class="bi bi-file-earmark-ruled text-primary"></i>
                Contrato de Comodato de Instrumental Técnico
              </h5>
              <button type="button" class="btn-close" (click)="cerrar.emit()" aria-label="Cerrar"></button>
            </div>
            <div class="modal-body p-4 text-secondary small leading-relaxed">
              <div class="alert alert-secondary py-2 px-3 mb-3">
                <strong>Colegio de Arquitectos de la Provincia de Córdoba - Regional 1</strong><br>
                Programa: "Caja de Herramientas R1 - Instrumental Técnico en Préstamo"
              </div>

              <h6 class="fw-bold text-dark mt-3">CLÁUSULA PRIMERA: OBJETO Y BENEFICIARIOS</h6>
              <p>El Colegio de Arquitectos de la Provincia de Córdoba - Regional 1 cede en comodato y de manera gratuita el uso del instrumental técnico y equipos de medición solicitados, exclusivamente a profesionales matriculados con matrícula habilitada al día.</p>

              <h6 class="fw-bold text-dark mt-3">CLÁUSULA SEGUNDA: PLAZO DE PRÉSTAMO Y PRÓRROGAS</h6>
              <p>El plazo máximo de tenencia por reserva es de <strong>tres (3) días corridos</strong>. La devolución debe realizarse en la misma sede pactada, en los horarios de atención fijados. El incumplimiento del plazo acarreará la suspensión temporal de futuros préstamos.</p>

              <h6 class="fw-bold text-dark mt-3">CLÁUSULA TERCERA: LÍMITE DE PRÉSTAMOS SIMULTÁNEOS</h6>
              <p>Cada profesional matriculado podrá tener en su poder un <strong>máximo de dos (2) equipos en simultáneo</strong>. Hasta que no se efectivice la devolución fehaciente en sede, no se autorizarán nuevos retiros.</p>

              <h6 class="fw-bold text-dark mt-3">CLÁUSULA CUARTA: CUIDADO, CUSTODIA Y ESTADO DEL EQUIPO</h6>
              <p>El matriculado comodatario recibe el equipo con sus accesorios, manuales y valija protectora en perfecto estado de funcionamiento y calibración. Se compromete a emplearlo conforme las buenas prácticas del arte y las especificaciones del fabricante, haciéndose responsable civilmente por extravío, rotura o daño por uso indebido.</p>

              <h6 class="fw-bold text-dark mt-3">CLÁUSULA QUINTA: CAPACITACIÓN PREVIA</h6>
              <p>Para aquellos equipos rotulados con "Requiere capacitación previa" (ej. Telurímetro, Esclerómetro, Manómetro), el profesional declara bajo juramento contar con la idoneidad y capacitación correspondiente para su operación.</p>
            </div>
            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary btn-sm" (click)="cerrar.emit()">Entendido</button>
            </div>
          </div>
        </div>
      </div>
    }
  `
})
export class ComodatoModalComponent {
  @Input() visible = false;
  @Output() cerrar = new EventEmitter<void>();
}

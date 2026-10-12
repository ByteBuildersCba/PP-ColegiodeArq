import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-whatsapp-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <a
      [href]="whatsappUrl"
      target="_blank"
      rel="noopener noreferrer"
      class="whatsapp-floating-btn"
      aria-label="Contactar por WhatsApp para consultas sobre Caja de Herramientas R1"
      title="Consultas técnicas y reservas por WhatsApp">
      <i class="bi bi-whatsapp"></i>
    </a>
  `,
  styles: [`
    :host {
      display: block;
    }
  `]
})
export class WhatsappButtonComponent {
  // WhatsApp oficial institucional CAPC
  readonly phoneNumber = '5493514684500';
  readonly defaultMessage = encodeURIComponent(
    'Hola! Me comunico desde el portal de Caja de Herramientas R1 del Colegio de Arquitectos de Córdoba para realizar una consulta técnica sobre el préstamo de equipos.'
  );

  get whatsappUrl(): string {
    return `https://wa.me/${this.phoneNumber}?text=${this.defaultMessage}`;
  }
}

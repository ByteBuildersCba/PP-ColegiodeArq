import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HeaderComponent } from './components/header/header.component';
import { FiltrosComponent } from './components/filtros/filtros.component';
import { CatalogoComponent } from './components/catalogo/catalogo.component';
import { ReservaDrawerComponent } from './components/reserva-drawer/reserva-drawer.component';
import { ComodatoModalComponent } from './components/comodato-modal/comodato-modal.component';
import { MisReservasModalComponent } from './components/mis-reservas-modal/mis-reservas-modal.component';
import { WhatsappButtonComponent } from './components/whatsapp-button/whatsapp-button.component';
import { HerramientasService } from './services/herramientas.service';
import { Herramienta, Reserva } from './models/herramienta.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    HeaderComponent,
    FiltrosComponent,
    CatalogoComponent,
    ReservaDrawerComponent,
    ComodatoModalComponent,
    MisReservasModalComponent,
    WhatsappButtonComponent
  ],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App {
  // Estado del drawer de reserva
  drawerVisible = signal(false);
  herramientaSeleccionada = signal<Herramienta | null>(null);

  // Modales adicionales
  comodatoModalVisible = signal(false);
  misReservasModalVisible = signal(false);

  constructor(public herramientasService: HerramientasService) {}

  abrirReserva(herramienta: Herramienta): void {
    this.herramientaSeleccionada.set(herramienta);
    this.drawerVisible.set(true);
  }

  cerrarDrawer(): void {
    this.drawerVisible.set(false);
  }

  abrirComodato(): void {
    this.comodatoModalVisible.set(true);
  }

  cerrarComodato(): void {
    this.comodatoModalVisible.set(false);
  }

  abrirMisReservas(): void {
    this.misReservasModalVisible.set(true);
  }

  cerrarMisReservas(): void {
    this.misReservasModalVisible.set(false);
  }

  onReservaConfirmada(reserva: Reserva): void {
    // Si se desea ejecutar acciones adicionales al confirmar
  }
}

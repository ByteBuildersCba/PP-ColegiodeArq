import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HerramientasService } from '../../services/herramientas.service';
import { AuthService } from '../../services/auth.service';
import { Sede } from '../../models/herramienta.model';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {
  @Output() abrirMisReservas = new EventEmitter<void>();
  @Output() abrirAuth = new EventEmitter<void>();
  @Output() toggleVistaAdmin = new EventEmitter<void>();

  menuHerramientasAbierto = false;
  menuUsuarioAbierto = false;

  constructor(
    public herramientasService: HerramientasService,
    public authService: AuthService
  ) {}

  onSedeChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    const selectedSede = this.herramientasService.sedes().find(s => s.id === Number(select.value));
    if (selectedSede) {
      this.herramientasService.setSede(selectedSede);
    }
  }

  toggleMenuHerramientas(): void {
    this.menuHerramientasAbierto = !this.menuHerramientasAbierto;
  }

  toggleMenuUsuario(): void {
    this.menuUsuarioAbierto = !this.menuUsuarioAbierto;
  }
}

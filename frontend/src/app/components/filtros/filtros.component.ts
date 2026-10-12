import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HerramientasService } from '../../services/herramientas.service';

@Component({
  selector: 'app-filtros',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './filtros.component.html',
  styleUrls: ['./filtros.component.css']
})
export class FiltrosComponent {
  query = '';

  constructor(public herramientasService: HerramientasService) {}

  onSearch(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.query = input.value;
    this.herramientasService.setBusqueda(this.query);
  }

  seleccionarCategoria(nombre: string): void {
    this.herramientasService.setCategoria(nombre);
  }

  limpiarBusqueda(): void {
    this.query = '';
    this.herramientasService.setBusqueda('');
  }
}

import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HerramientasService } from '../../services/herramientas.service';
import { Herramienta } from '../../models/herramienta.model';

@Component({
  selector: 'app-catalogo',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './catalogo.component.html',
  styleUrls: ['./catalogo.component.css']
})
export class CatalogoComponent {
  @Output() seleccionarHerramienta = new EventEmitter<Herramienta>();

  constructor(public herramientasService: HerramientasService) {}

  onReservar(herramienta: Herramienta): void {
    this.seleccionarHerramienta.emit(herramienta);
  }
}

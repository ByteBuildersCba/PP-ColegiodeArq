import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { VerificacionMatriculaRespuesta } from '../../models/herramienta.model';

@Component({
  selector: 'app-auth-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    @if (visible) {
      <div class="modal-backdrop fade show" (click)="cerrar.emit()"></div>
      <div class="modal fade show d-block" tabindex="-1" role="dialog" aria-labelledby="authTitle" aria-modal="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow-lg auth-modal-card">
            
            <!-- Modal Header con Tabs -->
            <div class="modal-header border-0 pb-0 bg-white">
              <div class="d-flex w-100 justify-content-between align-items-center">
                <ul class="nav nav-pills custom-auth-tabs">
                  <li class="nav-item">
                    <button
                      type="button"
                      class="nav-link"
                      [class.active]="tabActiva === 'login'"
                      (click)="setTab('login')">
                      Iniciar Sesión
                    </button>
                  </li>
                  <li class="nav-item">
                    <button
                      type="button"
                      class="nav-link"
                      [class.active]="tabActiva === 'registro'"
                      (click)="setTab('registro')">
                      Registro de Matrícula
                    </button>
                  </li>
                </ul>
                <button type="button" class="btn-close" (click)="cerrar.emit()" aria-label="Cerrar"></button>
              </div>
            </div>

            <!-- Modal Body -->
            <div class="modal-body p-4 pt-3">
              
              <!-- Tab 1: Iniciar Sesión -->
              @if (tabActiva === 'login') {
                <form (ngSubmit)="onLogin()">
                  <div class="text-center mb-3">
                    <h5 class="fw-bold text-dark m-0" id="authTitle">Autogestión de Matrícula</h5>
                    <p class="text-secondary small mt-1">Acceso para arquitectos y administradores de sede</p>
                  </div>

                  @if (mensajeError) {
                    <div class="alert alert-danger py-2 px-3 small rounded-2 mb-3">
                      <i class="bi bi-exclamation-circle-fill me-1"></i> {{ mensajeError }}
                    </div>
                  }

                  <div class="mb-3">
                    <label class="form-label small fw-bold text-dark">Matrícula o Correo Electrónico</label>
                    <div class="input-group">
                      <span class="input-group-text bg-light"><i class="bi bi-person-fill"></i></span>
                      <input
                        type="text"
                        class="form-control"
                        placeholder="Ej: M1 o correo@colegioarq.org.ar"
                        [(ngModel)]="loginUser"
                        name="loginUser"
                        required
                      />
                    </div>
                  </div>

                  <div class="mb-3">
                    <label class="form-label small fw-bold text-dark">Contraseña</label>
                    <div class="input-group">
                      <span class="input-group-text bg-light"><i class="bi bi-key-fill"></i></span>
                      <input
                        type="password"
                        class="form-control"
                        placeholder="••••••••"
                        [(ngModel)]="loginPass"
                        name="loginPass"
                        required
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    class="btn btn-capc-primary w-100 py-2.5 fw-bold mb-3"
                    [disabled]="cargando">
                    @if (cargando) {
                      <span class="spinner-border spinner-border-sm me-1"></span> Ingresando...
                    } @else {
                      <i class="bi bi-box-arrow-in-right me-1"></i> Ingresar al Sistema
                    }
                  </button>

                  <!-- Accesos rápidos Demo para pruebas -->
                  <div class="demo-access-box p-3 rounded-3 border bg-light">
                    <span class="d-block text-xs text-muted fw-bold text-uppercase mb-2">Accesos directos de prueba:</span>
                    <div class="d-flex flex-column gap-1.5">
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-primary text-start d-flex justify-content-between align-items-center"
                        (click)="entrarDemo('ARQUITECTO')">
                        <span><i class="bi bi-person-badge me-1"></i> Arq. Damián Coronda</span>
                        <span class="badge bg-primary">Matrícula M1</span>
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-dark text-start d-flex justify-content-between align-items-center"
                        (click)="entrarDemo('ADMIN_PANOL')">
                        <span><i class="bi bi-shield-lock-fill me-1"></i> Administrador de Pañol</span>
                        <span class="badge bg-dark">Control Sedes</span>
                      </button>
                    </div>
                  </div>
                </form>
              }

              <!-- Tab 2: Registro con Verificación de Matrícula -->
              @if (tabActiva === 'registro') {
                <form (ngSubmit)="onRegistro()">
                  <div class="text-center mb-3">
                    <h5 class="fw-bold text-dark m-0">Registro Profesional</h5>
                    <p class="text-secondary small mt-1">Validación en el Padrón Oficial Regional 1</p>
                  </div>

                  <!-- Campo Matrícula con Botón Verificar -->
                  <div class="mb-3">
                    <label class="form-label small fw-bold text-dark d-flex justify-content-between">
                      <span>Número de Matrícula</span>
                      <span class="text-xs text-muted">Ej: M2045, M3180, M4521</span>
                    </label>
                    <div class="input-group">
                      <span class="input-group-text bg-light"><i class="bi bi-card-heading"></i></span>
                      <input
                        type="text"
                        class="form-control"
                        placeholder="Ej: M2045"
                        [(ngModel)]="registroMatricula"
                        name="registroMatricula"
                        (input)="onMatriculaInput()"
                        required
                      />
                      <button
                        type="button"
                        class="btn btn-outline-primary fw-semibold btn-sm"
                        (click)="verificarMatricula()"
                        [disabled]="verificando || !registroMatricula">
                        @if (verificando) {
                          <span class="spinner-border spinner-border-sm"></span>
                        } @else {
                          Verificar Padrón
                        }
                      </button>
                    </div>
                  </div>

                  <!-- Estado de Validación de la Matrícula -->
                  @if (resultadoMatricula) {
                    @if (resultadoMatricula.valida) {
                      <div class="alert alert-success py-2 px-3 small rounded-2 mb-3 d-flex align-items-start gap-2">
                        <i class="bi bi-check-circle-fill text-success fs-5 mt-0.5"></i>
                        <div>
                          <strong>{{ resultadoMatricula.nombre_titular }}</strong><br>
                          <span class="text-success-emphasis fw-medium">{{ resultadoMatricula.estado_vigencia }}</span> · Matrícula habilitada para préstamos.
                        </div>
                      </div>
                    } @else {
                      <div class="alert alert-danger py-2 px-3 small rounded-2 mb-3 d-flex align-items-start gap-2">
                        <i class="bi bi-x-circle-fill text-danger fs-5 mt-0.5"></i>
                        <div>
                          <strong>Matrícula No Habilitada</strong><br>
                          <span>{{ resultadoMatricula.mensaje }}</span>
                        </div>
                      </div>
                    }
                  }

                  <div class="mb-3">
                    <label class="form-label small fw-bold text-dark">Correo Electrónico</label>
                    <input
                      type="email"
                      class="form-control"
                      placeholder="arquitecto@ejemplo.com"
                      [(ngModel)]="registroEmail"
                      name="registroEmail"
                      required
                    />
                  </div>

                  <div class="mb-3">
                    <label class="form-label small fw-bold text-dark">Teléfono / Celular de Contacto</label>
                    <input
                      type="tel"
                      class="form-control"
                      placeholder="+54 9 351 123-4567"
                      [(ngModel)]="registroTelefono"
                      name="registroTelefono"
                    />
                  </div>

                  <div class="mb-3">
                    <label class="form-label small fw-bold text-dark">Contraseña</label>
                    <input
                      type="password"
                      class="form-control"
                      placeholder="Mínimo 6 caracteres"
                      [(ngModel)]="registroPass"
                      name="registroPass"
                      required
                    />
                  </div>

                  @if (mensajeError) {
                    <div class="alert alert-danger py-2 px-3 small rounded-2 mb-3">
                      {{ mensajeError }}
                    </div>
                  }

                  <button
                    type="submit"
                    class="btn btn-capc-primary w-100 py-2.5 fw-bold"
                    [disabled]="cargando || !resultadoMatricula || !resultadoMatricula.valida">
                    @if (cargando) {
                      <span class="spinner-border spinner-border-sm me-1"></span> Registrando...
                    } @else {
                      <i class="bi bi-person-check-fill me-1"></i> Confirmar Registro Profesional
                    }
                  </button>
                </form>
              }

            </div>
          </div>
        </div>
      </div>
    }
  `,
  styles: [`
    .auth-modal-card {
      border-radius: 12px;
      overflow: hidden;
    }
    .custom-auth-tabs .nav-link {
      font-size: 0.84rem;
      font-weight: 700;
      color: #64748b;
      padding: 0.5rem 0.9rem;
      border-radius: 6px;
      border: none;
    }
    .custom-auth-tabs .nav-link.active {
      background-color: #004b87;
      color: #ffffff;
    }
    .text-xs {
      font-size: 0.72rem;
    }
    .demo-access-box {
      border-color: #e2e8f0;
    }
  `]
})
export class AuthModalComponent {
  @Input() visible = false;
  @Output() cerrar = new EventEmitter<void>();
  @Output() usuarioAutenticado = new EventEmitter<void>();

  tabActiva: 'login' | 'registro' = 'login';

  // Login
  loginUser = '';
  loginPass = '';

  // Registro
  registroMatricula = '';
  registroEmail = '';
  registroTelefono = '';
  registroPass = '';

  verificando = false;
  resultadoMatricula: VerificacionMatriculaRespuesta | null = null;

  cargando = false;
  mensajeError = '';

  constructor(public authService: AuthService) {}

  setTab(tab: 'login' | 'registro'): void {
    this.tabActiva = tab;
    this.mensajeError = '';
  }

  onMatriculaInput(): void {
    this.resultadoMatricula = null;
    this.mensajeError = '';
  }

  verificarMatricula(): void {
    if (!this.registroMatricula) return;
    this.verificando = true;
    this.mensajeError = '';

    this.authService.verificarMatricula(this.registroMatricula).subscribe(res => {
      this.verificando = false;
      this.resultadoMatricula = res;
      if (!res.valida) {
        this.mensajeError = res.mensaje;
      }
    });
  }

  onLogin(): void {
    if (!this.loginUser || !this.loginPass) {
      this.mensajeError = 'Por favor complete su usuario/matrícula y contraseña.';
      return;
    }

    this.cargando = true;
    this.mensajeError = '';

    this.authService.login(this.loginUser, this.loginPass).subscribe(res => {
      this.cargando = false;
      if (res.ok) {
        this.usuarioAutenticado.emit();
        this.cerrar.emit();
      } else {
        this.mensajeError = res.mensaje;
      }
    });
  }

  onRegistro(): void {
    if (!this.resultadoMatricula?.valida) {
      this.mensajeError = 'Debe verificar previamente una matrícula vigente.';
      return;
    }
    if (!this.registroEmail || !this.registroPass) {
      this.mensajeError = 'Complete todos los campos requeridos.';
      return;
    }

    this.cargando = true;
    this.mensajeError = '';

    this.authService.registro(
      this.registroMatricula,
      this.registroEmail,
      this.registroPass,
      this.registroTelefono
    ).subscribe(res => {
      this.cargando = false;
      if (res.ok) {
        this.usuarioAutenticado.emit();
        this.cerrar.emit();
      } else {
        this.mensajeError = res.mensaje;
      }
    });
  }

  entrarDemo(rol: 'ARQUITECTO' | 'ADMIN_PANOL'): void {
    this.authService.cambiarRolDemo(rol);
    this.usuarioAutenticado.emit();
    this.cerrar.emit();
  }
}

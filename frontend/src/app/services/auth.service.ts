import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, catchError, map } from 'rxjs';
import { Usuario, VerificacionMatriculaRespuesta } from '../models/herramienta.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly apiUrl = 'http://127.0.0.1:8000/api';

  // Usuario predeterminado inicial: Arq. Damián Coronda
  readonly usuarioActual = signal<Usuario>({
    id: 1,
    username: 'm1',
    email: 'damian.coronda@colegioarq.org.ar',
    nombre: 'Arq. Damián Coronda',
    matricula: 'M1',
    estado_matricula: 'Matrícula Habilitada - M1',
    rol: 'ARQUITECTO'
  });

  readonly isLoggedIn = computed(() => !!this.usuarioActual());
  readonly isAdmin = computed(() => this.usuarioActual()?.rol === 'ADMIN_PANOL');
  readonly isArquitecto = computed(() => this.usuarioActual()?.rol === 'ARQUITECTO');

  constructor(private http: HttpClient) {}

  verificarMatricula(matricula: string): Observable<VerificacionMatriculaRespuesta> {
    const mat = matricula.trim().toUpperCase();

    return this.http.get<VerificacionMatriculaRespuesta>(`${this.apiUrl}/auth/verificar-matricula/?matricula=${mat}`).pipe(
      catchError((err) => {
        // Fallback local en memoria con el padrón simulado
        const padronSimulado: Record<string, { titular: string; vigente: boolean; estado: string }> = {
          'M1': { titular: 'Arq. Damián Coronda', vigente: true, estado: 'Matrícula Habilitada - Vigente' },
          'M2045': { titular: 'Arq. María Eugenia Silva', vigente: true, estado: 'Matrícula Habilitada - Vigente' },
          'M3180': { titular: 'Arq. Lucas Benítez', vigente: true, estado: 'Matrícula Habilitada - Vigente' },
          'M4521': { titular: 'Arq. Florencia Rossi', vigente: true, estado: 'Matrícula Habilitada - Vigente' },
          'M9999': { titular: 'Arq. Roberto Morales', vigente: false, estado: 'Matrícula Suspendida / Mora' },
        };

        const res = padronSimulado[mat];
        if (res) {
          return of({
            valida: res.vigente,
            numero_matricula: mat,
            nombre_titular: res.titular,
            estado_vigencia: res.estado,
            mensaje: res.vigente ? 'Matrícula habilitada y vigente en el Padrón Oficial.' : 'Matrícula no habilitada (posee deuda o suspensión).'
          });
        }

        return of({
          valida: false,
          mensaje: `La matrícula '${mat}' no fue encontrada en el Padrón Oficial de la Regional 1.`
        });
      })
    );
  }

  registro(numeroMatricula: string, email: string, password: string, telefono: string): Observable<{ ok: boolean; mensaje: string; usuario?: Usuario }> {
    const payload = {
      numero_matricula: numeroMatricula.trim().toUpperCase(),
      email: email.trim().toLowerCase(),
      password,
      telefono
    };

    return this.http.post<any>(`${this.apiUrl}/auth/registro/`, payload).pipe(
      map(res => {
        const user: Usuario = res.usuario;
        this.usuarioActual.set(user);
        return { ok: true, mensaje: res.mensaje, usuario: user };
      }),
      catchError(err => {
        const errorMsg = err?.error?.numero_matricula?.[0] || err?.error?.email?.[0] || 'Error al registrar el profesional.';
        return of({ ok: false, mensaje: errorMsg });
      })
    );
  }

  login(usernameOrMatricula: string, password: string): Observable<{ ok: boolean; mensaje: string; usuario?: Usuario }> {
    const payload = {
      username_or_matricula: usernameOrMatricula.trim(),
      password
    };

    return this.http.post<any>(`${this.apiUrl}/auth/login/`, payload).pipe(
      map(res => {
        const user: Usuario = res.usuario;
        this.usuarioActual.set(user);
        return { ok: true, mensaje: res.mensaje, usuario: user };
      }),
      catchError(() => {
        // Fallback demo local si el backend no está disponible
        const input = usernameOrMatricula.toLowerCase().trim();
        if (input.includes('admin') || input.includes('panol')) {
          const adminUser: Usuario = {
            id: 2,
            username: 'admin.panol',
            email: 'admin.panol@colegioarq.org.ar',
            nombre: 'Administrador de Pañol R1',
            matricula: 'ADM-R1',
            estado_matricula: 'Administrador General de Pañol',
            rol: 'ADMIN_PANOL'
          };
          this.usuarioActual.set(adminUser);
          return of({ ok: true, mensaje: 'Sesión iniciada como Administrador de Pañol.', usuario: adminUser });
        } else {
          const arqUser: Usuario = {
            id: 1,
            username: 'm1',
            email: 'damian.coronda@colegioarq.org.ar',
            nombre: 'Arq. Damián Coronda',
            matricula: 'M1',
            estado_matricula: 'Matrícula Habilitada - M1',
            rol: 'ARQUITECTO'
          };
          this.usuarioActual.set(arqUser);
          return of({ ok: true, mensaje: 'Sesión iniciada como Arquitecto Matriculado.', usuario: arqUser });
        }
      })
    );
  }

  logout(): void {
    // Por defecto al salir vuelve al matriculado demo o vacía la sesión
    this.usuarioActual.set({
      id: 1,
      username: 'm1',
      email: 'damian.coronda@colegioarq.org.ar',
      nombre: 'Arq. Damián Coronda',
      matricula: 'M1',
      estado_matricula: 'Matrícula Habilitada - M1',
      rol: 'ARQUITECTO'
    });
  }

  cambiarRolDemo(rol: 'ARQUITECTO' | 'ADMIN_PANOL'): void {
    if (rol === 'ADMIN_PANOL') {
      this.usuarioActual.set({
        id: 2,
        username: 'admin.panol',
        email: 'admin.panol@colegioarq.org.ar',
        nombre: 'Administrador de Pañol R1',
        matricula: 'ADM-R1',
        estado_matricula: 'Administrador General de Pañol (Todas las Sedes)',
        rol: 'ADMIN_PANOL'
      });
    } else {
      this.usuarioActual.set({
        id: 1,
        username: 'm1',
        email: 'damian.coronda@colegioarq.org.ar',
        nombre: 'Arq. Damián Coronda',
        matricula: 'M1',
        estado_matricula: 'Matrícula Habilitada - M1',
        rol: 'ARQUITECTO'
      });
    }
  }
}

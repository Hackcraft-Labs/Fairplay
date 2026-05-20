import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface AuthState {
  token: string | null;
  username: string | null;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
	private readonly state$ = new BehaviorSubject<AuthState>({ token: null, username: null });

	get authState$(): Observable<AuthState> {
		return this.state$.asObservable();
	}

	get token(): string | null {
		return this.state$.value.token;
	}

	login(token: string, username: string): void {
		this.state$.next({ token, username });
		// Persist if desired: localStorage.setItem('fp_token', token);
	}

	logout(): void {
		this.state$.next({ token: null, username: null });
		// localStorage.removeItem('fp_token');
	}
}
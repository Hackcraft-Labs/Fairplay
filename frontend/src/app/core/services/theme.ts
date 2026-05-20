import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type ThemeMode = 'light' | 'dark';

@Injectable({ providedIn: 'root' })
export class ThemeService {
	private readonly mode$ = new BehaviorSubject<ThemeMode>('light');

	get theme$() {
		return this.mode$.asObservable();
	}

	get current(): ThemeMode {
		return this.mode$.value;
	}

	toggle(): void {
		const next: ThemeMode = this.current === 'light' ? 'dark' : 'light';
		this.set(next);
	}

	set(mode: ThemeMode): void {
		this.mode$.next(mode);
		document.body.classList.toggle('dark-theme', mode === 'dark');
	}
}
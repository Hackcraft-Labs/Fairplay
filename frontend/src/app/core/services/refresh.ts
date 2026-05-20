import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';

/**
 * Emits when app-wide data should be re-fetched (e.g. after reset DB from the shell).
 */
@Injectable({ providedIn: 'root' })
export class RefreshService {
	private readonly dataChanged$ = new Subject<void>();

	afterDataChanged(): Observable<void> {
		return this.dataChanged$.asObservable();
	}

	notifyDataChanged(): void {
		this.dataChanged$.next();
	}
}

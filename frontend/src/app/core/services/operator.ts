import { inject, Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { ApiService } from './api';
import { environment } from '../../../environments/environment';

export type ResetDbResponse = {
	ok: boolean;
	deleted?: Record<string, number>;
};

@Injectable({ providedIn: 'root' })
export class OperatorService {
	private readonly api = inject(ApiService);
	private readonly useMockData = environment.useMockData;

	resetDb(): Observable<ResetDbResponse> {
		if (this.useMockData) {
			return of({ ok: true, deleted: { mock: 1 } });
		}

		return this.api.post<ResetDbResponse, Record<string, never>>('/ops/reset-db', {});
	}
}


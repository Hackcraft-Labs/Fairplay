import { inject, Injectable } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { ApiService } from './api';
import { Ioc } from '../models/ioc';
import { environment } from '../../../environments/environment';
import { MOCK_IOCS } from '../mocks/iocs.mock';

let mockIocsStore: Ioc[] = MOCK_IOCS.map(ioc => ({ ...ioc }));

@Injectable({ providedIn: 'root' })
export class IocService {
    private readonly api = inject(ApiService);
    private readonly resourcePath = '/iocs';
    private readonly useMockData = environment.useMockData;

    list(): Observable<Ioc[]> {
        if (this.useMockData) {
            return of(mockIocsStore.map(ioc => ({ ...ioc })));
        }

        return this.api.get<Ioc[]>(this.resourcePath);
    }

    get(name: string): Observable<Ioc> {
        if (this.useMockData) {
            const ioc = mockIocsStore.find(item => item.name === name);
            return ioc ? of({ ...ioc }) : throwError(() => new Error(`IOC "${name}" not found.`));
        }

        return this.api.get<Ioc>(`${this.resourcePath}/${encodeURIComponent(name)}`);
    }

    create(payload: Ioc): Observable<Ioc> {
        if (this.useMockData) {
            const created = { ...payload };
            mockIocsStore = [created, ...mockIocsStore];
            return of({ ...created });
        }

        return this.api.post<Ioc, Ioc>(this.resourcePath, payload);
    }

    update(name: string, payload: Ioc): Observable<Ioc> {
        if (this.useMockData) {
            const index = mockIocsStore.findIndex(item => item.name === name);
            if (index < 0) {
                return throwError(() => new Error(`IOC "${name}" not found.`));
            }

            const updated = { ...payload };
            mockIocsStore = mockIocsStore.map((item, currentIndex) =>
                currentIndex === index ? updated : item
            );
            return of({ ...updated });
        }

        return this.api.put<Ioc, Ioc>(
            `${this.resourcePath}/${encodeURIComponent(name)}`,
            payload
        );
    }

    delete(name: string): Observable<void> {
        if (this.useMockData) {
            const initialLength = mockIocsStore.length;
            mockIocsStore = mockIocsStore.filter(item => item.name !== name);
            if (mockIocsStore.length === initialLength) {
                return throwError(() => new Error(`IOC "${name}" not found.`));
            }
            return of(void 0);
        }

        return this.api.delete<void>(`${this.resourcePath}/${encodeURIComponent(name)}`);
    }

	resetMockStore(): void {
		if (this.useMockData) {
			mockIocsStore = [];
		}
	}
}
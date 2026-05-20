import { inject, Injectable } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { ApiService } from './api';
import { Detection } from '../models/detection';
import { environment } from '../../../environments/environment';
import { MOCK_DETECTIONS } from '../mocks/detections.mock';

let mockDetectionsStore: Detection[] = MOCK_DETECTIONS.map(det => ({ ...det }));

@Injectable({ providedIn: 'root' })
export class DetectionService {
    private readonly api = inject(ApiService);
    private readonly resourcePath = '/detections';
    private readonly useMockData = environment.useMockData;

    list(): Observable<Detection[]> {
        if (this.useMockData) {
            return of(mockDetectionsStore.map(det => ({ ...det })));
        }

        return this.api.get<Detection[]>(this.resourcePath);
    }

    get(fileHash: string): Observable<Detection> {
        if (this.useMockData) {
            const detection = mockDetectionsStore.find(det => det.file_hash === fileHash);
            return detection
                ? of({ ...detection })
                : throwError(() => new Error(`Detection "${fileHash}" not found.`));
        }

        return this.api.get<Detection>(`${this.resourcePath}/${encodeURIComponent(fileHash)}`);
    }

    create(payload: Detection): Observable<Detection> {
        if (this.useMockData) {
            const created = { ...payload };
            mockDetectionsStore = [created, ...mockDetectionsStore];
            return of({ ...created });
        }

        return this.api.post<Detection, Detection>(this.resourcePath, payload);
    }

    update(fileHash: string, payload: Detection): Observable<Detection> {
        if (this.useMockData) {
            const index = mockDetectionsStore.findIndex(det => det.file_hash === fileHash);
            if (index < 0) {
                return throwError(() => new Error(`Detection "${fileHash}" not found.`));
            }

            const updated = { ...payload };
            mockDetectionsStore = mockDetectionsStore.map((det, currentIndex) =>
                currentIndex === index ? updated : det
            );
            return of({ ...updated });
        }

        return this.api.put<Detection, Detection>(
            `${this.resourcePath}/${encodeURIComponent(fileHash)}`,
            payload
        );
    }

  	delete(fileHash: string): Observable<void> {
        if (this.useMockData) {
            const initialLength = mockDetectionsStore.length;
            mockDetectionsStore = mockDetectionsStore.filter(det => det.file_hash !== fileHash);
            if (mockDetectionsStore.length === initialLength) {
                return throwError(() => new Error(`Detection "${fileHash}" not found.`));
            }
            return of(void 0);
        }

    	return this.api.delete<void>(`${this.resourcePath}/${encodeURIComponent(fileHash)}`);
  	}

	resetMockStore(): void {
		if (this.useMockData) {
			mockDetectionsStore = [];
		}
	}
}
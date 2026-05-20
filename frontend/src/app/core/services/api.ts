import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
    private readonly http = inject(HttpClient);
    private readonly baseUrl = environment.apiBaseUrl;

    get<T>(path: string, params?: Record<string, string | number | boolean>): Observable<T> {
        const httpParams = new HttpParams({
            fromObject: (params ?? {}) as Record<string, string>
        });

        return this.http.get<T>(`${this.baseUrl}${path}`, { params: httpParams });
    }

    post<T, B = unknown>(path: string, body: B): Observable<T> {
        return this.http.post<T>(`${this.baseUrl}${path}`, body);
    }

    put<T, B = unknown>(path: string, body: B): Observable<T> {
        return this.http.put<T>(`${this.baseUrl}${path}`, body);
    }

    delete<T>(path: string): Observable<T> {
        return this.http.delete<T>(`${this.baseUrl}${path}`);
    }
}
import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

/** The public JSON contract returned by FastAPI's liveness endpoint. */
export interface HealthResponse {
  status: 'ok';
  service: string;
  version: string;
  environment: string;
}

@Injectable({ providedIn: 'root' })
export class HealthApiService {
  private readonly http = inject(HttpClient);

  /** Ask the backend whether its application process is serving requests. */
  getHealth(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>('/api/v1/health');
  }
}

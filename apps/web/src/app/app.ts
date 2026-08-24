import { Component, inject, OnInit, signal } from '@angular/core';
import { timeout } from 'rxjs';

import { HealthApiService, HealthResponse } from './core/api/health-api.service';

type ConnectionState = 'checking' | 'connected' | 'unavailable';

@Component({
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App implements OnInit {
  private readonly healthApi = inject(HealthApiService);

  protected readonly connectionState = signal<ConnectionState>('checking');
  protected readonly health = signal<HealthResponse | null>(null);
  protected readonly errorMessage = signal('');

  ngOnInit(): void {
    this.checkConnection();
  }

  protected checkConnection(): void {
    this.connectionState.set('checking');
    this.health.set(null);
    this.errorMessage.set('');

    this.healthApi
      .getHealth()
      .pipe(timeout(5_000))
      .subscribe({
        next: (response) => {
          this.health.set(response);
          this.connectionState.set('connected');
        },
        error: () => {
          this.errorMessage.set(
            'The API did not respond. Confirm that FastAPI is running on port 8000.',
          );
          this.connectionState.set('unavailable');
        },
      });
  }
}

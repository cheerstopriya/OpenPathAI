import { TestBed } from '@angular/core/testing';
import { Observable, of, throwError } from 'rxjs';

import { App } from './app';
import { HealthApiService, HealthResponse } from './core/api/health-api.service';

describe('App', () => {
  const health: HealthResponse = {
    status: 'ok',
    service: 'OpenPath AI API',
    version: '0.1.0',
    environment: 'test',
  };

  async function renderWith(response: Observable<HealthResponse>) {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        {
          provide: HealthApiService,
          useValue: { getHealth: () => response },
        },
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
    return fixture.nativeElement as HTMLElement;
  }

  it('shows backend details when the health request succeeds', async () => {
    const element = await renderWith(of(health));

    expect(element.textContent).toContain('Backend connected');
    expect(element.textContent).toContain('OpenPath AI API version 0.1.0');
    expect(element.textContent).toContain('test');
  });

  it('shows a retry action when the health request fails', async () => {
    const element = await renderWith(throwError(() => new Error('offline')));

    expect(element.textContent).toContain('Backend unavailable');
    expect(element.querySelector('button')?.textContent).toContain('Try again');
  });
});

import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { HealthApiService, HealthResponse } from './health-api.service';

describe('HealthApiService', () => {
  let service: HealthApiService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });

    service = TestBed.inject(HealthApiService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  it('requests the versioned backend health endpoint', () => {
    const expected: HealthResponse = {
      status: 'ok',
      service: 'OpenPath AI API',
      version: '0.1.0',
      environment: 'test',
    };

    service.getHealth().subscribe((response) => expect(response).toEqual(expected));

    const request = httpTesting.expectOne('/api/v1/health');
    expect(request.request.method).toBe('GET');
    request.flush(expected);
  });
});

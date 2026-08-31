import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { RepositoryApiService, RepositoryPreview } from './repository-api.service';

describe('RepositoryApiService', () => {
  let service: RepositoryApiService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(RepositoryApiService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  it('posts the repository URL to the preview endpoint', () => {
    const repositoryUrl = 'https://github.com/angular/angular';
    const expected = createRepositoryPreview();

    service.preview(repositoryUrl).subscribe((response) => expect(response).toEqual(expected));

    const request = httpTesting.expectOne('/api/v1/repositories/preview');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ repository_url: repositoryUrl });
    request.flush(expected);
  });
});

function createRepositoryPreview(): RepositoryPreview {
  return {
    owner: 'angular',
    name: 'angular',
    full_name: 'angular/angular',
    description: 'Web framework',
    html_url: 'https://github.com/angular/angular',
    primary_language: 'TypeScript',
    stars: 100,
    forks: 20,
    default_branch: 'main',
    archived: false,
    disabled: false,
    visibility: 'public',
    topics: ['typescript'],
    license_spdx: 'MIT',
    pushed_at: '2026-08-20T10:00:00Z',
  };
}

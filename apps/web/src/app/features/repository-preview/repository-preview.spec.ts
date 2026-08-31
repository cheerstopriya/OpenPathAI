import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { RepositoryApiService, RepositoryPreview } from '../../core/api/repository-api.service';
import { RepositoryPreviewComponent } from './repository-preview';

describe('RepositoryPreviewComponent', () => {
  let fixture: ComponentFixture<RepositoryPreviewComponent>;
  let previewCalls: string[];

  const repository: RepositoryPreview = {
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

  beforeEach(async () => {
    previewCalls = [];
    await TestBed.configureTestingModule({
      imports: [RepositoryPreviewComponent],
      providers: [
        {
          provide: RepositoryApiService,
          useValue: {
            preview: (url: string) => {
              previewCalls.push(url);
              return of(repository);
            },
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(RepositoryPreviewComponent);
    fixture.detectChanges();
  });

  it('does not call the API for an invalid URL', () => {
    fixture.componentInstance.repositoryUrl.setValue('http://127.0.0.1/private');
    fixture.componentInstance.submit();
    fixture.detectChanges();

    expect(previewCalls).toEqual([]);
    expect(fixture.nativeElement.textContent).toContain('Enter a URL in the form');
  });

  it('renders repository details after a successful request', async () => {
    fixture.componentInstance.repositoryUrl.setValue('https://github.com/angular/angular');
    fixture.componentInstance.submit();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(previewCalls).toEqual(['https://github.com/angular/angular']);
    expect(fixture.nativeElement.textContent).toContain('angular/angular');
    expect(fixture.nativeElement.textContent).toContain('TypeScript');
  });
});

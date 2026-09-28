import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, Subject } from 'rxjs';

import {
  RepositoryApiService,
  Investigation,
  RepositoryPreview,
  RepositoryReadiness,
  OpportunityList,
} from '../../core/api/repository-api.service';
import { RepositoryPreviewComponent } from './repository-preview';

describe('RepositoryPreviewComponent', () => {
  let fixture: ComponentFixture<RepositoryPreviewComponent>;
  let previewCalls: string[];
  let briefResponse: Subject<Investigation>;
  const brief: Investigation = {
    repository_full_name: 'angular/angular', issue_number: 1, issue_title: 'Example issue',
    issue_state: 'open', fetched_at: '2026-09-28T00:00:00Z', generation_mode: 'deterministic',
    evidence: [{id: 'issue', kind: 'issue', source_url: 'https://github.com/angular/angular/issues/1',
      text: '<script>alert(1)</script>', updated_at: null, truncated: false}],
    steps: [{instruction: 'Read the issue', evidence_ids: ['issue']}], warnings: ['Limited sample'],
  };

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
  const readiness: RepositoryReadiness = {
    repository_full_name: 'angular/angular',
    repository_html_url: 'https://github.com/angular/angular',
    evaluated_at: '2026-09-01T00:00:00Z',
    overall_score: 82,
    coverage_percentage: 100,
    confidence: 'high',
    formula_version: '1.0.0',
    dimensions: [
      {
        key: 'maintenance_activity',
        title: 'Maintenance activity',
        weight: 20,
        score: 100,
        confidence: 'high',
        sample_size: 1,
        observations: ['Last repository push was 5 days ago.'],
        evidence_urls: ['https://github.com/angular/angular'],
        warnings: [],
      },
    ],
    warnings: [],
  };
  const opportunities: OpportunityList = {
    repository_full_name: 'angular/angular',
    sample_size: 30,
    warning: null,
    opportunities: [
      {
        number: 1,
        title: 'Improve documentation',
        html_url: 'https://github.com/angular/angular/issues/1',
        labels: ['good first issue'],
        updated_at: '2026-09-01T00:00:00Z',
        fit_score: 100,
        reasons: ['Unassigned, so it is more likely to be available.'],
      },
    ],
  };

  beforeEach(async () => {
    previewCalls = [];
    briefResponse = new Subject<Investigation>();
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
            analyzeReadiness: () => of(readiness),
            findOpportunities: () => of(opportunities),
            investigate: () => briefResponse,
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
    expect(fixture.nativeElement.textContent).toContain('82/100');
    expect(fixture.nativeElement.textContent).toContain('Maintenance activity');
    expect(fixture.nativeElement.textContent).toContain('Improve documentation');
  });

  it('prevents native browser navigation when the form is submitted', () => {
    fixture.componentInstance.repositoryUrl.setValue('https://github.com/angular/angular');
    const form = fixture.nativeElement.querySelector('form') as HTMLFormElement;
    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });

    const wasNotCancelled = form.dispatchEvent(submitEvent);

    expect(wasNotCancelled).toBe(false);
    expect(submitEvent.defaultPrevented).toBe(true);
    expect(previewCalls).toEqual(['https://github.com/angular/angular']);
  });
  it('renders investigation evidence as text with source links', () => {
    fixture.componentInstance.repositoryUrl.setValue('https://github.com/angular/angular');
    fixture.componentInstance.submit();
    fixture.componentInstance.investigate(1);
    briefResponse.next(brief);
    briefResponse.complete();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Investigation: #1');
    expect(fixture.nativeElement.textContent).toContain('<script>alert(1)</script>');
    expect(fixture.nativeElement.querySelector('script')).toBeNull();
    expect(fixture.nativeElement.textContent).toContain('Limited sample');
  });

  it('ignores an old investigation response after another repository submission', () => {
    fixture.componentInstance.repositoryUrl.setValue('https://github.com/angular/angular');
    fixture.componentInstance.submit();
    fixture.componentInstance.investigate(1);
    fixture.componentInstance.submit();
    briefResponse.next(brief);
    briefResponse.complete();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).not.toContain('Investigation: #1');
  });
});

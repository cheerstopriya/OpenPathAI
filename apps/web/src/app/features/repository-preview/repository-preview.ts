import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin, timeout } from 'rxjs';

import {
  RepositoryApiService,
  Investigation,
  OpportunityList,
  RepositoryPreview,
  RepositoryReadiness,
} from '../../core/api/repository-api.service';

type PreviewState = 'idle' | 'loading' | 'success' | 'error';

@Component({
  imports: [ReactiveFormsModule],
  selector: 'app-repository-preview',
  styleUrl: './repository-preview.scss',
  templateUrl: './repository-preview.html',
})
export class RepositoryPreviewComponent {
  private readonly repositoryApi = inject(RepositoryApiService);

  readonly repositoryUrl = new FormControl('', {
    nonNullable: true,
    validators: [
      Validators.required,
      Validators.maxLength(300),
      Validators.pattern(/^https:\/\/github\.com\/[A-Za-z0-9-]+\/[A-Za-z0-9._-]+(?:\.git)?\/?$/),
    ],
  });
  protected readonly state = signal<PreviewState>('idle');
  protected readonly repository = signal<RepositoryPreview | null>(null);
  protected readonly readiness = signal<RepositoryReadiness | null>(null);
  protected readonly opportunities = signal<OpportunityList | null>(null);
  protected readonly investigation = signal<Investigation | null>(null);
  protected readonly investigationLoading = signal(false);
  protected readonly investigationError = signal('');
  private requestVersion = 0;

  investigate(issueNumber: number): void {
    const repository = this.repository();
    if (!repository || this.investigationLoading()) return;
    const version = ++this.requestVersion;
    this.investigation.set(null);
    this.investigationError.set('');
    this.investigationLoading.set(true);
    this.repositoryApi.investigate(repository.html_url, issueNumber).pipe(timeout(20_000)).subscribe({
      next: brief => {
        if (version !== this.requestVersion) return;
        this.investigation.set(brief);
        this.investigationLoading.set(false);
      },
      error: (error: unknown) => {
        if (version !== this.requestVersion) return;
        this.investigationError.set(this.toSafeMessage(error));
        this.investigationLoading.set(false);
      },
    });
  }

  protected readonly errorMessage = signal('');

  submit(event?: Event): void {
    event?.preventDefault();
    this.repositoryUrl.markAsTouched();
    if (this.repositoryUrl.invalid || this.state() === 'loading') {
      return;
    }

    this.requestVersion++;
    this.investigation.set(null);
    this.investigationLoading.set(false);
    this.investigationError.set('');
    this.state.set('loading');
    this.repository.set(null);
    this.readiness.set(null);
    this.opportunities.set(null);
    this.errorMessage.set('');

    const repositoryUrl = this.repositoryUrl.value.trim();
    forkJoin({
      repository: this.repositoryApi.preview(repositoryUrl),
      readiness: this.repositoryApi.analyzeReadiness(repositoryUrl),
      opportunities: this.repositoryApi.findOpportunities(repositoryUrl),
    })
      .pipe(timeout(20_000))
      .subscribe({
        next: ({ repository, readiness, opportunities }) => {
          this.repository.set(repository);
          this.readiness.set(readiness);
          this.opportunities.set(opportunities);
          this.state.set('success');
        },
        error: (error: unknown) => {
          this.errorMessage.set(this.toSafeMessage(error));
          this.state.set('error');
        },
      });
  }

  private toSafeMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      if (error.status === 404) {
        return 'That repository was not found or is not publicly accessible.';
      }
      if (error.status === 422) {
        return 'Enter a public repository URL such as https://github.com/angular/angular.';
      }
      if (error.status === 429) {
        return 'GitHub’s request limit has been reached. Please try again later.';
      }
    }

    return 'The repository could not be loaded. Please try again.';
  }
}

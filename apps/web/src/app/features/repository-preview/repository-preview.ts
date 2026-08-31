import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { timeout } from 'rxjs';

import { RepositoryApiService, RepositoryPreview } from '../../core/api/repository-api.service';

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
  protected readonly errorMessage = signal('');

  submit(): void {
    this.repositoryUrl.markAsTouched();
    if (this.repositoryUrl.invalid || this.state() === 'loading') {
      return;
    }

    this.state.set('loading');
    this.repository.set(null);
    this.errorMessage.set('');

    this.repositoryApi
      .preview(this.repositoryUrl.value.trim())
      .pipe(timeout(10_000))
      .subscribe({
        next: (repository) => {
          this.repository.set(repository);
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

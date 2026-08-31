import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface RepositoryPreview {
  owner: string;
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  primary_language: string | null;
  stars: number;
  forks: number;
  default_branch: string;
  archived: boolean;
  disabled: boolean;
  visibility: string;
  topics: string[];
  license_spdx: string | null;
  pushed_at: string | null;
}

@Injectable({ providedIn: 'root' })
export class RepositoryApiService {
  private readonly http = inject(HttpClient);

  preview(repositoryUrl: string): Observable<RepositoryPreview> {
    return this.http.post<RepositoryPreview>('/api/v1/repositories/preview', {
      repository_url: repositoryUrl,
    });
  }
}

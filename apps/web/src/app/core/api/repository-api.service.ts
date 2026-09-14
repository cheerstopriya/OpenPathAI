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

export type ReadinessConfidence = 'low' | 'medium' | 'high';

export interface ReadinessDimension {
  key: string;
  title: string;
  weight: number;
  score: number | null;
  confidence: ReadinessConfidence;
  sample_size: number;
  observations: string[];
  evidence_urls: string[];
  warnings: string[];
}

export interface RepositoryReadiness {
  repository_full_name: string;
  repository_html_url: string;
  evaluated_at: string;
  overall_score: number | null;
  coverage_percentage: number;
  confidence: ReadinessConfidence;
  formula_version: string;
  dimensions: ReadinessDimension[];
  warnings: string[];
}

@Injectable({ providedIn: 'root' })
export class RepositoryApiService {
  private readonly http = inject(HttpClient);

  preview(repositoryUrl: string): Observable<RepositoryPreview> {
    return this.http.post<RepositoryPreview>('/api/v1/repositories/preview', {
      repository_url: repositoryUrl,
    });
  }

  analyzeReadiness(repositoryUrl: string): Observable<RepositoryReadiness> {
    return this.http.post<RepositoryReadiness>('/api/v1/repositories/readiness', {
      repository_url: repositoryUrl,
    });
  }
}

# OpenPath AI

OpenPath AI helps a developer evaluate an open-source GitHub repository, find a suitable contribution issue, and create an evidence-grounded contribution plan.

## Current status

The FastAPI application foundation, health endpoint, and Angular connection-status page are implemented.

Phase 2 adds a secure public GitHub repository preview. The browser sends a repository URL to FastAPI; FastAPI validates it, calls only `api.github.com`, and returns a small typed response.

Phase 3 adds a transparent contribution-readiness analysis. It collects a bounded sample of public repository evidence and scores six dimensions with deterministic Python rules. Every result includes its sample size, confidence, observations, warnings, and supporting GitHub links. An LLM does not calculate or alter these scores.

## Backend quick start

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend in editable mode:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".\apps\api"
```

Run the API:

```powershell
python -m uvicorn openpath_api.main:app --app-dir .\apps\api\src --reload
```

Open:

- API health: <http://127.0.0.1:8000/api/v1/health>
- Interactive API documentation: <http://127.0.0.1:8000/docs>

Repository endpoints:

- `POST /api/v1/repositories/preview` returns validated repository metadata.
- `POST /api/v1/repositories/readiness` returns contribution-readiness evidence and scores.

Example request body:

```json
{
  "repository_url": "https://github.com/angular/angular"
}
```

Run tests:

```powershell
python -m unittest discover -s .\apps\api\tests -p "test_*.py" -v
```

## Frontend quick start

Start FastAPI first, then open a second PowerShell terminal:

```powershell
Set-Location .\apps\web
npm.cmd start
```

Open <http://localhost:4200>. Angular calls `/api/v1/health`; the development proxy forwards that request to FastAPI on port 8000.

Enter a URL such as `https://github.com/cheerstopriya/OpenPathAI` to exercise the preview and readiness-analysis flow.

Run frontend checks:

```powershell
Set-Location .\apps\web
npm.cmd test -- --watch=false
npm.cmd run build
```

## Request flow

```text
HTTP GET /api/v1/health
  -> health router
  -> health service
  -> HealthResponse schema
  -> JSON response
```

The separation is intentional: the router handles HTTP, the service owns application logic, and the schema defines the public contract.

The Phase 3 flow is:

```text
Angular repository form
  -> POST /api/v1/repositories/readiness
  -> strict github.com repository URL parser
  -> bounded GitHub REST adapter calls
  -> evidence collection and PR/issue normalization
  -> deterministic scoring formula v1.0.0
  -> typed JSON with scores, confidence, warnings, and evidence links
  -> Angular readiness cards
```

## Readiness formula v1.0.0

The overall score is a weighted assessment of contribution readiness, not a claim about repository quality:

| Dimension                   | Weight | Evidence used                                                                         |
| --------------------------- | -----: | ------------------------------------------------------------------------------------- |
| Maintenance activity        |    20% | Days since the latest repository push                                                 |
| Newcomer documentation      |    20% | README, contributing guide, license, code of conduct, issue template, and PR template |
| Review responsiveness       |    20% | Median time to first submitted review in sampled PRs                                  |
| Contribution outcomes       |    15% | Merge ratio among sampled closed PRs                                                  |
| Beginner issue availability |    15% | Unassigned open issues carrying recognized beginner labels                            |
| Community participation     |    10% | Distinct PR authors and reviewers in the sample                                       |

Missing evidence is represented as unavailable rather than zero. The response reports evidence coverage and re-normalizes only the available dimension weights. Low sample sizes reduce confidence and produce explicit warnings.

## Retrieval and security boundaries

- Only canonical `https://github.com/{owner}/{repository}` URLs are accepted.
- The backend uses a fixed `https://api.github.com` base URL and does not follow redirects.
- Analysis is read-only and never posts an issue comment or modifies a repository.
- Each analysis samples at most 10 pull requests, 20 reviews per sampled PR, and 30 open issue results.
- GitHub responses are validated into small DTOs before reaching domain logic.
- A GitHub token is optional and must be supplied through an untracked `.env` file.

The sample is intentionally bounded, so a score should be read together with its confidence, coverage, and observations. It does not prove how many people are currently working on a repository.


## Issue investigation

Select **Investigate issue** on an opportunity card. OpenPath collects the issue
description, author, labels, up to ten comments and repository guidance links,
then presents source-linked investigation steps. Expand each evidence item to
inspect its text and open the original source. Collection time, truncation and
missing-evidence warnings are visible; this is a sampled snapshot, not live truth.

`POST /api/v1/repositories/investigation` accepts:

```json
{"repository_url": "https://github.com/owner/repository", "issue_number": 1}
```

This phase is deterministic evidence collection and planning. It does not claim
LLM generation, source-code diagnosis or measured RAG improvements. Read the
[implementation evidence map](docs/resume-claims.md) before using project claims.
Repository text is displayed as escaped text and is never executed as instructions.

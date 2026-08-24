# OpenPath AI web application

This Angular application is the browser interface for OpenPath AI.

## Phase 1 request flow

```text
App component
  -> HealthApiService
  -> GET /api/v1/health
  -> Angular development proxy
  -> FastAPI on http://127.0.0.1:8000
```

The component owns visual state. The API service owns HTTP communication. `proxy.conf.json` is used only by the local Angular development server; production routing will be configured at deployment time.

## Commands

```powershell
npm.cmd start
npm.cmd test -- --watch=false
npm.cmd run build
```


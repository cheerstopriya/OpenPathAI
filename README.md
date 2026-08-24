# OpenPath AI

OpenPath AI helps a developer evaluate an open-source GitHub repository, find a suitable contribution issue, and create an evidence-grounded contribution plan.

## Phase 1 status

The FastAPI application foundation, health endpoint, and Angular connection-status page are implemented.

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

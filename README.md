# Full Stack FastAPI + Frontend Project

## Development

### 1. Backend (FastAPI)
- Create and activate a virtual environment:
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```
- Run the backend (from project root):
  ```sh
  uvicorn espresso_engine.main_cafe_server:app --reload
  ```
- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend (Vite/React or similar)
- Go to your frontend directory (e.g., `café-ui/first-sip-station`):
  ```sh
  npm install
  npm run dev
  ```
- The dev server will show a local URL (e.g., [http://localhost:5173](http://localhost:5173)).

---

## Production Build & Deployment

### 1. Build Frontend for Production
- In your frontend directory:
  ```sh
  npm run build
  ```
- This creates a `dist` (or `build`) folder with static files.

### 2. Prepare Backend for Production
- Copy the contents of the frontend `dist` folder to a static folder your backend or IIS will serve (e.g., `café-ui/` or `espresso_engine/static/`).
- Ensure all backend code, static files, and `requirements.txt` are in your deployable folder.

### 3. Deploy to IIS (Windows)
- Install IIS and CGI:
  ```powershell
  Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole -All
  Enable-WindowsOptionalFeature -Online -FeatureName IIS-CGI -All
  ```
- Install Python and dependencies on the server:
  ```sh
  pip install -r requirements.txt
  pip install wfastcgi
  ```
- Place your backend code, static files, and `web.config` in your IIS site directory.
- Edit `web.config` to point to your Python and wfastcgi paths, and set the correct `WSGI_HANDLER`.
- In IIS Manager, create a new site or point an existing site to your deploy folder.
- Set permissions so IIS can access your files.

---

## Quick Reference

| Task                | Command/Action                                                      |
|---------------------|---------------------------------------------------------------------|
| Backend dev         | `uvicorn espresso_engine.main_cafe_server:app --reload`             |
| Frontend dev        | `npm run dev` (in frontend folder)                                  |
| Build frontend      | `npm run build` (in frontend folder)                                |
| Backend prod (IIS)  | Use `web.config` + wfastcgi + IIS                                  |
| Backend prod (Linux)| `gunicorn espresso_engine.main_cafe_server:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000` |

---

## Notes
- Make sure CORS is enabled in FastAPI for frontend-backend communication.
- For IIS, static files can be served directly by IIS or by FastAPI.
- Always test your APIs and frontend after deployment.
# User Service

Handles user registration and management.

## Setup

1. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

2. **Run the service**:
   ```sh
   uvicorn routers.register:app --reload
   ```

3. **Access the API docs**:
   Open your browser and go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   to view and test the API endpoints.

## Testing

- Make sure your server is running before running tests that use the `requests` library.
- To run pytest-based tests:
  ```sh
  pytest
  ```
- To generate a JUnit XML report:
  ```sh
  pytest --junitxml=report.xml
  ```
- To generate a simple text report:
  ```sh
  pytest -v > report.txt
  ```
- If you see import errors, ensure you have installed all dependencies:
  ```sh
  pip install -r requirements.txt
  pip install pytest requests httpx
  ```

## Docker & Docker Compose

1. **Install Docker Desktop** ([download here](https://www.docker.com/products/docker-desktop/)) and ensure it is running (Linux containers mode).
2. **Build and start all services:**
   ```sh
   docker-compose up --build
   ```
   - This builds the FastAPI app image, starts the app (API + UI), and runs tests in a separate container.
3. **Access the app:**
   - API: [http://localhost:8000/register](http://localhost:8000/register)
   - UI:  [http://localhost:8000/ui/register.html](http://localhost:8000/ui/register.html)
4. **Stop all services:**
   ```sh
   docker-compose down
   ```
5. **View logs:**
   ```sh
   docker-compose logs app
   docker-compose logs test
   ```

## GitHub Actions (CI) & Local CI with act

- CI is automated via `.github/workflows/python-app.yml`.
- To run GitHub Actions locally:
  1. Install [`act`](https://github.com/nektos/act#installation) (e.g., `scoop install act` on Windows).
  2. Start Docker Desktop.
  3. Run:
     ```sh
     act
     ```
  - This will execute your GitHub Actions workflow locally using Docker.
  - If your workflow starts a server and runs tests, ensure the server is fully started before tests run. (The workflow uses sleep/wait logic for reliability.)

## UI
- The `ui` folder contains static assets for the registration page.
- You can add more static files (CSS, images, etc.) to this folder.
- Access the registration page at `/ui/register.html`.

## Test Scenarios
- Password policy and registration test cases are implemented in `tests/basic_requests_test.py`.
- To run all tests:
  ```sh
  pytest
  ```

## Troubleshooting
- If tests fail due to connection errors, ensure the app is healthy before tests run. The compose file uses healthchecks and wait logic.
- If you change code, re-run with `--build` to rebuild the image.
- For import errors, ensure all dependencies are installed.

---

For more details, see `run_docker_and_compose.txt` and `run_github_actions_locally.txt`.

## Notes
- The registration API uses in-memory storage, so data is lost when the server restarts.
- The API expects a JSON payload with `username`, `email`, and `password` fields.
- For Pydantic v2+, the code uses `model_dump()` instead of `dict()` for serialization.

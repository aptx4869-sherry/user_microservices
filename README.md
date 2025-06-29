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

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

## Notes
- The registration API uses in-memory storage, so data is lost when the server restarts.
- The API expects a JSON payload with `username`, `email`, and `password` fields.
- For Pydantic v2+, the code uses `model_dump()` instead of `dict()` for serialization.

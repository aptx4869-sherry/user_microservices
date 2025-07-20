from fastapi.responses import FileResponse
from pathlib import Path

# Import the shared router instance
from config.cafe_config import router

@router.get("/", include_in_schema=False)
async def serve_frontend():
    """Serves the main frontend HTML file."""
    file_path = Path(__file__).parent.parent.parent / "café-ui" / "index.html"
    if not file_path.is_file():
        return {"message": "Frontend index.html not found. Ensure it's in the 'frontend' directory."}
    return FileResponse(file_path)
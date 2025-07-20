# backend/main_cafe_server.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Import your routers
from routes import cafe_auth_routes
from routes import cafe_frontend_route
from routes import cafe_user_routes
from routes import token_manager

# Import the limiter from config
from config.cafe_config import limiter

# Create the FastAPI application instance
app = FastAPI(
    title="Coding Café Backend",
    description="API for the Coding Café application, handling user authentication and more.",
    version="1.0.0",
)

# --- Middleware ---

# CORS Middleware (Crucial for frontend-backend communication)
# Adjust origins to your frontend's URL in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Set this to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
app.state.limiter = limiter # Required by SlowAPI
app.add_middleware(SlowAPIMiddleware)

# --- Exception Handlers ---
# Add the default rate limit exception handler (optional, your custom one below will override)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom Rate Limit Exception Handler
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors, providing a themed message."""
    return JSONResponse(
        status_code=429,
        content={"detail": "☕ Whoa, slow down! You're sipping too fast. Try again in a minute."}
    )

# --- Include Routers ---
# Include the authentication routes
app.include_router(cafe_auth_routes.router, tags=["Authentication"])

# Include the user management routes
app.include_router(cafe_user_routes.router, prefix="/users", tags=["Users"])

app.include_router(token_manager.router)

# Include the frontend serving route (usually at the root)
app.include_router(cafe_frontend_route.router)

# Example root endpoint (optional)
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is brewing!"}
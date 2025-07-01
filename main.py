# Entry point for register service
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from routers import register
from routers import view_users

# Shared in-memory store
users = []

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.include_router(register.router)
app.include_router(view_users.router)

app.state.limiter = limiter
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "☕ Whoa, slow down! You're sipping too fast. Try again in a minute."}
    )

# Inject shared store into both routers
register.users = users
view_users.users = users
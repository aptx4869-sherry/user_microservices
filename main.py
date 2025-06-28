# Entry point for register service
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers import register
from routers import view_users

# Shared in-memory store
users = []

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.include_router(register.router)
app.include_router(view_users.router)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Inject shared store into both routers
register.users = users
view_users.users = users
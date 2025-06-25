# Entry point for register service
from fastapi import FastAPI
from user_service.routers import register


app = FastAPI()
app.include_router(register.router)


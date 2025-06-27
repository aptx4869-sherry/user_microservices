# Entry point for register service
from fastapi import FastAPI
from routers import register


app = FastAPI()
app.include_router(register.router)
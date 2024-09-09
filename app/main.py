# app/main.py

from fastapi import FastAPI
from app.api.v1.routes import router as movie_router

app = FastAPI()

app.include_router(movie_router, prefix="/api/v1")
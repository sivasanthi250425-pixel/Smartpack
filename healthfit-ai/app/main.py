import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import init_db
from app.routes import health, assistant

app = FastAPI(title="SmartPack HealthFit & AI Guidance", version="1.0.0")
app.add_middleware(CORSMiddleware,
                   allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
                   allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/")
def root():
    return {"service": "healthfit-ai", "status": "ok"}


app.include_router(health.router)
app.include_router(assistant.router)

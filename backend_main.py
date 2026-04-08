from fastapi import FastAPI
from sqlalchemy import create_engine

app = FastAPI(title="VisitaLab API")

@app.get("/")
def root():
    return {"status": "ok"}

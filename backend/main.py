from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
from database import engine, get_db
import crud, schemas
from routers import cases, blocklist, export

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FraudWatch API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(blocklist.router)
app.include_router(export.router)


@app.get("/api/dashboard/kpis", response_model=schemas.KPIOut, tags=["dashboard"])
def dashboard_kpis(
    filter: str = Query("all", pattern="^(all|week|month)$"),
    db: Session = Depends(get_db),
):
    return crud.get_kpis(db, filter)


@app.get("/api/dashboard/charts", response_model=schemas.ChartsOut, tags=["dashboard"])
def dashboard_charts(
    filter: str = Query("all", pattern="^(all|week|month)$"),
    db: Session = Depends(get_db),
):
    return crud.get_charts(db, filter)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "FraudWatch API"}

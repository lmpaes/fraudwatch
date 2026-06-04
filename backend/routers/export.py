import csv
import io
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
import crud
from database import get_db

router = APIRouter(prefix="/api/export", tags=["export"])


def _cases_to_rows(cases):
    rows = []
    for c in cases:
        rows.append({
            "id": c.id,
            "name": c.name,
            "suspicion": c.suspicion,
            "hours": c.hours,
            "transport": c.transport.value,
            "value": float(c.value),
            "score": c.score,
            "status": c.status.value,
            "date": str(c.date),
            "justification": c.justification or "",
        })
    return rows


def _blocklist_to_rows(entries):
    rows = []
    for e in entries:
        rows.append({
            "id": e.id,
            "name": e.name,
            "initials": e.initials,
            "dob": str(e.dob),
            "reasons": " | ".join(r.reason for r in e.reasons),
            "created_at": str(e.created_at),
        })
    return rows


@router.get("/cases/csv")
def export_cases_csv(db: Session = Depends(get_db)):
    cases = crud.get_cases(db)
    rows = _cases_to_rows(cases)
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cases.csv"},
    )


@router.get("/cases/json")
def export_cases_json(db: Session = Depends(get_db)):
    cases = crud.get_cases(db)
    return JSONResponse(content=_cases_to_rows(cases))


@router.get("/blocklist/csv")
def export_blocklist_csv(db: Session = Depends(get_db)):
    entries = crud.get_blocklist(db)
    rows = _blocklist_to_rows(entries)
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=blocklist.csv"},
    )


@router.get("/blocklist/json")
def export_blocklist_json(db: Session = Depends(get_db)):
    entries = crud.get_blocklist(db)
    return JSONResponse(content=_blocklist_to_rows(entries))

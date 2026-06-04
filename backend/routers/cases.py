from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("", response_model=List[schemas.CaseListOut])
def list_cases(
    filter: str = Query("all", pattern="^(all|week|month)$"),
    db: Session = Depends(get_db),
):
    return crud.get_cases(db, filter)


@router.get("/{case_id}", response_model=schemas.CaseOut)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    return case


@router.post("", response_model=schemas.CaseOut, status_code=201)
def create_case(data: schemas.CaseCreate, db: Session = Depends(get_db)):
    return crud.create_case(db, data)


@router.put("/{case_id}", response_model=schemas.CaseOut)
def update_case(case_id: int, data: schemas.CaseUpdate, db: Session = Depends(get_db)):
    case = crud.update_case(db, case_id, data)
    if not case:
        raise HTTPException(404, "Case not found")
    return case


@router.patch("/{case_id}/status", response_model=schemas.CaseOut)
def patch_status(case_id: int, data: schemas.CaseStatusUpdate, db: Session = Depends(get_db)):
    case = crud.patch_case_status(db, case_id, data.status)
    if not case:
        raise HTTPException(404, "Case not found")
    return case


@router.delete("/{case_id}", status_code=204)
def delete_case(case_id: int, db: Session = Depends(get_db)):
    if not crud.delete_case(db, case_id):
        raise HTTPException(404, "Case not found")

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(prefix="/api/blocklist", tags=["blocklist"])


@router.get("", response_model=List[schemas.BlocklistOut])
def list_blocklist(db: Session = Depends(get_db)):
    return crud.get_blocklist(db)


@router.get("/{entry_id}", response_model=schemas.BlocklistOut)
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = crud.get_blocklist_entry(db, entry_id)
    if not entry:
        raise HTTPException(404, "Entry not found")
    return entry


@router.post("", response_model=schemas.BlocklistOut, status_code=201)
def create_entry(data: schemas.BlocklistCreate, db: Session = Depends(get_db)):
    return crud.create_blocklist_entry(db, data)


@router.put("/{entry_id}", response_model=schemas.BlocklistOut)
def update_entry(entry_id: int, data: schemas.BlocklistUpdate, db: Session = Depends(get_db)):
    entry = crud.update_blocklist_entry(db, entry_id, data)
    if not entry:
        raise HTTPException(404, "Entry not found")
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    if not crud.delete_blocklist_entry(db, entry_id):
        raise HTTPException(404, "Entry not found")

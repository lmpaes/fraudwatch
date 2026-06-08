from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
from models import TransportEnum, StatusEnum

_Date = date  # alias para evitar conflito de nome em CaseUpdate (campo 'date: Optional[date]'
              # cria atributo de classe date=None, que sombrearia datetime.date no Pydantic v2)


# ── CaseHistory ──────────────────────────────────────────────

class CaseHistoryBase(BaseModel):
    d: date
    t: str


class CaseHistoryCreate(CaseHistoryBase):
    pass


class CaseHistoryOut(CaseHistoryBase):
    id: int
    case_id: int

    model_config = {"from_attributes": True}


# ── CaseFactor ───────────────────────────────────────────────

class CaseFactorBase(BaseModel):
    blocklist: int = 0
    reincidencia: int = 0
    transporte: int = 0
    data: int = 0


class CaseFactorCreate(CaseFactorBase):
    pass


class CaseFactorOut(CaseFactorBase):
    id: int
    case_id: int

    model_config = {"from_attributes": True}


# ── Case ─────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    name: str
    suspicion: str
    hours: float
    transport: TransportEnum
    value: float
    status: StatusEnum = StatusEnum.open
    date: date
    justification: Optional[str] = None
    factors: CaseFactorCreate
    history: List[CaseHistoryCreate] = []


class CaseUpdate(BaseModel):
    name: Optional[str] = None
    suspicion: Optional[str] = None
    hours: Optional[float] = None
    transport: Optional[TransportEnum] = None
    value: Optional[float] = None
    status: Optional[StatusEnum] = None
    date: Optional[_Date] = None
    justification: Optional[str] = None
    factors: Optional[CaseFactorCreate] = None
    history: Optional[List[CaseHistoryCreate]] = None


class CaseStatusUpdate(BaseModel):
    status: StatusEnum


class CaseOut(BaseModel):
    id: int
    name: str
    initials: str
    col: str
    suspicion: str
    hours: float
    transport: TransportEnum
    value: float
    score: int
    status: StatusEnum
    date: date
    justification: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    factors: Optional[CaseFactorOut] = None
    history: List[CaseHistoryOut] = []

    model_config = {"from_attributes": True}


class CaseListOut(BaseModel):
    id: int
    name: str
    initials: str
    col: str
    suspicion: str
    hours: float
    transport: TransportEnum
    value: float
    score: int
    status: StatusEnum
    date: date

    model_config = {"from_attributes": True}


# ── Blocklist ────────────────────────────────────────────────

class BlocklistReasonCreate(BaseModel):
    reason: str


class BlocklistReasonOut(BaseModel):
    id: int
    reason: str

    model_config = {"from_attributes": True}


class BlocklistCreate(BaseModel):
    name: str
    dob: date
    reasons: List[str] = []


class BlocklistUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    reasons: Optional[List[str]] = None


class BlocklistOut(BaseModel):
    id: int
    name: str
    initials: str
    dob: date
    created_at: Optional[datetime]
    reasons: List[BlocklistReasonOut] = []

    model_config = {"from_attributes": True}


# ── Dashboard ────────────────────────────────────────────────

class KPIOut(BaseModel):
    total: int
    open: int
    denied: int
    released: int
    total_value: float
    saved_value: float
    saved_pct: float


class TransportDistOut(BaseModel):
    taxi: int
    road: int
    air: int


class RiskDistOut(BaseModel):
    low: int
    medium: int
    high: int


class AvgValueOut(BaseModel):
    taxi: float
    road: float
    air: float


class TimelinePoint(BaseModel):
    week: str
    count: int
    holiday: bool


class ChartsOut(BaseModel):
    transport: TransportDistOut
    risk: RiskDistOut
    avg_value: AvgValueOut
    timeline: List[TimelinePoint]

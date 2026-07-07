from datetime import date, timedelta
from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.orm import Session
import models, schemas
from services.score import (
    calculate_score, generate_initials, generate_color, is_in_blocklist
)


# ── Cases ─────────────────────────────────────────────────────

def _apply_filter(query, filter: str):
    today = date.today()
    if filter == "week":
        return query.filter(models.Case.date >= today - timedelta(days=6))
    if filter == "month":
        return query.filter(models.Case.date >= today - timedelta(days=29))
    return query


def get_cases(db: Session, filter: str = "all") -> List[models.Case]:
    q = db.query(models.Case).order_by(models.Case.date.desc())
    return _apply_filter(q, filter).all()


def get_case(db: Session, case_id: int) -> Optional[models.Case]:
    return db.query(models.Case).filter(models.Case.id == case_id).first()


def create_case(db: Session, data: schemas.CaseCreate) -> models.Case:
    in_bl = is_in_blocklist(db, data.name)
    score, computed_factors = calculate_score(
        db, data.name, data.transport.value, data.date, data.factors, in_bl
    )

    case = models.Case(
        name=data.name,
        initials=generate_initials(data.name),
        col=generate_color(),
        suspicion=data.suspicion,
        hours=data.hours,
        transport=data.transport,
        value=data.value,
        score=score,
        status=data.status,
        date=data.date,
        justification=data.justification,
    )
    db.add(case)
    db.flush()

    db.add(models.CaseFactor(case_id=case.id, **computed_factors))

    for h in data.history:
        db.add(models.CaseHistory(case_id=case.id, d=h.d, t=h.t))

    db.commit()
    db.refresh(case)
    return case


def update_case(db: Session, case_id: int, data: schemas.CaseUpdate) -> Optional[models.Case]:
    case = get_case(db, case_id)
    if not case:
        return None

    update_fields = data.model_dump(exclude_none=True, exclude={"factors", "history"})
    for k, v in update_fields.items():
        setattr(case, k, v)

    if data.factors is not None or data.transport is not None or data.date is not None:
        transport = data.transport.value if data.transport else case.transport.value
        case_date = data.date if data.date else case.date
        factors_input = data.factors if data.factors else schemas.CaseFactorCreate(
            blocklist=case.factors.blocklist if case.factors else 0,
            reincidencia=case.factors.reincidencia if case.factors else 0,
            transporte=case.factors.transporte if case.factors else 0,
            data=case.factors.data if case.factors else 0,
        )
        in_bl = is_in_blocklist(db, case.name)
        score, computed = calculate_score(db, case.name, transport, case_date, factors_input, in_bl)
        case.score = score

        if case.factors:
            for k, v in computed.items():
                setattr(case.factors, k, v)
        else:
            db.add(models.CaseFactor(case_id=case.id, **computed))

    if data.history is not None:
        db.query(models.CaseHistory).filter(models.CaseHistory.case_id == case_id).delete()
        for h in data.history:
            db.add(models.CaseHistory(case_id=case.id, d=h.d, t=h.t))

    db.commit()
    db.refresh(case)
    return case


def patch_case_status(db: Session, case_id: int, status: models.StatusEnum) -> Optional[models.Case]:
    case = get_case(db, case_id)
    if not case:
        return None
    case.status = status
    db.commit()
    db.refresh(case)
    return case


def delete_case(db: Session, case_id: int) -> bool:
    case = get_case(db, case_id)
    if not case:
        return False
    db.delete(case)
    db.commit()
    return True


# ── Blocklist ─────────────────────────────────────────────────

def get_blocklist(db: Session) -> List[models.Blocklist]:
    return db.query(models.Blocklist).order_by(models.Blocklist.created_at.desc()).all()


def get_blocklist_entry(db: Session, entry_id: int) -> Optional[models.Blocklist]:
    return db.query(models.Blocklist).filter(models.Blocklist.id == entry_id).first()


def create_blocklist_entry(db: Session, data: schemas.BlocklistCreate) -> models.Blocklist:
    from services.score import generate_initials, generate_color
    entry = models.Blocklist(
        name=data.name,
        initials=generate_initials(data.name),
        dob=data.dob,
    )
    db.add(entry)
    db.flush()
    for r in data.reasons:
        db.add(models.BlocklistReason(blocklist_id=entry.id, reason=r))
    db.commit()
    db.refresh(entry)
    return entry


def update_blocklist_entry(db: Session, entry_id: int, data: schemas.BlocklistUpdate) -> Optional[models.Blocklist]:
    entry = get_blocklist_entry(db, entry_id)
    if not entry:
        return None
    if data.name is not None:
        entry.name = data.name
        entry.initials = generate_initials(data.name)
    if data.dob is not None:
        entry.dob = data.dob
    if data.reasons is not None:
        db.query(models.BlocklistReason).filter(models.BlocklistReason.blocklist_id == entry_id).delete()
        for r in data.reasons:
            db.add(models.BlocklistReason(blocklist_id=entry.id, reason=r))
    db.commit()
    db.refresh(entry)
    return entry


def delete_blocklist_entry(db: Session, entry_id: int) -> bool:
    entry = get_blocklist_entry(db, entry_id)
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True


# ── Dashboard ─────────────────────────────────────────────────

def get_kpis(db: Session, filter: str = "all") -> dict:
    cases = get_cases(db, filter)
    total = len(cases)
    open_ = sum(1 for c in cases if c.status.value == "open")
    denied = sum(1 for c in cases if c.status.value == "denied")
    released = sum(1 for c in cases if c.status.value == "released")
    total_value = sum(float(c.value) for c in cases)
    saved_value = sum(float(c.value) for c in cases if c.status.value == "denied")
    return {
        "total": total,
        "open": open_,
        "denied": denied,
        "released": released,
        "total_value": round(total_value, 2),
        "saved_value": round(saved_value, 2),
        "saved_pct": round(saved_value / total_value * 100, 1) if total_value else 0.0,
    }


def get_charts(db: Session, filter: str = "all") -> dict:
    cases = get_cases(db, filter)

    road = sum(1 for c in cases if c.transport.value == "road")
    maritime = sum(1 for c in cases if c.transport.value == "maritime")
    air = sum(1 for c in cases if c.transport.value == "air")

    low = sum(1 for c in cases if c.score <= 25)
    medium = sum(1 for c in cases if 26 <= c.score <= 55)
    high = sum(1 for c in cases if c.score >= 56)

    def avg(t: str) -> float:
        vals = [float(c.value) for c in cases if c.transport.value == t]
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    # Timeline: janela e granularidade adaptam-se ao filtro ativo
    from datetime import date, timedelta
    today = date.today()
    NATIONAL_HOLIDAYS = {
        (1, 1), (4, 21), (5, 1), (9, 7), (10, 12),
        (11, 2), (11, 15), (12, 25), (4, 18), (4, 19),
        (4, 3), (4, 5),
    }

    timeline = []

    if filter == "week":
        # Últimos 7 dias → 1 ponto por dia
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = sum(1 for c in cases if c.date == day)
            has_holiday = (day.month, day.day) in NATIONAL_HOLIDAYS
            timeline.append({"week": day.strftime("%d/%m"), "count": count, "holiday": has_holiday})

    elif filter == "month":
        # Últimos 30 dias → buckets de 7 dias a partir de hoje-29
        bucket = today - timedelta(days=29)
        while bucket <= today:
            bucket_end = bucket + timedelta(days=6)
            count = sum(1 for c in cases if bucket <= c.date <= bucket_end)
            has_holiday = any(
                (check.month, check.day) in NATIONAL_HOLIDAYS
                for j in range(7)
                for check in [bucket + timedelta(days=j)]
            )
            timeline.append({"week": bucket.strftime("%d/%m"), "count": count, "holiday": has_holiday})
            bucket += timedelta(days=7)

    else:
        # Todos os casos → janela rolante de 45 dias, buckets de 7 dias
        bucket = today - timedelta(days=45)
        while bucket <= today:
            bucket_end = bucket + timedelta(days=6)
            count = sum(1 for c in cases if bucket <= c.date <= bucket_end)
            has_holiday = any(
                (check.month, check.day) in NATIONAL_HOLIDAYS
                for j in range(7)
                for check in [bucket + timedelta(days=j)]
            )
            timeline.append({"week": bucket.strftime("%d/%m"), "count": count, "holiday": has_holiday})
            bucket += timedelta(days=7)

    return {
        "transport": {"road": road, "maritime": maritime, "air": air},
        "risk": {"low": low, "medium": medium, "high": high},
        "avg_value": {"road": avg("road"), "maritime": avg("maritime"), "air": avg("air")},
        "timeline": timeline,
    }

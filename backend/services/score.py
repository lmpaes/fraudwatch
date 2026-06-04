import random
from datetime import date
from sqlalchemy.orm import Session
import models

AVATAR_COLORS = [
    "#F87171", "#60A5FA", "#A78BFA", "#4ADE80", "#FB923C",
    "#38BDF8", "#C084FC", "#E879F9", "#FBBF24", "#34D399",
    "#A3E635", "#F472B6", "#2DD4BF", "#818CF8", "#FCA5A5",
]

NATIONAL_HOLIDAYS = {
    (1, 1), (4, 21), (5, 1), (9, 7), (10, 12),
    (11, 2), (11, 15), (12, 25),
    # Semana Santa / Carnaval approximation
    (4, 18), (4, 19), (3, 4), (3, 5),
    # 2026 specific
    (4, 3), (4, 5),
}


def _is_near_holiday(d: date) -> bool:
    for delta in range(-3, 4):
        from datetime import timedelta
        check = d + timedelta(days=delta)
        if (check.month, check.day) in NATIONAL_HOLIDAYS:
            return True
    return False


def generate_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def generate_color() -> str:
    return random.choice(AVATAR_COLORS)


def calculate_score(
    db: Session,
    name: str,
    transport: str,
    case_date: date,
    factors_input,
    is_blocklist: bool,
) -> tuple[int, dict]:
    bl_pts = 45 if is_blocklist else min(int(factors_input.blocklist), 45)
    re_pts = min(int(factors_input.reincidencia), 25)
    tr_pts = {"air": 20, "road": 10, "taxi": 0}.get(transport, 0)
    dt_pts = 10 if _is_near_holiday(case_date) else min(int(factors_input.data), 10)

    score = min(bl_pts + re_pts + tr_pts + dt_pts, 100)
    return score, {
        "blocklist": bl_pts,
        "reincidencia": re_pts,
        "transporte": tr_pts,
        "data": dt_pts,
    }


def is_in_blocklist(db: Session, name: str) -> bool:
    return (
        db.query(models.Blocklist)
        .filter(models.Blocklist.name.ilike(name.strip()))
        .first()
        is not None
    )

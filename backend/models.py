import enum
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Numeric, Text, Date, DateTime,
    Enum, ForeignKey, func
)
from sqlalchemy.orm import relationship
from database import Base


class TransportEnum(str, enum.Enum):
    road = "road"
    maritime = "maritime"
    air = "air"


class StatusEnum(str, enum.Enum):
    open = "open"
    denied = "denied"
    released = "released"


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    initials = Column(String(5), nullable=False)
    col = Column(String(10), nullable=False)
    suspicion = Column(Text, nullable=False)
    hours = Column(Float, nullable=False)
    transport = Column(Enum(TransportEnum), nullable=False)
    value = Column(Numeric(10, 2), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.open)
    date = Column(Date, nullable=False)
    justification = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    factors = relationship("CaseFactor", back_populates="case", uselist=False, cascade="all, delete-orphan")
    history = relationship("CaseHistory", back_populates="case", cascade="all, delete-orphan", order_by="CaseHistory.d.desc()")


class CaseFactor(Base):
    __tablename__ = "case_factors"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, unique=True)
    blocklist = Column(Integer, default=0)
    reincidencia = Column(Integer, default=0)
    transporte = Column(Integer, default=0)
    data = Column(Integer, default=0)

    case = relationship("Case", back_populates="factors")


class CaseHistory(Base):
    __tablename__ = "case_history"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    d = Column(Date, nullable=False)
    t = Column(Text, nullable=False)

    case = relationship("Case", back_populates="history")


class Blocklist(Base):
    __tablename__ = "blocklist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    initials = Column(String(5), nullable=False)
    dob = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    reasons = relationship("BlocklistReason", back_populates="blocklist_entry", cascade="all, delete-orphan")


class BlocklistReason(Base):
    __tablename__ = "blocklist_reasons"

    id = Column(Integer, primary_key=True, index=True)
    blocklist_id = Column(Integer, ForeignKey("blocklist.id"), nullable=False)
    reason = Column(Text, nullable=False)

    blocklist_entry = relationship("Blocklist", back_populates="reasons")

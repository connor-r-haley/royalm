from __future__ import annotations

import os
import uuid as _uuid
from datetime import date
from typing import Generator, Optional, List

from sqlalchemy import (
    String,
    Integer,
    Float,
    Date,
    ForeignKey,
    create_engine,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


class Country(Base):
    __tablename__ = "ref_countries"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)  # ISO-3
    name: Mapped[str] = mapped_column(String(128))
    iso2: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    continent: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    capital: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    population: Mapped[int] = mapped_column(Integer)
    gdp_usd_billion: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gov_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    leaders: Mapped[List["Leader"]] = relationship(back_populates="country")


Index("ix_ref_countries_continent", Country.continent)


class Leader(Base):
    __tablename__ = "ref_leaders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID4 string
    country_code: Mapped[str] = mapped_column(String(3), ForeignKey("ref_countries.code"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(128), index=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    ideology: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    approval: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    country: Mapped["Country"] = relationship(back_populates="leaders")


def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



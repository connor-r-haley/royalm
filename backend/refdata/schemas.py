from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CountryRead(BaseModel):
    code: str
    name: str
    iso2: Optional[str] = None
    continent: Optional[str] = None
    capital: Optional[str] = None
    population: int
    gdp_usd_billion: Optional[float] = None
    gov_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LeaderRead(BaseModel):
    id: str
    country_code: str
    name: str
    title: str
    start_date: Optional[date] = None
    ideology: Optional[str] = None
    approval: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)



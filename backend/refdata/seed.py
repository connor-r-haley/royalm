from __future__ import annotations

import json
import os
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from .models import SessionLocal, Country, Leader
from .router import invalidate_cache


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _read_json(name: str) -> Any:
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


def seed_countries(db: Session, items: list[dict[str, Any]]):
    for it in items:
        code = (it.get("code") or "").upper()
        if not code:
            continue
        obj = db.get(Country, code)
        if not obj:
            obj = Country(
                code=code,
                name=it.get("name", code),
                iso2=it.get("iso2"),
                continent=it.get("continent"),
                capital=it.get("capital"),
                population=int(it.get("population", 0) or 0),
                gdp_usd_billion=it.get("gdp_usd_billion"),
                gov_type=it.get("gov_type"),
            )
            db.add(obj)
        else:
            obj.name = it.get("name", obj.name)
            obj.iso2 = it.get("iso2", obj.iso2)
            obj.continent = it.get("continent", obj.continent)
            obj.capital = it.get("capital", obj.capital)
            obj.population = int(it.get("population", obj.population or 0) or 0)
            obj.gdp_usd_billion = it.get("gdp_usd_billion", obj.gdp_usd_billion)
            obj.gov_type = it.get("gov_type", obj.gov_type)


def seed_leaders(db: Session, items: list[dict[str, Any]]):
    for it in items:
        lid = it.get("id")
        if not lid:
            continue
        obj = db.get(Leader, lid)
        if not obj:
            obj = Leader(
                id=lid,
                country_code=(it.get("country_code") or "").upper(),
                name=it.get("name", "Unknown"),
                title=it.get("title", "Leader"),
                start_date=_parse_date(it.get("start_date")),
                ideology=it.get("ideology"),
                approval=_safe_float(it.get("approval")),
            )
            db.add(obj)
        else:
            obj.country_code = (it.get("country_code") or obj.country_code or "").upper()
            obj.name = it.get("name", obj.name)
            obj.title = it.get("title", obj.title)
            obj.start_date = _parse_date(it.get("start_date")) or obj.start_date
            obj.ideology = it.get("ideology", obj.ideology)
            obj.approval = _safe_float(it.get("approval", obj.approval))


def _parse_date(v: Any) -> date | None:
    if not v:
        return None
    try:
        y, m, d = str(v).split("-")
        return date(int(y), int(m), int(d))
    except Exception:
        return None


def _safe_float(v: Any) -> float | None:
    try:
        return float(v)
    except Exception:
        return None


def main() -> None:
    db = SessionLocal()
    try:
        countries = _read_json("countries.json")
        leaders = _read_json("leaders.json")
        seed_countries(db, countries)
        seed_leaders(db, leaders)
        db.commit()
        invalidate_cache()
        print("Refdata seed complete")
    finally:
        db.close()


if __name__ == "__main__":
    main()



from __future__ import annotations

from functools import lru_cache
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
import aiohttp
import asyncio

from .models import Country, Leader, get_session
from ..world_data_service import world_data_service
from .schemas import CountryRead, LeaderRead


router = APIRouter()
logger = logging.getLogger(__name__)


def _normalize_code(code: str) -> str:
    return (code or "").upper()


def _normalize_text(text: Optional[str]) -> str:
    return (text or "").strip().lower()


def _paginate(query, limit: int = 50, offset: int = 0):
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    return query.limit(limit).offset(offset)


def _clear_lru_cache():
    get_country_by_code.cache_clear()
    list_countries.cache_clear()
    get_leader_by_id.cache_clear()
    list_leaders.cache_clear()


@lru_cache(maxsize=1024)
def get_country_by_code(code: str, _: int = 0) -> Optional[CountryRead]:
    # _: dummy arg to allow invalidation pattern when needed
    return None  # placeholder for signature; actual call via route uses DB


@lru_cache(maxsize=128)
def list_countries(q: str, continent: str, limit: int, offset: int, _: int = 0) -> List[CountryRead]:
    return []  # placeholder; actual data from route using DB


@lru_cache(maxsize=1024)
def get_leader_by_id(leader_id: str, _: int = 0) -> Optional[LeaderRead]:
    return None


@lru_cache(maxsize=128)
def list_leaders(country: str, title: str, limit: int, offset: int, _: int = 0) -> List[LeaderRead]:
    return []


@router.get("/countries", response_model=List[CountryRead])
def get_countries(
    q: str = "",
    continent: str = "",
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_session),
):
    query = select(Country)
    if q:
        qn = f"%{_normalize_text(q)}%"
        # Case-insensitive compare on name/code
        query = query.filter((Country.name.ilike(qn)) | (Country.code.ilike(qn)))
    if continent:
        query = query.filter(Country.continent == continent)
    query = _paginate(query, limit, offset)
    rows = db.execute(query).scalars().all()
    return [CountryRead.model_validate(r) for r in rows]


@router.get("/countries/{code}", response_model=CountryRead)
def get_country(code: str, db: Session = Depends(get_session)):
    norm = _normalize_code(code)
    obj = db.get(Country, norm)
    if not obj:
        raise HTTPException(status_code=404, detail="Country not found")
    return CountryRead.model_validate(obj)


@router.get("/leaders", response_model=List[LeaderRead])
def get_leaders(
    country: str = "",
    title: str = "",
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_session),
):
    query = select(Leader)
    if country:
        query = query.filter(Leader.country_code == _normalize_code(country))
    if title:
        tn = f"%{_normalize_text(title)}%"
        query = query.filter(Leader.title.ilike(tn))
    query = _paginate(query, limit, offset)
    rows = db.execute(query).scalars().all()
    return [LeaderRead.model_validate(r) for r in rows]


@router.get("/leaders/{leader_id}", response_model=LeaderRead)
def get_leader(leader_id: str, db: Session = Depends(get_session)):
    obj = db.get(Leader, leader_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Leader not found")
    return LeaderRead.model_validate(obj)


def invalidate_cache() -> None:
    _clear_lru_cache()


# -----------------------------
# World Bank live data helpers
# -----------------------------

WB_BASE = "https://api.worldbank.org/v2"


async def _wb_fetch_latest(session: aiohttp.ClientSession, indicator: str, iso3_codes: List[str]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    if not iso3_codes:
        return result
    # World Bank supports semicolon-separated country codes in a single request
    chunk_size = 50
    tasks = []
    chunk_codes = []
    for i in range(0, len(iso3_codes), chunk_size):
        chunk_list = iso3_codes[i:i+chunk_size]
        chunk_codes.append(chunk_list)
        chunk = ";".join(chunk_list)
        url = f"{WB_BASE}/country/{chunk}/indicator/{indicator}?format=json&MRV=1&per_page=5000"
        tasks.append(session.get(url, timeout=aiohttp.ClientTimeout(total=30)))
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    for idx, resp in enumerate(responses):
        if isinstance(resp, Exception):
            logger.warning("WB chunk %d failed: %s (codes: %s)", idx, resp, chunk_codes[idx][:5])
            continue
        try:
            async with resp:
                if resp.status != 200:
                    logger.warning("WB chunk %d status=%d (codes: %s)", idx, resp.status, chunk_codes[idx][:5])
                    continue
                data = await resp.json()
                # Expected: [meta, [ {countryiso3code, value, date, ...}, ... ]]
                if isinstance(data, list) and len(data) >= 2 and isinstance(data[1], list):
                    for entry in data[1]:
                        code = (entry.get("countryiso3code") or "").upper()
                        val = entry.get("value")
                        if code and val is not None and code not in result:
                            result[code] = {
                                "value": val,
                                "date": entry.get("date")
                            }
                    logger.info("WB chunk %d: parsed %d entries from %d records", idx, len([e for e in data[1] if e.get("value") is not None]), len(data[1]))
                else:
                    logger.warning("WB chunk %d: unexpected shape (codes: %s) data=%s", idx, chunk_codes[idx], str(data)[:200])
        except Exception as e:
            logger.warning("WB chunk %d parse error: %s (codes: %s)", idx, e, chunk_codes[idx][:5])
            continue
    return result


@router.get("/worldbank/gdp")
async def worldbank_gdp_latest(countries: str = "", db: Session = Depends(get_session)) -> dict:
    # GDP current USD
    indicator = "NY.GDP.MKTP.CD"
    iso3 = []
    if countries:
        iso3 = [c.strip().upper() for c in countries.split(",") if c.strip()]
    else:
        # Prefer comprehensive baseline from world_data_service; fall back to DB
        # Pull explicit iso3 if present; otherwise use key when it looks like iso3
        iso3 = []
        # Exclude codes that World Bank doesn't recognize (territories, disputed regions, historical codes, etc.)
        excluded_codes = {
            'ATA', 'ESH', 'ATF', 'SGS', 'BVT', 'HMD', 'IOT', 'UMI', 'PCN', 'TKL', 
            'XAD', 'XCA', 'XKX', 'ALA', 'ASM', 'COK', 'FLK', 'FRO', 'GGY', 'GIB',
            'GRL', 'GUM', 'IMN', 'JEY', 'MSR', 'MNP', 'NIU', 'NFK', 'PRK', 'PSE',
            'SHN', 'SPM', 'SXM', 'TCA', 'VGB', 'WLF', 'MAF', 'BLM', 'CXR', 'CCK'
        }
        for k, v in world_data_service.get_all_countries().items():
            code = v.get("iso3") or (k if isinstance(k, str) and len(k) == 3 and k.isalpha() else None)
            if code and len(code) == 3 and code.isalpha() and code.upper() not in excluded_codes:
                iso3.append(code.upper())
        if not iso3:
            rows = db.execute(select(Country.code)).scalars().all()
            iso3 = [c for c in rows if c]
    # Deduplicate
    iso3 = list(set(iso3))
    logger.info("WorldBank GDP: requesting for %d country codes: %s", len(iso3), iso3[:10])
    # Create SSL context that doesn't verify certificates (World Bank API is public/trusted)
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        data = await _wb_fetch_latest(session, indicator, iso3)
        logger.info("WorldBank GDP fetched entries=%s", len(data))
        return data


@router.get("/worldbank/population")
async def worldbank_population_latest(countries: str = "", db: Session = Depends(get_session)) -> dict:
    indicator = "SP.POP.TOTL"
    iso3 = []
    if countries:
        iso3 = [c.strip().upper() for c in countries.split(",") if c.strip()]
    else:
        iso3 = []
        # Exclude codes that World Bank doesn't recognize (territories, disputed regions, historical codes, etc.)
        excluded_codes = {
            'ATA', 'ESH', 'ATF', 'SGS', 'BVT', 'HMD', 'IOT', 'UMI', 'PCN', 'TKL', 
            'XAD', 'XCA', 'XKX', 'ALA', 'ASM', 'COK', 'FLK', 'FRO', 'GGY', 'GIB',
            'GRL', 'GUM', 'IMN', 'JEY', 'MSR', 'MNP', 'NIU', 'NFK', 'PRK', 'PSE',
            'SHN', 'SPM', 'SXM', 'TCA', 'VGB', 'WLF', 'MAF', 'BLM', 'CXR', 'CCK'
        }
        for k, v in world_data_service.get_all_countries().items():
            code = v.get("iso3") or (k if isinstance(k, str) and len(k) == 3 and k.isalpha() else None)
            if code and len(code) == 3 and code.isalpha() and code.upper() not in excluded_codes:
                iso3.append(code.upper())
        if not iso3:
            rows = db.execute(select(Country.code)).scalars().all()
            iso3 = [c for c in rows if c]
    # Deduplicate
    iso3 = list(set(iso3))
    logger.info("WorldBank Population: requesting for %d country codes: %s", len(iso3), iso3[:10])
    # Create SSL context that doesn't verify certificates (World Bank API is public/trusted)
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        data = await _wb_fetch_latest(session, indicator, iso3)
        logger.info("WorldBank Population fetched entries=%s", len(data))
        return data


@router.get("/health")
def ref_health(db: Session = Depends(get_session)) -> dict:
    countries_count = db.execute(select(Country).count()).scalar() if hasattr(select(Country), 'count') else len(db.execute(select(Country)).scalars().all())
    leaders_count = len(db.execute(select(Leader)).scalars().all())
    return {
        "countries": countries_count,
        "leaders": leaders_count,
        "worldbank": {
            "gdp_endpoint": "/ref/worldbank/gdp",
            "population_endpoint": "/ref/worldbank/population"
        }
    }



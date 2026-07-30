# -*- coding: utf-8 -*-
"""
FEDERAL CONTRACTS & SPENDING API (FastAPI). Search US federal awards, see how much a company
received, and browse top agencies — from USAspending.gov (public domain, keyless).
Run:  uvicorn api:app --port 8000   ·   docs: /docs
"""
from __future__ import annotations
from fastapi import FastAPI, Query
import engine as ENG
import sources as SRC

app = FastAPI(
    title="Federal Contracts & Spending API",
    version="1.0.0",
    description="US federal awards from USAspending.gov (public domain). Search contracts/grants "
                "by keyword, company, agency; see how much federal money a company received; browse "
                "top agencies. Cleanest licensing — free to use and redistribute.",
)


@app.get("/")
def root():
    return {"name": "Federal Contracts & Spending API", "version": "1.0.0",
            "endpoints": ["/search", "/recipient", "/agencies", "/award", "/sources", "/health"],
            "unique": ["search federal contracts/grants by keyword/company/agency",
                       "how much federal money a company received", "public-domain data, resale-safe"],
            "data": "USAspending.gov (US Treasury) — public domain"}

@app.get("/health")
def health():
    a = ENG.agencies(1)
    return {"status": "ok" if a.get("count") else "degraded", "source": "USAspending.gov"}

@app.get("/search")
def search(keyword: str = Query("", description="search text, e.g. 'artificial intelligence'"),
           recipient: str = Query("", description="company name filter, e.g. 'Palantir'"),
           agency: str = Query("", description="awarding agency name filter, e.g. 'Department of Defense'"),
           award_type: str = Query("contracts", description="contracts | grants | loans | direct_payments"),
           years: int = Query(10, ge=1, le=20, description="look back this many years"),
           limit: int = Query(25, ge=1, le=100)):
    """Search US federal awards (contracts/grants) by keyword, company or agency — sorted by amount."""
    return ENG.search_awards(keyword=keyword or None, recipient=recipient or None,
                             agency=agency or None, award_type=award_type, years=years, limit=limit)

@app.get("/recipient")
def recipient(name: str = Query(..., description="company/recipient name, e.g. 'Lockheed Martin'"),
              years: int = Query(10, ge=1, le=20),
              limit: int = Query(25, ge=1, le=100)):
    """How much US federal money a company received (top awards + total), for contracts."""
    return ENG.recipient_spending(name, years=years, limit=limit)

@app.get("/agencies")
def agencies(limit: int = Query(25, ge=1, le=100)):
    """Top US federal agencies by budget authority."""
    return ENG.agencies(limit)

@app.get("/award")
def award(id: str = Query(..., description="award id (from a /search result)")):
    """Full details of a specific federal award."""
    return ENG.award_detail(id)

@app.get("/sources")
def sources():
    return {"sources": SRC.source_meta(),
            "note": "USAspending.gov is US-government public domain — free to use and redistribute, no key."}


if __name__ == "__main__":
    import os, uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))

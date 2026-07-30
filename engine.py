# -*- coding: utf-8 -*-
"""
FEDERAL CONTRACTS & SPENDING — MOTORUL. Cauta premii federale (contracte/granturi), suma primita
de o firma, agentiile de top. Sursa USAspending (POST cu filtre). Best-effort + cache scurt.
"""
from __future__ import annotations
import json, ssl, time, urllib.request
from datetime import datetime, timezone
import sources as SRC

_UA = {"User-Agent": SRC.USER_AGENT, "Accept": "application/json", "Content-Type": "application/json"}
_CTX = ssl.create_default_context(); _CTX.check_hostname = False; _CTX.verify_mode = ssl.CERT_NONE
_CACHE: dict = {}

# campuri returnate (pt contracte — cele mai valoroase; granturile au etichete diferite)
FIELDS_CONTRACT = ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency",
                   "Awarding Sub Agency", "Start Date", "End Date", "recipient_id"]
FIELDS_GRANT    = ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency", "Start Date", "End Date"]


def _get(url, timeout=20):
    now = time.time()
    hit = _CACHE.get(url)
    if hit and (now - hit[1]) < 600:
        return hit[0]
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=timeout, context=_CTX) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
        _CACHE[url] = (j, now); return j
    except Exception:
        return None

def _post(url, body, timeout=25):
    key = url + json.dumps(body, sort_keys=True)
    now = time.time()
    hit = _CACHE.get(key)
    if hit and (now - hit[1]) < 300:
        return hit[0]
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=_UA, method="POST")
        with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
        _CACHE[key] = (j, now); return j
    except Exception as e:
        return {"_error": str(e)[:120]}


def _time_period(years=10):
    end = datetime.now(timezone.utc).date()
    start = end.replace(year=end.year - years)
    return [{"start_date": start.isoformat(), "end_date": end.isoformat()}]


def search_awards(keyword=None, recipient=None, agency=None, award_type="contracts",
                  years=10, limit=25) -> dict:
    codes = SRC.AWARD_TYPES.get(award_type, SRC.AWARD_TYPES["contracts"])
    is_contract = award_type == "contracts"
    filters = {"award_type_codes": codes, "time_period": _time_period(years)}
    if keyword:   filters["keywords"] = [keyword]
    if recipient: filters["recipient_search_text"] = [recipient]
    if agency:    filters["agencies"] = [{"type": "awarding", "tier": "toptier", "name": agency}]
    body = {"filters": filters,
            "fields": FIELDS_CONTRACT if is_contract else FIELDS_GRANT,
            "limit": min(max(limit, 1), 100), "sort": "Award Amount", "order": "desc"}
    j = _post(SRC.SEARCH_AWARD, body)
    if not isinstance(j, dict) or j.get("_error"):
        return {"results": [], "count": 0, "error": (j or {}).get("_error", "no data")}
    res = j.get("results", []) or []
    return {"query": {"keyword": keyword, "recipient": recipient, "agency": agency, "award_type": award_type, "years": years},
            "count": len(res), "results": res,
            "note": "US federal awards (USAspending, public domain). Amounts in USD."}


def recipient_spending(name: str, years=10, limit=25) -> dict:
    """Cat a primit o FIRMA din bani federali (contracte) + top premii."""
    r = search_awards(recipient=name, award_type="contracts", years=years, limit=limit)
    total = 0.0
    for a in r.get("results", []):
        try: total += float(a.get("Award Amount") or 0)
        except Exception: pass
    return {"recipient": name, "years": years,
            "top_awards_total_usd": round(total),
            "award_count_shown": r.get("count", 0),
            "top_awards": r.get("results", []),
            "note": "Suma este pe premiile AFISATE (top {}); pt totalul exact per firma se pot pagina toate.".format(limit),
            "error": r.get("error")}


def agencies(limit=25) -> dict:
    j = _get(SRC.TOPTIER)
    if not isinstance(j, dict):
        return {"agencies": [], "count": 0}
    rows = j.get("results", []) or []
    rows.sort(key=lambda a: a.get("budget_authority_amount") or 0, reverse=True)
    out = [{"name": a.get("agency_name"), "abbreviation": a.get("abbreviation"),
            "budget_authority_usd": a.get("budget_authority_amount"),
            "obligated_usd": a.get("current_total_budget_authority_amount")} for a in rows[:limit]]
    return {"count": len(out), "agencies": out, "note": "Top US federal agencies by budget authority (USAspending)."}


def award_detail(award_id: str) -> dict:
    import urllib.parse
    j = _get(SRC.AWARD_DETAIL.format(award_id=urllib.parse.quote(award_id, safe="")))
    if not isinstance(j, dict):
        return {"award_id": award_id, "found": False}
    return {"award_id": award_id, "found": True,
            "recipient": (j.get("recipient") or {}).get("recipient_name"),
            "amount_usd": j.get("total_obligation"),
            "awarding_agency": ((j.get("awarding_agency") or {}).get("toptier_agency") or {}).get("name"),
            "type": j.get("type_description"), "description": j.get("description"),
            "start": (j.get("period_of_performance") or {}).get("start_date"),
            "end": (j.get("period_of_performance") or {}).get("end_date")}


if __name__ == "__main__":
    import sys
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
    print("== agentii top ==")
    a = agencies(3)
    for x in a["agencies"]: print("  ", x["name"], "|", x["abbreviation"])
    print("== cauta contracte 'artificial intelligence' ==")
    s = search_awards(keyword="artificial intelligence", limit=3)
    print("  gasite:", s["count"], "| eroare:", s.get("error"))
    for r in s["results"][:3]:
        print("   ", r.get("Recipient Name"), "| $", r.get("Award Amount"), "|", r.get("Awarding Agency"))
    print("== cat a primit Lockheed Martin ==")
    rc = recipient_spending("Lockheed Martin", limit=3)
    print("  total (top afisat): $", rc["top_awards_total_usd"], "| premii:", rc["award_count_shown"], "| eroare:", rc.get("error"))

# -*- coding: utf-8 -*-
"""
FEDERAL CONTRACTS & SPENDING API — REGISTRU DE SURSE.
Date despre banii federali SUA: cine primeste contracte/granturi, cat, de la ce agentie.
Sursa: USAspending.gov (Trezoreria SUA) — DOMENIU PUBLIC (guvern SUA), FARA cheie, merge din datacenter.
Licenta cea mai curata din tot Top 5: se poate revinde fara nicio restrictie.

Diferentiator vs incumbenti (makegov/GovCon API, care iau bani pt "un API peste SAM.gov+USAspending"):
un API ieftin self-serve care raspunde "cati bani federali a primit firma X" + cauta contracte.
"""

USER_AGENT = "CrisIntel Federal Contracts (contact: lungucristian1980@gmail.com)"

BASE = "https://api.usaspending.gov/api/v2"

# cautare premii (contracte/granturi) — POST cu filtre
SEARCH_AWARD   = BASE + "/search/spending_by_award/"
# cheltuieli grupate pe categorie (recipient/agency/...) — POST
SPENDING_BY_CAT= BASE + "/search/spending_by_category/"
# lista agentiilor de top + cheltuieli — GET
TOPTIER        = BASE + "/references/toptier_agencies/"
# detaliile unui premiu dupa ID — GET
AWARD_DETAIL   = BASE + "/awards/{award_id}/"

# coduri tip premiu
AWARD_TYPES = {
    "contracts": ["A", "B", "C", "D"],
    "grants":    ["02", "03", "04", "05"],
    "loans":     ["07", "08"],
    "direct_payments": ["06", "10"],
    "other":     ["09", "11"],
}
ALL_CONTRACT_GRANT = ["A", "B", "C", "D", "02", "03", "04", "05"]

def source_meta():
    return [{"name": "USAspending.gov", "authority": "US Treasury / Bureau of the Fiscal Service",
             "url": "https://api.usaspending.gov", "license": "US Government public domain (no restrictions)", "key": False}]

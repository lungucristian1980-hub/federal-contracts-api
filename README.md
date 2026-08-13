# Federal Contracts & Spending API

Search **US federal awards** (contracts & grants), see **how much federal money a company
received**, and browse top agencies — from **USAspending.gov**. US-government **public domain**:
the cleanest licensing possible — free to use and redistribute, no key.

## Why this API

Every federal contract and grant is public, but it's spread across clunky, rate-limited government
systems. Paid "unifiers" (makegov, GovCon API) charge real money for one clean key over
SAM.gov + USAspending + FPDS. This is a cheap, self-serve slice: **the questions govcon firms,
sales teams and researchers actually ask** — *who got the money, how much, from which agency.*

## Endpoints

| Endpoint | What it returns |
|---|---|
| `GET /search?keyword=artificial+intelligence` | Federal awards matching a keyword, sorted by amount |
| `GET /search?recipient=Palantir` | Awards to a specific company |
| `GET /search?agency=Department+of+Defense` | Awards from a specific agency |
| `GET /recipient?name=Lockheed+Martin` | **How much federal money a company received** (total + top awards) |
| `GET /agencies` | Top US federal agencies by budget authority |
| `GET /award?id=...` | Full details of one award |
| `GET /sources` | Data provenance & licensing |
| `GET /health` | Service health |

`/search` params: `keyword`, `recipient`, `agency`, `award_type` (`contracts`/`grants`/`loans`/`direct_payments`), `years` (look-back), `limit`.

## Example

```bash
curl "https://<host>/recipient?name=Lockheed%20Martin"
```
```json
{
  "recipient": "Lockheed Martin",
  "top_awards_total_usd": 117373211219,
  "award_count_shown": 25,
  "top_awards": [ { "Recipient Name": "LOCKHEED MARTIN CORPORATION",
                    "Award Amount": 12345678, "Awarding Agency": "Department of Defense",
                    "Start Date": "...", "End Date": "..." } ]
}
```

Interactive docs: **`/docs`**

## Data & licensing

100% from **USAspending.gov** (US Treasury / Bureau of the Fiscal Service) — **US-government public
domain**, no restrictions on reuse or resale, no API key. This service adds one clean self-serve
interface (search + recipient totals + agencies) on top.

## Run locally

```bash
pip install -r requirements.txt
uvicorn api:app --reload
# http://localhost:8000/docs
```


---

<sub>Built & maintained by **Quiet Machines** — the quiet machines that run your business. · by Cristian Lungu</sub>

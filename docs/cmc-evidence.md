# CoinMarketCap API — evidence of real calls (VaultTerms v2)

Hackathon requirement: *"visible evidence of a real API call: code and response."*
Run of `registry/cmc_rwa.py` on 2026-09-03T23:26:08+00:00 with a hackathon Startup-tier key (never committed — it is a GitHub Actions secret; see the daily workflow).
Base URL `https://pro-api.coinmarketcap.com`, header `X-CMC_PRO_API_KEY`. The cron commits `registry/cmc_calls.json` on every run, so the call log is public and refreshed daily.

## Calls made in this run (9 credits)

| Endpoint | Params | Credits |
|---|---|---|
| `/issuers/list` | `{"limit": 250, "active": "true"}` | 1 |
| `/assets/list` | `{"asset_type": "stock", "limit": 50, "sort": "tokenized_market_cap", "sort_dir": "desc"}` | 1 |
| `/assets/list` | `{"asset_type": "commodity", "limit": 50, "sort": "tokenized_market_cap", "sort_dir": "desc"}` | 1 |
| `/assets/list` | `{"asset_type": "currency", "limit": 50, "sort": "tokenized_market_cap", "sort_dir": "desc"}` | 1 |
| `/assets/list` | `{"asset_type": "government_security", "limit": 50, "sort": "tokenized_market_cap", "sort_dir": "desc"}` | 1 |
| `/assets/list` | `{"asset_type": "etf", "limit": 50, "sort": "tokenized_market_cap", "sort_dir": "desc"}` | 1 |
| `/assets/list` | `{"asset_type": "real_estate", "limit": 50, "sort": "tokenized_market_cap", "sort_dir": "desc"}` | 1 |
| `/quotes/latest` | `{"symbol": "NVDA,TSLA,AAPL,MSFT,GOOGL,AMZN,META,SPY,QQQ,GOLD", "skip_invalid": "true"}` | 1 |
| `/quotes/latest` | `{"symbol": "SILVER,COIN,MSTR,CRCL", "skip_invalid": "true"}` | 1 |

## The client (registry/cmc_rwa.py)

```python
#!/usr/bin/env python3
"""VaultTerms v2 — CoinMarketCap Real-World Assets layer.

Pulls the CMC RWA endpoints (v5) into three files the page renders, and joins
CMC issuers to the hand-verified registry:

  cmc_issuers.json   issuers/list  → every RWA token issuer CMC tracks (+ ledger match)
  cmc_assets.json    assets/list   → per asset_type totals + top assets (stock, commodity,
                                     currency, government_security, etf, real_estate)
  cmc_premiums.json  quotes/latest → per-issuer wrapper price vs blended tokenized average
                                     for the tickers our tokenized-stock / gold vaults wrap

Key: CMC_API_KEY env var, else ~/.config/cmc.env. Cost: ~10 credits per run.
Endpoints: https://coinmarketcap.com/api/documentation/pro-api-reference/real-world-assets
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
BASE = "https://pro-api.coinmarketcap.com/v5/real-world-assets"
ASSET_TYPES = ["stock", "commodity", "currency", "government_security", "etf", "real_estate"]
# Tickers whose tokenized wrappers appear in the verified ledger (xStocks, Ondo GM, PAXG/XAUT)
PREMIUM_SYMBOLS = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "SPY", "QQQ", "GOLD", "SILVER", "COIN", "MSTR", "CRCL"]
# Ledger vault id → CMC issuer name (as returned by issuers/list)
VAULT_ISSUER = {
    "paxos-gold-paxg": "Paxos",
    "tether-gold-xaut": "Tether Holdings",
    "ondo-global-markets": "Ondo Assets",
    "xstocks-backed": "Backed Assets",
}
CALLS = []


def key():
    k = os.environ.get("CMC_API_KEY")
    if not k:
        f = Path.home() / ".config" / "cmc.env"
        if f.exists():
            k = f.read_text().strip().split("=", 1)[1]
    if not k:
        raise SystemExit("CMC_API_KEY missing (env var or ~/.config/cmc.env)")
    return k


def get(path, **params):
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"X-CMC_PRO_API_KEY": key(), "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    st = body.get("status", {})
    CALLS.append({"endpoint": path, "params": params, "credits": st.get("credit_count"), "error_code": st.get("error_code")})
    if int(st.get("error_code") or 0) != 0:  # CMC serialises error_code as a string
        raise RuntimeError(f"{path}: {st.get('error_message')}")
    return body["data"]
```

## GET /v5/real-world-assets/assets/list — per-category sizing (`sort=tokenized_market_cap&sort_dir=desc`)

| asset_type | assets on CMC | top-50 tokenized mcap | top-50 24h volume |
|---|---|---|---|
| stock | 4,811 | $1,895.1M | $961.9M |
| commodity | 3 | $4,762.3M | $533.6M |
| currency | 0 | $0.0M | $0.0M |
| government_security | 0 | $0.0M | $0.0M |
| etf | 3,126 | $600.8M | $254.1M |
| real_estate | 0 | $0.0M | $0.0M |

Top tokenized stocks by tokenized market cap:

| Symbol | Name | Tokenized mcap | Avg tokenized price |
|---|---|---|---|
| CRCL | Circle Internet Group Inc | $331.2M | $102.32 |
| SPCX | SpaceX | $211.2M | $149.19 |
| MSTR | MicroStrategy Inc | $172.2M | $143.39 |
| TSLA | Tesla, Inc. | $119.1M | $375.37 |
| MU | Micron Technology Inc | $118.3M | $954.99 |
| NVDA | Nvidia Corp | $112.0M | $228.93 |
| GOOGL | Alphabet Inc Class A | $109.4M | $343.29 |
| SNDK | SanDisk Corp | $77.1M | $1,548.72 |

## GET /v5/real-world-assets/quotes/latest — wrapper premiums

`tokens[]` per underlying carries each issuer's wrapper price; VaultTerms computes premium vs the blended `average_tokenized_price`.

GOLD (blended $4,468.86):

| Token | Issuer | Price | vs blended | Mcap |
|---|---|---|---|---|
| XAUt | Tether Holdings | $4,466.78 | -0.047% | $2,737.3M |
| PAXG | Paxos | $4,475.86 | +0.157% | $1,934.0M |
| XAUM | Matrixdock | $4,463.74 | -0.115% | $49.0M |
| CGO | Comtech Gold | $143.72 | -96.784% | $20.3M |
| XAUT0 | Tether Holdings | $4,469.72 | +0.019% | $16.6M |
| VNXAU | VNX | $142.84 | -96.804% | $6.0M |
| XAU | NA (Derivatives) | $4,477.94 | +0.203% | $0.0M |

NVDA (blended $228.93):

| Token | Issuer | Price | vs blended |
|---|---|---|---|
| NVDAX | Backed Assets | $229.62 | +0.300% |
| NVDAon | Ondo Assets | $229.53 | +0.264% |
| NVDAB | bStocks | $229.45 | +0.226% |
| NVDA | Robinhood | $228.70 | -0.099% |
| rNVDA | Reality | $229.48 | +0.242% |
| WNVDAX | Backed Assets | $229.58 | +0.285% |
| NVDA | NA (Derivatives) | $229.63 | +0.306% |

## GET /v5/real-world-assets/issuers/list → joined to the verified ledger

24 issuers tracked. Vaults on the ledger matched to their CMC issuer record:

| Ledger vault | CMC issuer | Tokens issued | Wrapper premiums (top) |
|---|---|---|---|
| paxos-gold-paxg | Paxos | 1 | PAXG +0.16% |
| tether-gold-xaut | Tether Holdings | 2 | XAUt -0.05%, XAUT0 +0.02% |
| ondo-global-markets | Ondo Assets | 544 | CRCLon +0.01%, SPYon +0.56%, NVDAon +0.26% |
| xstocks-backed | Backed Assets | 976 | CRCLX -0.00%, TSLAX -0.03%, MSTRX -0.07% |

## Where the API got in the way (feedback for the CMC product team)

- `sort=tokenized_market_cap` sorts **ascending** unless `sort_dir=desc` is passed — the first run returned $0-cap assets as "top". Documenting the default would save every integrator a wasted credit.
- `status.error_code` is serialised as the string `"0"`; a strict numeric check treats every success as an error.
- Three of six `asset_type` values return **zero assets** (`currency`, `government_security`, `real_estate`) — yet tokenized treasuries are the largest RWA category by TVL. Tokenized funds (BUIDL, USDY, JTRSY) are the biggest gap.
- Some wrappers report prices in a different unit than the blended average (Comtech Gold CGO at −97%): a `unit` or `contract_size` field would let clients tell a unit mismatch from a real dislocation.
- No yield/APY, TVL, or terms fields — eligibility and yield still come from the hand-verified registry and DeFiLlama; a `yield` field and a `vault`/`fund` asset type would make these endpoints the backbone of any RWA product.
- `market-pairs/list` is Growth-tier only, so venue-level liquidity was out of reach on the Startup tier.

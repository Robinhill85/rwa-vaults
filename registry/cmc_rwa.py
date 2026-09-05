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


def sum_complete(rows, field):
    """Missing contributions must not become a false zero or a full total."""
    values = [row.get(field) for row in rows]
    return round(sum(values)) if values and all(isinstance(v, (int, float)) for v in values) else None


def main():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    vaults = json.loads((HERE / "vaults.json").read_text())

    # 1) Issuers — small universe (~25), one call
    d = get("/issuers/list", limit=250, active="true")
    issuers = [{"issuer_id": i["issuer_id"], "name": i["name"], "website": i.get("website"), "logo": i.get("logo"), "num_tokens": i.get("num_tokens", 0)} for i in d["issuers"]]
    by_name = {i["name"]: i for i in issuers}
    for vid, iname in VAULT_ISSUER.items():
        if iname in by_name:
            by_name[iname]["ledger_vault_id"] = vid
    issuers.sort(key=lambda i: -(i["num_tokens"] or 0))
    (HERE / "cmc_issuers.json").write_text(json.dumps({"as_of": now, "total": d.get("total_size", len(issuers)), "issuers": issuers}, indent=2))

    # 2) Assets per type — six calls
    types = {}
    for t in ASSET_TYPES:
        a = get("/assets/list", asset_type=t, limit=50, sort="tokenized_market_cap", sort_dir="desc")  # sort_dir required: default is ascending
        rows = []
        for x in a.get("rwa_assets", []):
            rows.append({
                "symbol": x["symbol"], "name": x["name"], "rwa_id": x["rwa_id"], "rwa_rank": x.get("rwa_rank"),
                "tokenized_market_cap": x.get("tokenized_market_cap"),
                "average_tokenized_price": x.get("average_tokenized_price"),
                "tokenized_volume_24h": x.get("tokenized_volume_24h"),
            })
        types[t] = {
            "count": a.get("total_size", len(rows)),
            "tokenized_market_cap_top50": sum_complete(rows, "tokenized_market_cap"),
            "volume_24h_top50": sum_complete(rows, "tokenized_volume_24h"),
            "top": rows[:15],
        }
    (HERE / "cmc_assets.json").write_text(json.dumps({"schema_version": 2, "as_of": now, "types": types}, indent=2))

    # 3) Wrapper premiums — two calls (batched symbols)
    prem = {}
    for i in range(0, len(PREMIUM_SYMBOLS), 10):
        q = get("/quotes/latest", symbol=",".join(PREMIUM_SYMBOLS[i:i + 10]), skip_invalid="true")
        for x in q.get("rwa_assets", []):
            avg = x.get("average_tokenized_price")
            toks = []
            for tk in x.get("tokens", []):
                p = tk.get("price")
                toks.append({
                    "symbol": tk.get("symbol"), "issuer": tk.get("issuer_name"), "issuer_id": tk.get("issuer_id"),
                    "price": p, "market_cap": tk.get("market_cap"), "volume_24h": tk.get("volume_24h"),
                    "premium_pct": round((p / avg - 1) * 100, 3) if (p and avg) else None,
                })
            toks.sort(key=lambda z: -(z["market_cap"] or 0))
            prem[x["symbol"]] = {
                "name": x["name"], "asset_type": x.get("asset_type"), "average_tokenized_price": avg,
                "tokenized_market_cap": x.get("tokenized_market_cap"), "last_updated": x.get("last_updated"), "tokens": toks,
            }
    (HERE / "cmc_premiums.json").write_text(json.dumps({"as_of": now, "assets": prem}, indent=2))

    # 4) Join onto the registry: issuer facts + the issuer's wrapper premiums
    matched = 0
    for v in vaults:
        iname = VAULT_ISSUER.get(v["id"])
        if not iname or iname not in by_name:
            continue
        inf = by_name[iname]
        wrappers = []
        for sym, a in prem.items():
            for tk in a["tokens"]:
                if tk["issuer"] == iname and tk["premium_pct"] is not None:
                    wrappers.append({"underlying": sym, "token": tk["symbol"], "premium_pct": tk["premium_pct"], "market_cap": tk["market_cap"]})
        wrappers.sort(key=lambda w: -(w["market_cap"] or 0))
        v["cmc"] = {"issuer_id": inf["issuer_id"], "issuer_name": iname, "num_tokens": inf["num_tokens"], "wrappers": wrappers[:8], "as_of": now}
        matched += 1
    (HERE / "vaults.json").write_text(json.dumps(vaults, indent=2))

    (HERE / "cmc_calls.json").write_text(json.dumps({"as_of": now, "calls": CALLS, "credits_total": sum(c["credits"] or 0 for c in CALLS)}, indent=2))
    print(f"cmc: {len(issuers)} issuers, {sum(t['count'] for t in types.values())} assets across {len(types)} types, "
          f"{len(prem)} premium symbols, {matched} vaults joined, {sum(c['credits'] or 0 for c in CALLS)} credits")


if __name__ == "__main__":
    main()

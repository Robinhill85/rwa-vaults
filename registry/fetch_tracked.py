#!/usr/bin/env python3
"""Build the auto-generated 'Tracked' tier from DeFiLlama's RWA-category protocols.

Everything here is machine-derived (no hand-verified terms) and the page labels
it as such. Curated vaults are excluded by slug so the tiers never overlap.

Usage: python3 fetch_tracked.py    # writes tracked.json
"""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
CATEGORIES = {"RWA": "rwa", "RWA Lending": "rwa_lending", "Basis Trading": "basis_trading"}
LIMIT = 80          # tracked entries kept (top by TVL), on top of the curated tier
MIN_TVL = 5_000_000  # ignore dust protocols


def main():
    curated = json.loads((HERE / "vaults.json").read_text())
    curated_slugs = {v["defillama_slug"] for v in curated if v.get("defillama_slug")}
    # slugs DeFiLlama splits differently from our curated join keys
    curated_slugs |= {"centrifuge-protocol", "ondo-global-markets", "goldfinch"}

    with urllib.request.urlopen("https://api.llama.fi/protocols", timeout=60) as r:
        protocols = json.load(r)

    rows = []
    for p in protocols:
        if p.get("category") not in CATEGORIES:
            continue
        if p["slug"] in curated_slugs:
            continue
        tvl = p.get("tvl") or 0
        if tvl < MIN_TVL:
            continue
        rows.append({
            "slug": p["slug"],
            "name": p["name"],
            "category": CATEGORIES[p["category"]],
            "chains": (p.get("chains") or [])[:6],
            "tvl_usd": round(tvl),
            "change_7d_pct": round(p["change_7d"], 2) if p.get("change_7d") is not None else None,
            "url": p.get("url"),
            "defillama_url": f"https://defillama.com/protocol/{p['slug']}",
        })

    rows.sort(key=lambda x: -x["tvl_usd"])
    rows = rows[:LIMIT]
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": "Auto-generated from DeFiLlama RWA categories. NOT hand-verified: no terms, KYC, or access data. Curated-tier vaults excluded.",
        "protocols": rows,
    }
    (HERE / "tracked.json").write_text(json.dumps(out, indent=2))
    print(f"tracked.json: {len(rows)} protocols "
          f"(total TVL ${sum(r['tvl_usd'] for r in rows)/1e9:.1f}B)")


if __name__ == "__main__":
    main()

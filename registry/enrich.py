#!/usr/bin/env python3
"""Join live DeFiLlama TVL/APY onto the curated vault registry.

Usage: python3 enrich.py            # reads vaults.json, writes vaults.enriched.json
"""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def main():
    vaults = json.loads((HERE / "vaults.json").read_text())
    protocols = {p["slug"]: p for p in fetch("https://api.llama.fi/protocols")}
    pools = fetch("https://yields.llama.fi/pools")["data"]

    # best APY-bearing pool per project slug, weighted toward TVL
    by_project = {}
    for p in pools:
        proj = (p.get("project") or "").lower()
        cur = by_project.get(proj)
        if cur is None or (p.get("tvlUsd") or 0) > (cur.get("tvlUsd") or 0):
            by_project[proj] = p

    # optional second-opinion APY check via AskSurf (covers only DeFi-native majors)
    surf_apy = {}
    surf_key_file = Path.home() / ".config" / "asksurf.env"
    if surf_key_file.exists():
        key = surf_key_file.read_text().strip().split("=", 1)[1]
        # superstate is deliberately absent: Surf's top superstate pool is USCC (crypto carry), not USTB
        SURF_PROJECTS = {"maple": "maple", "ethena-usde": "ethena", "ondo-yield-assets": "ondo"}
        for slug, proj in SURF_PROJECTS.items():
            try:
                req = urllib.request.Request(
                    f"https://api.asksurf.ai/gateway/v1/onchain/yield/ranking?project={proj}&limit=1&sort_by=tvl_usd&order=desc",
                    headers={"Authorization": "Bearer " + key})
                with urllib.request.urlopen(req, timeout=30) as r:
                    rows = json.load(r)["data"]
                if rows:
                    surf_apy[slug] = round(rows[0]["apy"], 2)
            except Exception:
                pass  # cross-check is best-effort; DeFiLlama remains authoritative

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for v in vaults:
        slug = v.get("defillama_slug")
        live = {"as_of": now, "tvl_usd": None, "apy_pct": None}
        if slug and slug in protocols:
            live["tvl_usd"] = protocols[slug].get("tvl")
        pool = by_project.get((slug or "").lower())
        if pool:
            live["apy_pct"] = pool.get("apy")
            if live["tvl_usd"] is None:
                live["tvl_usd"] = pool.get("tvlUsd")
        if slug in surf_apy:
            live["apy_check_asksurf"] = surf_apy[slug]
        v["live"] = live

    out = HERE / "vaults.enriched.json"
    out.write_text(json.dumps(vaults, indent=2))
    matched = sum(1 for v in vaults if v["live"]["tvl_usd"] is not None)
    print(f"enriched {matched}/{len(vaults)} vaults with live TVL -> {out.name}")


if __name__ == "__main__":
    main()

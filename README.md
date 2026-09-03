# VaultTerms (vaultterms.com)

Curated registry + live data pipeline behind vaultterms.com — an overview of RWA vaults:
what backs each vault, who can invest, on what terms, and where.

## Status (Sep 1, 2026)

- `registry/vaults.json` — 26 vaults, hand-verified from official issuer docs (research pass 2026-09-01)
- `registry/vaults.enriched.json` — registry + live DeFiLlama TVL/APY (`python3 registry/enrich.py`)
- `registry/cmc_issuers.json`, `cmc_assets.json`, `cmc_premiums.json`, `cmc_calls.json` — CoinMarketCap RWA layer (`python3 registry/cmc_rwa.py`)
- `registry/SCHEMA.md` — field reference
- `registry/_batch_*.json` — raw research batches (provenance; vaults.json is the merge)

## Coverage

12 tokenized treasuries, 6 private credit, 1 corporate bonds (IXS/SHYG on
Avalanche), 2 gold, 2 tokenized stocks, 2 basis-yield, 1 reinsurance.
16 of 26 retail-accessible somewhere.
Goldfinch Prime included as winding-down (historical/cautionary; not investable).
Note for the page: IXS is a Robin/Overxceed client — add a disclosure line
wherever the IXS vault is featured.

## #BuildwithCMC — Real World Assets track

VaultTerms v2 adds a CoinMarketCap Real-World Assets layer on top of the hand-verified registry (`registry/cmc_rwa.py`, run daily by the same cron):

| CMC endpoint | What VaultTerms does with it |
|---|---|
| `GET /v5/real-world-assets/issuers/list` | **Issuer explorer** — every RWA token issuer CMC tracks, joined to the vaults on this ledger that carry verified terms |
| `GET /v5/real-world-assets/assets/list` (`asset_type`, `sort=tokenized_market_cap&sort_dir=desc`) | **Tokenized assets tier** — sizes stocks / commodities / ETFs, categories no DeFi TVL tracker models |
| `GET /v5/real-world-assets/quotes/latest` | **Wrapper premiums** — each issuer's tokenized price vs the blended average (xStocks, Ondo, Robinhood, PAXG vs XAUT…), shown on the relevant vault cards |

Evidence of real calls (code + responses + the daily public call log `registry/cmc_calls.json`): [`docs/cmc-evidence.md`](docs/cmc-evidence.md). The CMC key is a GitHub Actions secret and never committed. Everything CMC-related was built for the hackathon (commits from 2026-09-03 onward); the registry, tracked tier and eligibility desk pre-date it and are disclosed as such.

## Data layers

1. **Curated (the moat):** underlying assets, KYC tier, jurisdiction, minimums,
   redemption mechanics, fees, how-to-invest paths — verified against issuer docs.
2. **Live:** DeFiLlama protocols + yields APIs (free, no key) via `enrich.py`.
   Franklin BENJI has no DeFiLlama entry (slug null) — use rwa.xyz if needed.
3. **CoinMarketCap RWA API:** issuers, tokenized-asset categories, wrapper premiums (`registry/cmc_rwa.py`, ~9 credits/day).

## Next steps

- Overview page (RWA Radar-style: snapshot JSON → static site → Vercel)
- Cron refresh (enrich + CMC sustainability pass)
- Filters: asset class, chain, "retail-accessible", KYC tier, jurisdiction

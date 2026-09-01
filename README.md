# VaultTerms (vaultterms.com)

Curated registry + live data pipeline behind vaultterms.com — an overview of RWA vaults:
what backs each vault, who can invest, on what terms, and where.

## Status (Sep 1, 2026)

- `registry/vaults.json` — 26 vaults, hand-verified from official issuer docs (research pass 2026-09-01)
- `registry/vaults.enriched.json` — registry + live DeFiLlama TVL/APY (`python3 registry/enrich.py`)
- `registry/SCHEMA.md` — field reference
- `registry/_batch_*.json` — raw research batches (provenance; vaults.json is the merge)

## Coverage

12 tokenized treasuries, 6 private credit, 1 corporate bonds (IXS/SHYG on
Avalanche), 2 gold, 2 tokenized stocks, 2 basis-yield, 1 reinsurance.
16 of 26 retail-accessible somewhere.
Goldfinch Prime included as winding-down (historical/cautionary; not investable).
Note for the page: IXS is a Robin/Overxceed client — add a disclosure line
wherever the IXS vault is featured.

## Data layers

1. **Curated (the moat):** underlying assets, KYC tier, jurisdiction, minimums,
   redemption mechanics, fees, how-to-invest paths — verified against issuer docs.
2. **Live:** DeFiLlama protocols + yields APIs (free, no key) via `enrich.py`.
   Franklin BENJI has no DeFiLlama entry (slug null) — use rwa.xyz if needed.
3. **Analysis (planned):** CMC Skill Hub `review_yield_sustainability` per-vault
   badge on refresh (verified working, ~4s/call).

## Next steps

- Overview page (RWA Radar-style: snapshot JSON → static site → Vercel)
- Cron refresh (enrich + CMC sustainability pass)
- Filters: asset class, chain, "retail-accessible", KYC tier, jurisdiction

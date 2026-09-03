# RWA Vault Registry — Schema

`vaults.json` is the curated, hand-verified layer of the RWA vaults overview.
Live numbers (TVL, APY) are enriched at build time by `enrich.py` from DeFiLlama;
the curated fields below are the moat and change rarely.

## Vault object

| Field | Type | Notes |
|---|---|---|
| `id` | string | kebab-case, stable key |
| `name` | string | display name |
| `issuer` | string | legal/brand issuer |
| `asset_class` | enum | `tokenized_treasuries` \| `private_credit` \| `corporate_bonds` \| `gold` \| `tokenized_stocks` \| `basis_yield` \| `reinsurance` |
| `underlying` | string | plain-English: what actually backs it |
| `tokens` | string[] | token symbols |
| `chains` | string[] | chains where the token lives |
| `tvl_usd_approx` | number | snapshot at research time; superseded by enrichment |
| `apy_pct_approx` | number\|null | snapshot; superseded by enrichment |
| `terms.min_investment` | string | "$5M", "$100k", "none" |
| `terms.kyc` | enum | `none` \| `kyc_retail` \| `accredited` \| `qualified_purchaser` \| `institutional_only` |
| `terms.jurisdiction` | string | e.g. "non-US only", "EU retail" |
| `terms.redemption` | string | mechanics + settlement time |
| `terms.lockup` | string | |
| `terms.fees` | string | mgmt fee etc. |
| `access.retail_accessible` | bool | can a normal person get in somewhere |
| `access.how_to_invest` | {method,url}[] | practical entry paths |
| `defillama_slug` | string\|null | join key for live enrichment |
| `yield_profile` | object? | optional: target vs trailing yield, guaranteed flag, notes (for vaults marketing a target) |
| `promotions` | object[]? | optional time-boxed bonus programs: `window.start/end` (page should auto-expire past `end`), `tiers`, `mechanic`, `caveats`, `source` |
| `risk_notes` | string | |
| `sources` | string[] | URLs the terms were verified from |
| `verified_at` | string | ISO date of the research pass |

## Files

- `vaults.json` — curated registry (this repo's source of truth)
- `enrich.py` — joins live DeFiLlama TVL/APY onto the registry → `vaults.enriched.json`

| `cmc` | object? | joined from CoinMarketCap RWA API by `cmc_rwa.py`: `issuer_id`, `issuer_name`, `num_tokens`, `wrappers[]` (token, underlying, premium_pct vs blended tokenized average), `as_of` |

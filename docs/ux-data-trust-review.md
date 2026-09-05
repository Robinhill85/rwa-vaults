# VaultTerms clarity and data trust

## Changes

- [x] Reused the existing blue grid, amber figures, panel styles and native HTML controls.
- [x] Financial values share live / approx / snapshot / unavailable states, with source dates per field or section. Successful empty CMC categories explicitly say not covered. Missing yields explain that no figure was supplied, rather than implying a zero return.
- [x] Preserved measured zero TVL instead of replacing it with research estimates. Removed mixed-provenance aggregate TVL totals from category headers/footer; individual figures retain their source/status.
- [x] CMC generation preserves missing market cap and volume as null. Category totals are unavailable when contributions are missing. Schema version 2 identifies corrected snapshots. Old snapshot zeros are conservatively shown unavailable, with an explanation, because the old generator conflated null with zero. Existing snapshot files were not rewritten.
- [x] Sticky “Showing X of Y verified vaults,” removable active-filter chips and category counts based on current Eligibility Desk answers. Reset clears category as well as region, ticket and KYC. Unknown minimums cannot pass a budget filter. Corrected the $1M option's value from $10M to $1M.
- [x] Jump links to all five sections. CMC/Tracked remain visible with explicit unfiltered scope. Issuer links reset filters when necessary to reveal the linked vault. Tracked carries a not-hand-verified badge and softer heading/figure weights.
- [x] All table columns retained on mobile, with labeled keyboard-focusable scroll regions and a pinned asset/issuer/protocol column. More obvious, individually ARIA-labeled vault expansion controls.
- [x] Raised helper/badge text to at least 12px, improved muted contrast, added focus indicators, retained explicit signed premium/discount text. Glossary and contextual links/tooltips cover KYC, admitted, QP, wrapper vs blended, basis-trade and data statuses.
- [x] Feeds load independently with 12-second bounds and retry controls. A ledger outage does not discard CMC data; a CMC outage does not discard verified entries.

## Status semantics

Live is a provider capture no older than 48 hours, not a streaming quote. Approx covers research estimates and issuer targets, regardless of age; its date remains visible. Snapshot covers recorded issuer terms and old/undated provider readings. Unavailable means no usable value/feed. Not covered is reserved for a successful CMC category response with count zero. Dates are displayed at day precision for density; original timestamps remain in the JSON files. These are application display rules, not issuer guarantees.

## Verification

Local Chromium, 1280px desktop and 375×812 mobile, 5 September 2026:

- Anywhere → US → $10k → No KYC: **26 → 16 → 11 → 5**. Visible entries, summary and All/category counts agree.
- Expanded Hastra terms, reset all filters, checked category reset.
- All four market-data tables scroll horizontally; first columns remain pinned; no document overflow at 375px.
- Visually inspected desktop filtered/expanded state and mobile asset/premium tables.
- Injected independent ledger and CMC outages, verified successful retries and retained unrelated sections. Confirmed absent category response differs from a successful zero-coverage response.
- Four Node regression tests and three Python unit tests pass; inline JavaScript parses; git diff whitespace check passes. No new dependencies.

```sh
node --test tests/data-ui.test.cjs
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
```

No paid CMC refresh, commit, push or deployment performed for this change.

## Files

- `ledger/index.html`: eligibility, field states, independent loading/retry, jump navigation, glossary, mobile tables and existing-token CSS.
- `registry/cmc_rwa.py`: null preservation, complete totals and schema marker.
- `tests/data-ui.test.cjs`: value/status/filter regression cases with stable fixtures.
- `tests/test_cmc_values.py`: missing-vs-zero aggregate behavior.
- `docs/ux-data-trust-review.md`: this record.

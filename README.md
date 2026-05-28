# Matassa Cycle Framework

Public reference layer for **cyclical market analysis** built around the Matassa methodology.

This repository is intentionally **showcase-only**: it shares calibrated reference tables and framework documentation. It does **not** include Pine Script source code, pattern-matching engines, statistical projection modules, or execution logic.

> **Full indicator suite:** [Matassa Completa](https://www.tradingview.com/u/AnDr3HA/) on TradingView ([@AnDr3HA](https://www.tradingview.com/u/AnDr3HA/)) — **invite-only**.  
> **Execution & terminal:** [Cycle Lab](https://andreafinazzi.com) — private product stack.

---

## What is here

| Asset | Description |
|-------|-------------|
| [`reference-tables/`](reference-tables/) | Optimized T-scale cycle duration tables by market and length profile |
| [`docs/framework-overview.md`](docs/framework-overview.md) | High-level architecture (public vs private layers) |
| [`docs/using-reference-tables.md`](docs/using-reference-tables.md) | How to read and apply the tables |
| [`assets/screenshots/`](assets/screenshots/) | Visual previews of private modules (images only, no source) |

---

## Reference tables (low-IP layer)

Cycle durations are expressed on the **T-scale** (T = weekly nominal anchor, T+n = longer harmonics).  
Five **length profiles** cover different volatility regimes:

| Profile | Factor | Use case |
|---------|--------|----------|
| MIN | 0.6875× | Compressed / fast markets |
| C | 0.75× | Short cycle bias |
| M | 1.0× | Neutral baseline |
| L | 1.25× | Extended cycles |
| MAX | 1.4375× | Slow / stretched cycles |

Markets are calibrated relative to Crypto (100% reference): Futures/Forex, Forex, Futures, US Stocks, EU Stocks.

Raw Hurst-style nominal lengths exist in public literature; **these tables apply cross-market calibration factors** tuned for live multi-asset work. See [`reference-tables/README.md`](reference-tables/README.md).

---

## Private stack (not in this repo)

The following remain **closed source** — screenshots may appear under `assets/screenshots/` for illustration only:

- **Matassa Completa** — full overlay indicator (TradingView, invite-only)
- **Matassa Pattern Matching** — cycle shape matching & forward projections
- **Matassa Statistica** — statistical cycle projection engine
- **Matassa Model Entry** — strategy / entry model
- **Cycle Lab Terminal** — FastAPI + Vue execution environment

---

## Quick start

1. Open [`reference-tables/m-1-0x.csv`](reference-tables/m-1-0x.csv) for the neutral baseline table.
2. Pick your market column (e.g. `CRYPTO (100%)`, `STOCK USA (19.3%)`).
3. Read [`docs/using-reference-tables.md`](docs/using-reference-tables.md) for interpretation.

---

## Request access

- **TradingView (Matassa Completa):** profile [@AnDr3HA](https://www.tradingview.com/u/AnDr3HA/) — request invite via [andreafinazzi.com](https://andreafinazzi.com) or [email](mailto:andrea.finazzi.info@gmail.com)
- **Cycle Lab terminal:** product waitlist via website

---

## License

Reference tables and documentation: see [LICENSE](LICENSE).  
Tables may be used for **personal research and education**. Commercial redistribution or repackaging as a competing product is not permitted without written permission.

---

**Andrea Finazzi** — Quantitative Architect · [GitHub](https://github.com/andreafinazziinfo) · [Website](https://andreafinazzi.com)

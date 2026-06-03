<div align="center">

<!-- GIF animates on GitHub (SVG CSS animations are stripped by GitHub's image proxy) -->
<img src="https://raw.githubusercontent.com/andreafinazziinfo/matassa-cycle-framework/main/assets/banner.gif?v=7" width="100%" alt="Matassa Cycle Framework — intro title, candle-by-candle chart, cyan FLD, projection line and T-scale table" />

<br>

<p>
  <a href="https://www.tradingview.com/u/AnDr3HA/"><img src="https://img.shields.io/badge/TradingView-@AnDr3HA-09F1B8?style=flat-square&logo=tradingview&logoColor=black" alt="TradingView" /></a>
  &nbsp;
  <a href="https://github.com/andreafinazziinfo"><img src="https://img.shields.io/badge/GitHub-andreafinazziinfo-8B5CF6?style=flat-square&logo=github&logoColor=white" alt="GitHub" /></a>
  &nbsp;
  <a href="https://andreafinazzi.com"><img src="https://img.shields.io/badge/Web-andreafinazzi.com-0b0f19?style=flat-square&logo=google-chrome&logoColor=09F1B8" alt="Website" /></a>
  &nbsp;
  <img src="https://img.shields.io/badge/Layer-Public_Reference-0b0f19?style=flat-square&logo=bookstack&logoColor=09F1B8" alt="Public reference" />
  &nbsp;
  <img src="https://img.shields.io/badge/Pine_Source-Private-0b0f19?style=flat-square&logo=lock&logoColor=8B5CF6" alt="Private Pine" />
</p>

<p><strong>Public reference layer</strong> for cyclical market analysis — optimized T-scale tables by market and length profile.<br>
Full <strong>Matassa Completa</strong> on TradingView is <strong>invite-only</strong>. No indicator source code in this repo.</p>

</div>

<img src="https://raw.githubusercontent.com/andreafinazziinfo/matassa-cycle-framework/main/assets/divider.svg?v=2" width="100%" alt="" />

<br>

## Architecture

```mermaid
flowchart TB
  subgraph public["Public — this repo"]
    T["reference-tables/<br/>T-scale CSV + XLSX"]
    D["docs/"]
  end
  subgraph tv["TradingView — invite"]
    C["Matassa Completa"]
    P["Pattern Matching"]
    S["Statistica"]
  end
  subgraph private["Private"]
    E["Model Entry"]
    L["Cycle Lab Terminal"]
  end
  T --> C
  C --> P
  C --> S
  S --> E
  E --> L
```

| Layer | Access | Contents |
|-------|--------|----------|
| **Reference tables** | Public | MIN → MAX profiles · 6 market calibrations |
| **Matassa Completa** | [TV invite](https://www.tradingview.com/u/AnDr3HA/) | Pivots · FLD/FEMA · swings · multi-cycle |
| **Advanced modules** | Private / screenshots | Pattern · statistics · strategy |
| **Cycle Lab** | Private product | Execution · terminal · backtest |

<img src="https://raw.githubusercontent.com/andreafinazziinfo/matassa-cycle-framework/main/assets/divider.svg?v=2" width="100%" alt="" />

<br>

## What's included

| Asset | Description |
|-------|-------------|
| [`reference-tables/`](reference-tables/) | T-scale duration tables (5 profiles × 6 markets) |
| [`docs/framework-overview.md`](docs/framework-overview.md) | Stack overview |
| [`docs/using-reference-tables.md`](docs/using-reference-tables.md) | How to read the tables |
| [`assets/screenshots/`](assets/screenshots/) | TradingView previews (images only) |

### Length profiles

| Profile | Factor | Use when |
|---------|--------|----------|
| `min-0-6875x` | 0.6875× | Cycles compress / high volatility |
| `c-0-75x` | 0.75× | Slightly short bias |
| **`m-1-0x`** | **1.0×** | **Default baseline** |
| `l-1-25x` | 1.25× | Extended harmonics |
| `max-1-4375x` | 1.4375× | Slow / stretched regimes |

Markets: **Crypto (100%)** reference · Futures/Forex · Forex · Futures · Stock US · Stock EU.

→ Start with [`reference-tables/m-1-0x.csv`](reference-tables/m-1-0x.csv)

<img src="https://raw.githubusercontent.com/andreafinazziinfo/matassa-cycle-framework/main/assets/divider.svg?v=2" width="100%" alt="" />

<br>

## Visual preview (TradingView)

Screenshots only — **no Pine source**. Full suite: [@AnDr3HA](https://www.tradingview.com/u/AnDr3HA/) (invite-only).

### Matassa Completa
Pivots, centratura, FLD/FEMA, cycle bands, multi-timeframe targets.

<img src="https://raw.githubusercontent.com/andreafinazziinfo/matassa-cycle-framework/main/assets/screenshots/completa-overview.png?v=2" width="100%" alt="Matassa Completa" />

### Matassa 3 Cicli
Three synchronized cycle layers (+2 / 0 / -2) on one chart.

<img src="https://raw.githubusercontent.com/andreafinazziinfo/matassa-cycle-framework/main/assets/screenshots/three-cycles.png?v=2" width="100%" alt="Matassa 3 Cicli" />

### Matassa Statistica
Statistical projections, heatmap distribution, accuracy tables.

<img src="https://raw.githubusercontent.com/andreafinazziinfo/matassa-cycle-framework/main/assets/screenshots/statistica.png?v=2" width="100%" alt="Matassa Statistica" />

### Matassa Pattern Matching
Historical shape matching (KNN / DTW), similarity ranking, walk-forward backtest.

<img src="https://raw.githubusercontent.com/andreafinazziinfo/matassa-cycle-framework/main/assets/screenshots/pattern-matching.png?v=2" width="100%" alt="Matassa Pattern Matching" />

<img src="https://raw.githubusercontent.com/andreafinazziinfo/matassa-cycle-framework/main/assets/divider.svg?v=2" width="100%" alt="" />

<br>

## Quick start

1. Open [`reference-tables/m-1-0x.csv`](reference-tables/m-1-0x.csv).
2. Pick your market column (e.g. `CRYPTO (100%)`).
3. Read [`docs/using-reference-tables.md`](docs/using-reference-tables.md).

## Request access

- **TradingView:** [@AnDr3HA](https://www.tradingview.com/u/AnDr3HA/) — [andreafinazzi.com](https://andreafinazzi.com) · [email](mailto:andrea.finazzi.info@gmail.com)
- **Cycle Lab terminal:** via website

## License

Reference tables: [LICENSE](LICENSE) — personal / educational use. No commercial redistribution without permission.

<br>

<div align="center">

**Andrea Finazzi** — Quantitative Architect

[Profile](https://github.com/andreafinazziinfo) · [matassa-cycle-framework](https://github.com/andreafinazziinfo/matassa-cycle-framework) · [claude-statusline-pro](https://github.com/andreafinazziinfo/claude-statusline-pro)

</div>

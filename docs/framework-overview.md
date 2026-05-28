# Framework Overview

## Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Cycle Lab Terminal (private)                               │
│  Execution · backtest · agent ops · live workspace          │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  Matassa Advanced Modules (private / TV invite)             │
│  Pattern Matching · Statistica · Model Entry                │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  Matassa Completa (TradingView — invite-only)               │
│  Pivots · centratura · swings · FLD/FEMA · multi-cycle UI   │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  Reference Tables (this repo — public)                        │
│  T-scale durations · market calibration · length profiles   │
└─────────────────────────────────────────────────────────────┘
```

## T-scale

The T-scale anchors analysis to a **nominal weekly cycle (T)** and expresses longer harmonics as T+n:

| Label | Typical name |
|-------|----------------|
| T | Weekly |
| T+1 | Bi-weekly |
| T+2 | Monthly |
| T+3 | Quarterly |
| T+4 | Semi-annual |
| T+5 | Annual |
| … | … |
| T+10 | 32-year |

Actual bar counts adapt to **timeframe**, **market type**, and **length profile** (see reference tables).

## Three-engine flywheel (product context)

| Engine | Role |
|--------|------|
| **Titan** | Quant research & cycle insight |
| **Control Plane** | Agent orchestration & dev workflow |
| **Cycle Lab** | Product, terminal, execution |

This public repo supports the **research narrative** only — not the proprietary engines.

## What we deliberately omit

- Pivot detection & centratura algorithms
- Swing confirmation rules
- FLD / FEMA / overlay math
- Pattern matching & KNN projection
- Statistical cycle engines
- Strategy entries & position logic

Those layers justify invite-only / private access.

# Using the Reference Tables

## 1. Choose market

Identify the asset class:

- **Crypto** — use `CRYPTO (100%)` column (reference baseline)
- **Forex / Futures** — use the dedicated column or the blended `FUTURES/FOREX` column
- **Equities** — `STOCK USA` or `STOCK EU` depending on listing

## 2. Choose length profile

Start with **M (1.0×)**. Move to:

- **C or MIN** if cycles appear systematically shorter than table expectations
- **L or MAX** if cycles stretch beyond M durations

## 3. Read a row

Example from `m-1-0x.csv`, row `T+2 (MENSILE)`:

| Market | Duration |
|--------|----------|
| Crypto | 45g 12h 15m |
| Stock USA | 8g 18h 48m |

Interpret as the **expected nominal length** of the monthly harmonic on that market, in trading time.

## 4. Practical workflow (manual)

1. Mark the last confirmed cycle pivot on your chart.
2. Look up the target harmonic (e.g. T+2) for your market and profile.
3. Project forward by the table duration as a **time window**, not a guaranteed turn.
4. Refine with price action — tables are calibration references, not signals.

## 5. What the full Matassa stack adds (private)

The closed-source indicators automate:

- Pivot & potential-pivot detection
- Centratura confirmation
- Multi-cycle overlay (3 Cicli)
- FLD/FEMA and target bands
- Pattern matching vs historical shapes
- Statistical forward projections
- Model Entry backtests

This repo gives you the **time ruler**. The indicators draw and update it on the chart.

## 6. Caveats

- Durations are in **trading days**, not calendar days.
- Calibration factors encode market microstructure; they are not universal constants.
- Do not treat table values as financial advice or guaranteed reversal dates.

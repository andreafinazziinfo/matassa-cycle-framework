# Reference Tables — T-Scale Cycle Durations

Optimized lookup tables for cyclical analysis across asset classes.

## Files

| File | Profile | Factor |
|------|---------|--------|
| `min-0-6875x.csv` | MIN | 0.6875× |
| `c-0-75x.csv` | C | 0.75× |
| `m-1-0x.csv` | M | 1.0× (baseline) |
| `l-1-25x.csv` | L | 1.25× |
| `max-1-4375x.csv` | MAX | 1.4375× |
| `TABELLE.xlsx` | All sheets | Original workbook |

## Column guide

| Column | Meaning |
|--------|---------|
| `Ciclo` | T-scale label (T = weekly anchor, T+n = longer harmonics) |
| `FUTURES/FOREX (70.3%)` | Blended futures/forex calibration |
| `CRYPTO (100%)` | Reference market (baseline = 100%) |
| `FOREX (71.4%)` | Spot FX calibration |
| `FUTURES (68.5%)` | Futures-only calibration |
| `STOCK USA (19.3%)` | US equities calibration |
| `STOCK EU (25.3%)` | EU equities calibration |

Percentages in headers are **cross-market scaling factors** relative to Crypto, not win rates or accuracy metrics.

## Duration format

Values use **trading days** (`g`), hours (`h`), minutes (`m`):

```
8192g 8h 6m  →  8192 trading days + 8 hours + 6 minutes
11g          →  11 trading days
```

## Which profile to use

| Profile | When |
|---------|------|
| **M (1.0×)** | Default starting point for most analysis |
| **C / MIN** | Faster cycles, higher volatility, shorter swings |
| **L / MAX** | Slower cycles, extended harmonics, macro framing |

Switch profile when the active market regime clearly compresses or stretches cycle length versus the M baseline.

## Public vs optimized

Nominal Hurst/Gann cycle names (weekly, monthly, quarterly, etc.) are widely documented.  
What is **specific to Matassa** here:

- Cross-market calibration percentages in column headers
- Length profile multipliers (MIN → MAX)
- Unified T-scale mapping across all six market columns

The indicator logic that *detects* and *projects* cycles from price is **not** included in this repository.

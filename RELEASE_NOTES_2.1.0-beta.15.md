# 2.1.0-beta.15 – Forecast remaining-energy normalization

Beta 15 fixes an inconsistency discovered after the Beta 14 intraday SOC-plan
rebasing was used in real operation.

## Problem

Forecast.Solar provides two related representations of the remaining solar
forecast:

- `energy_production_today_remaining`, which is the remaining energy total, and
- the native time-resolved power curve, whose future area describes the expected
  distribution over time.

Beta 14 rebased the SOC plan at the current measured SOC and then integrated only
the future part of the native power curve. In some situations the integrated
future curve area differed materially from the remaining-energy sensor value.

This could produce a contradictory state such as:

```text
Effective remaining forecast: positive
Planned end SOC: current SOC
Saved SOC plan: flat
```

The normal optimizer calculations still saw forecast energy, while the rebased
SOC plan could treat the usable remaining energy as zero after the configured
forecast safety reserve was applied.

## Normalized remaining-energy budget

Beta 15 separates energy amount from time distribution:

```text
energy_production_today_remaining
        -> authoritative remaining energy

native Forecast.Solar power curve
        -> time-distribution shape
```

At the active Beta 14 intraday anchor, the optimizer integrates the future native
power curve and scales its cumulative energy so that the complete future area
matches the effective remaining-energy sensor value.

Forecast safety reserve and charging efficiency are applied only after this
normalization. The resulting SOC gain is still limited by configured battery
capacity and target SOC.

## Result

The following values now use a consistent remaining-energy budget:

- effective remaining forecast
- rebased dynamic SOC schedule
- saved SOC plan
- forecast-based planned end SOC

The native power curve still determines how the planned SOC gain is distributed
through the remaining hours of the day.

## Fallback behavior

If `energy_production_today_remaining` is unavailable, the Beta 14 native-curve
integration remains the fallback.

If the native forecast contains no usable future curve shape, Beta 15 does not
invent a synthetic charging profile from an energy total alone. The plan remains
flat until a usable native curve becomes available again.

## Existing protections

Beta 15 keeps the existing behavior unchanged:

- intraday plan rebasing only on genuine Forecast.Solar source/curve changes
- no continuous rebasing on ordinary optimizer refreshes
- same-day Forecast.Solar curve cache for short runtime gaps
- forecast safety reserve and charging efficiency
- predictive SOC-release hysteresis
- NOAH offline command/source/PV-learning guards
- expected minimum-SOC night shutdown handling

## Version

```text
2.1.0-beta.15
```

Base: `main` commit `80763c57ca8d42f956aca5095bbfcfa1c189b6bc`
(`2.1.0-beta.14`).

No dashboard-template migration and no translation migration are required.

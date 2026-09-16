# 2.1.0-beta.16 – NOAH-specific energy-flow visualization

Beta 16 replaces the generated Power Flow Card Plus energy-flow card with a
bundled NOAH-specific card.

## Problem

The previous dashboard used Power Flow Card Plus with separate PV, battery and
home entities. That card assumes a generic AC-coupled topology and derives some
line flows from the available source values.

The Growatt NOAH topology is different: PV power enters the NOAH on the DC side,
while only the measured NOAH AC output can supply the house. Small differences
between PV input and battery charging power could therefore be shown as a false
PV-to-house flow even when `output_power` was exactly `0 W`.

Typical contradictory display:

```text
PV power:       38 W
Charging power:  0 W
NOAH output:     0 W
Grid import:   325 W
Home load:     325 W
```

The old card could still animate PV power toward the house although the measured
AC output proved that the house was fully supplied by the grid.

## Dedicated NOAH topology

The bundled `custom:noah-energy-flow-card` uses explicit measured paths:

```text
Grid <-> Home        = grid_import / grid_export
PV -> NOAH           = solar_power
NOAH -> Home         = output_power
NOAH battery details = charging_power / discharging_power / SOC
Home value           = home_load
```

The NOAH-to-home path is therefore driven **only** by `output_power`.

If `output_power = 0 W`, no NOAH-to-home flow is animated regardless of the
difference between PV input and battery charging power.

This also keeps PV conversion losses, NOAH internal consumption and sensor
resolution differences from being misrepresented as household supply.

## Bundled frontend card

The energy-flow card is shipped with the integration and registered as a
Lovelace module in the same way as the bundled historical SOC card.

Power Flow Card Plus is no longer required for the generated NOAH Optimizer
dashboard. ApexCharts Card is still required for the chart cards.

## Dashboard migration

Dashboard template version 20 replaces only a recognized generated legacy
`custom:power-flow-card-plus` card with the bundled NOAH energy-flow card.

Recognition requires the standard generated title and the expected NOAH entity
mapping. Unrelated or user-created Power Flow Card Plus cards are left unchanged.

Newly created dashboards also receive the bundled energy-flow card immediately.

## Safety

This update changes dashboard visualization only.

- no controller calculation is changed
- no NOAH output command path is changed
- no Forecast.Solar calculation is changed
- no SOC planning or release logic is changed
- offline protection remains unchanged

## Version

```text
2.1.0-beta.16
```

Base: `main` commit `a67c3f3a3678391562b86e9bc945d076ed3e3b5e`
(`2.1.0-beta.15`).

No entity or translation migration is required. The dashboard migrates to
template version 20 automatically.

# 2.1.0-beta.17 – Energy-flow card redesign

Beta 17 refines the bundled NOAH energy-flow card introduced in Beta 16.

## Motivation

Beta 16 fixed the data model by coupling **NOAH → Home** exclusively to the
measured `output_power`, but the first dedicated frontend card was visually
more technical and less readable than the previous Power Flow Card Plus view.

Beta 17 keeps the corrected NOAH topology while restoring the compact four-node
layout users are familiar with.

## Redesigned layout

The card again uses four primary nodes:

```text
                  PV
                  |
                  v
Grid <---------- NOAH ----------> Home
```

The actual rendered layout keeps Grid and Home on the horizontal household bus,
PV above and NOAH below, matching the established dashboard arrangement.

The NOAH circle shows:

- battery SOC
- measured AC output
- charging power
- discharging power

This keeps the card compact without adding a separate technical inverter node.

## Explicit flow sources

The visual paths remain tied to measured entities:

```text
Grid -> Home  = grid_import
Home -> Grid  = grid_export
PV -> NOAH    = solar_power
NOAH -> Home  = output_power
```

Charging and discharging values are displayed inside the NOAH node and are not
used to infer the NOAH-to-home flow.

Therefore `output_power = 0 W` still guarantees that no NOAH-to-home flow is
animated, regardless of differences between PV input and battery charging
power.

## Visual changes

- return to four large circular nodes
- restore the familiar Grid / PV / Home / NOAH arrangement
- replace dashed animated lines with smooth moving flow dots
- remove the separate output label floating on the connection line
- display output, charging and discharging values compactly inside the NOAH node
- preserve the established dashboard colors

## Frontend cache

The bundled energy-flow card resource version is increased from `v=1` to
`v=2`, so Home Assistant updates the stored Lovelace resource URL and browsers
load the redesigned frontend module instead of a cached Beta-16 copy.

## Safety

This is a frontend-only redesign. It does not modify:

- controller calculations
- output commands
- Forecast.Solar processing
- SOC planning or release
- PV learning
- offline protection

## Version

`2.1.0-beta.17`

Base: `main` commit `b1085752d8148833d1ebb5cb67e5788f7119e500`
(`2.1.0-beta.16`).

No entity, translation or dashboard-template migration is required.

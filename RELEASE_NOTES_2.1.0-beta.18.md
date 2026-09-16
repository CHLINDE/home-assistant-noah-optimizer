# 2.1.0-beta.18 – Energy-flow visual refinement

Beta 18 refines the bundled NOAH energy-flow card after the Beta 17 redesign.

## Motivation

Beta 17 restored the familiar four-node Grid / PV / Home / NOAH layout while
keeping the corrected Beta 16 measurement model. In practice the card could
still look visually busy and the crossing between the PV path and the household
AC bus could be mistaken for a connection.

Beta 18 keeps the same measurements and topology but simplifies the rendering.

## Layout

The card keeps the established arrangement:

```text
                  PV
                  |
                  v

Grid ---------------------------- Home
                   \            /
                    \          /
                     NOAH ----
```

The rendered PV path crosses the household AC bus with a small visual bridge.
This crossing is therefore clearly shown as **not electrically connected**.

## Flow animation

Each active path now uses a single subtle moving marker:

- Grid -> Home or Home -> Grid
- PV -> NOAH
- NOAH -> Home

Inactive paths remain visible as neutral base lines.

This reduces visual clutter compared with the multiple moving markers used in
Beta 17.

## Explicit measured flow sources

The measurement model remains unchanged:

```text
Grid -> Home = grid_import
Home -> Grid = grid_export
PV -> NOAH   = solar_power
NOAH -> Home = output_power
```

`output_power` remains the exclusive source for the NOAH-to-home path.

If `output_power = 0 W`, no NOAH-to-home flow is animated regardless of PV,
charging or discharging values.

## NOAH node

The NOAH node continues to show:

- battery SOC
- measured AC output
- charging power
- discharging power

These values are displayed compactly and are not used to infer additional
household supply.

## Frontend cache

The bundled energy-flow card resource is increased from:

```text
v=2
```

to:

```text
v=3
```

so Home Assistant and browsers load the refined card after the update.

## Safety

This release changes visualization only.

It does not modify:

- controller calculations
- output commands
- Forecast.Solar processing
- forecast normalization
- SOC planning
- SOC release logic
- PV learning
- offline protection

## Version

`2.1.0-beta.18`

Base: `main` commit `824c11432f53cebc3a13103e4b4255d5593760b4`
(`2.1.0-beta.17`).

No entity, translation or dashboard-template migration is required.

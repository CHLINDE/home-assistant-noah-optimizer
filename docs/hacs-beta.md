# HACS Beta / Pre-Release

## Current versions

Stable:

```text
2.0.0
```

Current pre-release:

```text
2.1.0-beta.8
```

## Install pre-releases

Add the repository to HACS as an Integration and enable pre-release versions
for this repository.

After every integration update restart Home Assistant completely.

## Beta 8 purpose

Beta 8 is a dashboard-migration correction.

It does not change optimizer calculations or active-control decisions.

### Problem

Earlier dashboard-color migrations updated templates, but existing stored
dashboards could keep stale explicit series colors.

### Solution

Dashboard template storage version is increased:

```text
17 -> 18
```

The v18 migration updates explicit colors only on recognized generated NOAH
standard ApexCharts.

Recognition uses:

- known German/English title
- expected entity set
- for the PV forecast card, known raw/effective forecast data generators

User-created/additional ApexCharts are left untouched.

## Standard palette

```text
Blue    #2196F3
Green   #009B21
Orange  #FF6A00
Yellow  #FFD800
Cyan    #00FFFF
Violet  #B200FF
```

Controller behavior:

```text
Controller target            Blue
Actual output                Green
Self-consumption target      Orange
Charge-priority target       Yellow
Required charging power      Cyan
Dynamic catch-up power       Violet
```

Historical SOC:

```text
Actual SOC       Blue
Dynamic target   Green
Target SOC       Orange
Saved plan       Yellow
```

The bundled history-card resource cache version is increased to `v8`.

## Automatic dashboard

The integration creates and owns the `NOAH Optimizer` Lovelace dashboard.

Entity IDs are resolved from Home Assistant's entity registry.

Initial language:

- German -> `dashboard_de.yaml`
- other languages -> `dashboard_en.yaml`

## Dashboard migration history

```text
8   Dynamic SOC
9   Beta-8 Jinja repair
10  Predictive SOC release
11  Night state / PV diversion / controller status
12  PV learning
13  SOC schedule hold
14  Forecast.Solar curve
15  Bundled SOC history card
16  Explicit standard colors
17  Final color alignment
18  Correct stale explicit colors on recognized standard charts
```

Migrations are selective. A stored dashboard is not replaced wholesale.

## History card

The date-selectable SOC history card is bundled with the integration.

Home Assistant dependencies:

- frontend
- history
- http
- websocket_api
- lovelace

The card uses Recorder history for actual historical states.

Saved forecast/plan snapshots are diagnostic only.

## PV learning

PV learning:

- runs passively
- stores learning history
- uses a median of up to seven valid days
- requires at least three valid days before application
- is opt-in for forecast correction

## Forecast curve

When the configured remaining-forecast sensor belongs directly to
Forecast.Solar, the optimizer reuses Forecast.Solar runtime data.

No additional Forecast.Solar API calls are made.

Fallback:

```text
daylight_fallback
```

## Active control

Active control remains opt-in.

Controller safeguards include:

- deadband
- command interval
- retry
- failsafe
- legacy YAML interlock

Predictive SOC release is also separately opt-in.

## Upgrade test for beta.8

After restart verify:

1. Dashboard loads.
2. Controller-behavior colors match the standard palette.
3. Historical SOC card uses blue/green/orange/yellow.
4. Other standard charts use consistent colors.
5. A user-created ApexCharts card is not changed.
6. Optimizer/controller behavior is otherwise identical to beta.7.

## Rollback

If a beta must be rolled back, install the previous release through HACS and
restart Home Assistant.

The dashboard storage version may already have been migrated. The v18
migration only changes recognized standard series colors and does not add
active-control state.

## Legacy YAML

Do not actively control the same NOAH from both the legacy YAML optimizer and
the HACS integration.

The integration checks the legacy helper and blocks conflicting writes.

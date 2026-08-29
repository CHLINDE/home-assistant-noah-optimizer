# HACS Beta / Pre-Release

Stable release:

```text
2.0.0
```

Current pre-release:

```text
2.1.0-beta.8
```

## Direct HACS repository button

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

Enable pre-release versions in HACS and restart Home Assistant after every
integration update.

## 2.1 beta overview

### Beta 1

PV learning:

- passive learning
- median of up to seven valid days
- minimum three days
- optional application
- disabled by default

### Beta 2

SOC schedule hold:

- prevents unnecessary charge priority once the dynamic plan is satisfied
- uses current PV for household demand
- does not intentionally release battery energy

### Beta 3

Time-resolved Forecast.Solar:

- reuses Home Assistant runtime forecast
- no additional API calls
- shapes dynamic SOC schedule
- daylight fallback remains available

### Beta 4

Historical SOC schedule:

- date selection
- Recorder history
- saved plan snapshots
- rolling retention
- bundled frontend card

### Beta 5 to Beta 7

Standardized dashboard-series palette.

### Beta 8

Corrects stale explicit colors in existing stored dashboards.

```text
Dashboard template 17 -> 18
```

Recognition requires:

- known title
- expected entity set
- PV forecast additionally checks known data generators

Custom ApexCharts remain untouched.

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

History-card cache:

```text
v8
```

## Dynamic SOC

Fallback:

```text
p = elapsed daylight / daylight duration
```

```text
time target
= minimum SOC + p × (target SOC - minimum SOC)
```

Native Forecast.Solar source uses the time-resolved curve.

## Predictive SOC release

Separate refill reserve:

```text
effective remaining forecast - additional energy reserve
```

Expected household energy is intentionally not deducted here.

## PV diversion

```text
diversion power
= min(grid import, battery charging power)
```

## Controller cadence

```text
evaluation                              15 s
normal command interval                120 s
soc_release/pv_redirect increases       30 s
```

## Controller status

Typical raw states:

```text
disabled
optimizer_disabled
legacy_controller_active
critical_data_missing
actuator_unavailable
target_unavailable
rate_limited
waiting_for_retry
in_sync
command_sent
command_failed
failsafe
```

## Dashboard migration history

```text
8   Dynamic SOC
9   Jinja repair
10  Predictive SOC release
11  Night / PV diversion / controller status
12  PV learning
13  SOC schedule hold
14  Forecast.Solar curve
15  SOC history card
16  Standard series colors
17  Final color alignment
18  Stored-color migration fix
```

## Upgrade test

After Beta 8 restart:

1. Dashboard loads.
2. Controller behavior uses six standard colors.
3. Historical SOC uses blue/green/orange/yellow.
4. Other standard charts are consistent.
5. Custom ApexCharts are unchanged.
6. Optimizer behavior is unchanged.

## Rollback

Install the previous release through HACS and restart.

## Legacy YAML

Never control the same NOAH simultaneously from legacy YAML and the HACS
integration.

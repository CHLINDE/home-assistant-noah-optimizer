# HACS pre-release / beta channel

Stable release: `2.0.0`

Current pre-release: `2.1.0-beta.8`

The 2.1 beta line builds on the stable 2.0.0 controller and adds PV learning,
SOC schedule hold, time-resolved Forecast.Solar planning and the date-selectable
SOC schedule history view.

`2.1.0-beta.8` repairs the stored-dashboard color migration. Recognized
generated NOAH standard charts are realigned to the documented palette with
dashboard template version 18; unrelated custom ApexCharts cards are preserved.

## Installing the pre-release in HACS

Add the repository as a custom HACS integration repository if it is not already
installed:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Enable pre-release versions for the repository and install:

```text
2.1.0-beta.8
```

Restart Home Assistant completely after updating.

## 2.1 beta features

### PV learning

PV learning compares measured daily NOAH PV energy with Forecast.Solar and
stores a robust learned correction factor. Applying the learned correction is
opt-in.

### Hold SOC schedule

The `soc_hold` controller mode prevents the legacy forecast-margin logic from
selecting charge priority again when the dynamic SOC schedule is already
satisfied. The mode is PV-only and does not intentionally discharge the
battery.

### Time-resolved Forecast.Solar SOC schedule

When the configured remaining-forecast entity belongs directly to
Forecast.Solar, the optimizer reuses Home Assistant's loaded time-resolved power
curve. No additional Forecast.Solar API requests are made.

The effective forecast curve applies the configured forecast factor and, when
enabled and ready, the learned PV factor. Charging efficiency and energy reserve
remain part of SOC planning. Expected household demand remains separate in
forecast-margin and output control.

If a native Forecast.Solar curve cannot be resolved, the existing daylight
fallback is used.

### Historical SOC schedule

The bundled history card can browse dates and compare recorded actual SOC,
recorded dynamic target, recorded target SOC and stored forecast/plan snapshots.
Snapshots are diagnostic and do not affect active control.

## Dashboard color migration repair in 2.1.0-beta.8

Beta 8 increases the dashboard template version from 17 to 18. The previous
migration skipped every series that already had an explicit `color` value, so
older generated colors could remain visible after an update.

Template 18 realigns only recognized generated NOAH standard charts, identified
by their known chart title and entity set. Additional/user-created ApexCharts
cards are left untouched.

The bundled history-card resource URL is bumped from `v=7` to `v=8` to
invalidate cached frontend code.

Stable palette:

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
Controller target              Blue
Actual output                  Green
Self-consumption target        Orange
Charge-priority target         Yellow
Required charging power        Cyan
Dynamic catch-up power         Violet
```

Historical SOC schedule:

```text
Actual SOC                     Blue
Dynamic target                 Green
Target SOC                     Orange
Saved historical plan          Yellow
```

## Automatic dashboard

The integration-managed Lovelace dashboard uses dynamically resolved entity IDs
and is stored by the integration. Existing dashboards are migrated selectively
instead of being fully replaced.

Current dashboard template version:

```text
18
```

## Safe update procedure

Before evaluating a new pre-release, it is recommended to disable active NOAH
control. After the restart, first verify source values, controller diagnostics,
SOC planning and dashboard output before re-enabling active control.

`2.1.0-beta.8` itself does not change optimizer calculations or active-control
logic.

## Version history

### 2.1.0-beta.8

- Repairs stored standard-chart colors that Beta 7 could leave unchanged
- Increases dashboard template version from 17 to 18
- Realigns only recognized generated NOAH standard ApexCharts cards
- Preserves unrelated custom/additional ApexCharts cards
- Increases bundled history-card cache version from `v=7` to `v=8`
- Sets the integration manifest version to `2.1.0-beta.8`

### 2.1.0-beta.7

- Final generated-chart color alignment before the migration repair
- Dashboard template version 17
- History-card cache `v=7`

### 2.1.0-beta.4

- Date-selectable historical SOC schedule card
- Recorder-backed SOC history
- Persistent forecast/plan snapshots

### 2.1.0-beta.3

- Native time-resolved Forecast.Solar curve planning
- Forecast curve diagnostics and chart
- Daylight fallback when native runtime data is unavailable

### 2.1.0-beta.2

- `soc_hold` / Hold SOC schedule controller mode
- Prevents duplicate forecast-margin charge priority when schedule is satisfied

### 2.1.0-beta.1

- Passive PV learning
- Persistent learning history
- Opt-in learned PV correction

### 2.0.0

- First stable 2.x release, functionally matching tested `2.0.0-beta.14`

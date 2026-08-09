# HACS Beta

Current beta: `2.0.0-beta.8`

## Direct HACS repository button

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

The button uses My Home Assistant to open this custom integration repository in
HACS.

## Dynamic SOC plan

Starting with `2.0.0-beta.8`, the integration calculates a dynamic minimum SOC
for the current point in time.

The goal is to answer:

> How much SOC should the battery already have now so that the configured
> target SOC can still be reached by sunset with the conservatively expected
> remaining PV energy?

The calculation considers:

- effective remaining PV forecast
- expected household energy demand until sunset
- additional energy reserve
- usable battery capacity
- charging efficiency
- minimum SOC
- target SOC

Simplified:

```text
PV energy available for battery
= effective remaining forecast
  - expected household energy
  - additional energy reserve

possible SOC gain
= available PV energy × charging efficiency
  / battery capacity × 100

dynamic SOC target
= target SOC - possible SOC gain
```

The dynamic SOC target is clamped between minimum SOC and target SOC.

### SOC deviation

```text
SOC deviation = actual SOC - dynamic SOC target
```

A tolerance of 2 percentage points is used:

```text
> +2 percentage points = ahead
-2 ... +2             = on_track
< -2                  = behind
```

### Dynamic catch-up power

When the battery is behind schedule, Beta 8 calculates the charging power
required to recover the SOC shortfall within the configured **SOC catch-up
time**.

Default catch-up time:

```text
2.0 h
```

The effective catch-up window is never longer than the remaining time until
sunset.

### Safe opt-in

The new switch:

```text
Dynamic SOC control
```

is disabled by default.

The dynamic SOC sensors are calculated even when this switch is off, allowing
the feature to be observed before it influences the output target.

Dynamic SOC control can affect the output target only when:

- optimizer calculation is enabled
- operating mode is `automatic`
- dynamic SOC control is enabled
- forecast data is available
- it is daytime
- SOC is above minimum SOC
- SOC is below target SOC
- the battery is more than 2 percentage points behind the dynamic SOC target

Manual, self-consumption, and charge-priority modes are not changed by the new
feature.

When active, the controller mode is:

```text
soc_catchup
```

## Automatic dashboard

Starting with `2.0.0-beta.6`, the integration creates a dedicated Lovelace
dashboard panel named **NOAH Optimizer**.

The panel is shown in the sidebar by default.

For new installations, sidebar visibility can be selected during setup. When
upgrading from a version that did not yet contain the setting, the missing
value defaults to enabled.

The dashboard resolves integration entities dynamically through Home
Assistant's entity registry, so area-based prefixes and user-renamed entity IDs
do not need to be known in advance.

The dashboard configuration is stored by the integration itself. It is not
created through a second Home Assistant `DashboardsCollection`.

The initial dashboard language follows the Home Assistant language:

- German -> `dashboard_de.yaml`
- all other languages -> `dashboard_en.yaml`

### Beta 8 dashboard migration

Beta 8 introduces dashboard template version 8.

Existing Beta 6 and Beta 7 dashboards are migrated selectively rather than
replaced. The migration can add the new dynamic SOC controls and sensors while
preserving unrelated user changes.

If the exact old Beta 6 battery mapping is still present, it is corrected to
the Beta 7 mapping during migration.

### Dashboard requirements

The enhanced dashboard requires:

- Power Flow Card Plus
- ApexCharts Card

These frontend cards are separate HACS dashboard components and are not
installed automatically.

The optimizer itself continues to operate if they are missing.

## Dashboard energy flow

### Grid

```text
consumption = grid import
production  = grid export
```

### NOAH battery

```text
consumption = discharging power
production  = charging power
```

This results in:

```text
Charging power    -> energy flows into the NOAH battery
Discharging power -> energy flows out of the NOAH battery
```

## Required source entities

The configuration flow asks for:

- signed grid power
- NOAH Solar Power
- NOAH Output Power
- NOAH SOC
- NOAH Charging Power
- NOAH Discharge Power
- Forecast.Solar remaining energy today
- NOAH System Output Power

The `NOAH System Output Power` entity must be a writable `number` entity.

## Supported units

Power:

- W
- kW

Energy:

- Wh
- kWh

Battery state of charge:

- %

## Grid sign

Expected convention:

```text
positive = grid import
negative = grid export
```

If the source sensor uses the opposite convention, enable
`Invert grid power sign` during setup.

## Active control

Starting with Beta 5, the integration can optionally write the calculated
output target to the configured NOAH System Output Power entity using Home
Assistant's `number.set_value` service.

Three switches are now available:

- `Optimizer calculation enabled`
- `Active NOAH control`
- `Dynamic SOC control`

Active NOAH control and dynamic SOC control are disabled by default.

The active controller includes:

- configurable command deadband
- minimum interval between normal output commands
- retry handling
- failsafe after prolonged loss of critical data
- persistent Home Assistant failsafe notification
- legacy YAML controller interlock

Beta 8 does not change the low-level write controller in `control.py`. The new
logic changes only the calculated target when the dynamic feature is explicitly
enabled.

## Legacy YAML interlock

The HACS controller checks:

```text
input_boolean.noah_optimizer_enabled
```

If the entity exists and is `on`, normal HACS output commands are blocked.

## Failsafe

If critical data remains unavailable for ten minutes while active control is
enabled:

1. Home Assistant creates a persistent notification.
2. If the actuator is reachable, the integration attempts to set `0 W`.
3. If the actuator is unavailable, the notification is still created.
4. After data recovery, the failsafe state is reset and the notification is
   dismissed.

## Controller diagnostics

The `Active NOAH control` switch exposes:

- `control_status`
- `last_command_target`
- `last_command_at`

Typical `control_status` values:

- `disabled`
- `optimizer_disabled`
- `legacy_controller_active`
- `critical_data_missing`
- `actuator_unavailable`
- `target_unavailable`
- `rate_limited`
- `waiting_for_retry`
- `in_sync`
- `command_sent`
- `command_failed`
- `failsafe`

## Version history

### 2.0.0-beta.1

Observation-only foundation with source entity selection, unit normalization,
basic energy-flow calculations, and availability checks.

### 2.0.0-beta.2

Improved the Home Assistant integration structure and verified the HACS update
path.

### 2.0.0-beta.3

Ported the legacy YAML optimizer calculation logic to Python. This version was
still observation-only.

### 2.0.0-beta.4

Fixed the missing `select.py` platform and completed the 1:1 calculation
comparison against the legacy YAML optimizer.

### 2.0.0-beta.5

Added optional active output control, rate limiting, retry handling, failsafe
behavior, controller diagnostics, and protection against simultaneous control
by the legacy YAML optimizer.

### 2.0.0-beta.6

Added the integration-managed Lovelace dashboard panel with dynamic entity
resolution, German and English templates, energy-flow visualization, charts,
calibration controls, and diagnostics.

### 2.0.0-beta.7

Corrected the battery energy-flow direction in Power Flow Card Plus and the
related documentation.

### 2.0.0-beta.8

Adds the dynamic SOC plan with:

- dynamic minimum SOC target
- SOC deviation
- ahead/on-track/behind status
- dynamic catch-up charging power
- configurable SOC catch-up time
- separate opt-in dynamic SOC switch
- `soc_catchup` controller mode
- dynamic SOC dashboard chart and diagnostics
- selective migration of existing dashboard configurations
- My Home Assistant HACS repository button in the documentation

## Current limitations

The beta does not yet include:

- learned household load
- multiple independent NOAH systems

Active control should still be treated as beta functionality and monitored
during testing.

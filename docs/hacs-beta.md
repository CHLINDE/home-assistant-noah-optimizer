# HACS Beta

Current beta: `2.0.0-beta.6`

## Automatic dashboard

Starting with `2.0.0-beta.6`, the integration creates a dedicated Lovelace
dashboard panel named **NOAH Optimizer**.

The panel is shown in the sidebar by default.

For new installations, sidebar visibility can be selected during the
integration setup. When upgrading from Beta 5, the missing setting defaults to
enabled.

The dashboard resolves integration entities dynamically through Home
Assistant's entity registry, so area-based prefixes and user-renamed entity IDs
do not need to be known in advance.

The dashboard configuration is stored by the integration itself. It is not
created through a second Home Assistant `DashboardsCollection`.

The default configuration is written only when no stored NOAH dashboard
configuration exists. User changes are therefore preserved across Home
Assistant restarts and integration reloads.

The initial dashboard language follows the Home Assistant language:

- German -> `dashboard_de.yaml`
- all other languages -> `dashboard_en.yaml`

Changing the Home Assistant language later does not overwrite an existing
dashboard.

### Dashboard requirements

The enhanced dashboard requires:

- Power Flow Card Plus
- ApexCharts Card

These frontend cards are separate HACS dashboard components and are not
installed automatically.

The optimizer itself continues to operate if they are missing.

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

## Optimizer calculation

The integration calculates, among other values:

- grid import and grid export
- home load
- battery power
- five-minute grid power average
- hours until sunset
- available battery energy
- required charging energy
- effective remaining PV forecast
- expected household energy demand
- forecast margin and forecast coverage
- required average charging power
- estimated time until target SOC
- self-consumption target
- charge-priority target
- controller mode
- final NOAH output target

The calculation logic was compared with the legacy YAML optimizer in Beta 4.
With identical configuration parameters, the relevant calculated values,
controller mode, and final output target matched the YAML implementation.

## Active control

Starting with Beta 5, the integration can optionally write the calculated
output target to the configured NOAH System Output Power entity using Home
Assistant's `number.set_value` service.

Two separate switches are provided:

- `Optimizer calculation enabled`
- `Active NOAH control`

Active NOAH control is disabled by default.

The controller includes:

- configurable command deadband
- minimum interval between normal output commands
- retry handling
- failsafe after prolonged loss of critical data
- persistent Home Assistant failsafe notification
- legacy YAML controller interlock

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

Adds the integration-managed Lovelace dashboard panel with:

- sidebar visibility enabled by default
- optional sidebar selection during initial setup
- dynamic entity resolution
- German and English default templates
- separate grid import/export display
- separate battery charging/discharging display
- controller status and command diagnostics
- forecast and controller charts
- calibration and diagnostic controls

## Current limitations

The beta does not yet include:

- dynamic SOC target curves
- learned household load
- multiple independent NOAH systems

Active control should still be treated as beta functionality and monitored
during testing.

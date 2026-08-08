# HACS Integration Beta

## Current beta: 2.0.0-beta.5

The HACS integration has progressed from observation-only testing to optional
active NOAH output control.

Active control is disabled by default and must be enabled explicitly.

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

- positive = grid import
- negative = grid export

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

## Active control in Beta 5

Beta 5 can optionally write the calculated output target to the configured
NOAH System Output Power entity using Home Assistant's `number.set_value`
service.

Two separate switches are provided:

- `Optimizer calculation enabled`
- `Active NOAH control`

Active NOAH control is disabled by default, including after updating from an
earlier beta.

The active controller includes:

- configurable command deadband
- a minimum interval between normal output commands
- retry handling if the requested setpoint was not applied
- a failsafe after prolonged loss of critical measurement data
- a persistent Home Assistant notification when the failsafe delay is reached
- a software interlock against the legacy YAML optimizer

## Legacy YAML interlock

The HACS controller checks the legacy YAML helper:

`input_boolean.noah_optimizer_enabled`

If that entity exists and is `on`, HACS active control is blocked and no normal
NOAH output command is sent by the HACS controller.

Before enabling HACS active control, switch the legacy YAML optimizer off.

## Failsafe behavior

If critical measurement data is unavailable continuously for ten minutes while
HACS active control is enabled:

1. Home Assistant creates a persistent notification.
2. If the configured NOAH System Output Power entity is reachable, the
   integration attempts to set it to `0 W`.
3. If the actuator is unavailable, the notification is still created and the
   integration keeps checking on subsequent control cycles.
4. When critical measurement data recovers, the failsafe state is reset and
   the persistent notification is dismissed.

## Controller diagnostics

The `Active NOAH control` switch exposes diagnostic attributes including:

- `control_status`
- `last_command_target`
- `last_command_at`

Typical `control_status` values include:

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

Improved Home Assistant integration structure and verified the HACS update path
while preserving the existing configuration entry and selected source entities.

### 2.0.0-beta.3

Ported the legacy YAML optimizer calculation logic to Python. This version was
still observation-only.

### 2.0.0-beta.4

Fixed the missing `select.py` platform and completed the 1:1 calculation
comparison against the legacy YAML optimizer.

### 2.0.0-beta.5

Adds optional active output control, rate limiting, retry handling, failsafe
behavior, controller diagnostics, and protection against simultaneous control
by the legacy YAML optimizer.

## Current limitations

The beta does not yet include:

- dynamic SOC target curves
- learned household load
- multiple independent NOAH systems

Active control should still be treated as beta functionality and monitored
closely during testing.

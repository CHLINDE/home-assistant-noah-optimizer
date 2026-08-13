# HACS Beta

Current beta: `2.0.0-beta.13`

## Direct HACS repository button

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

The button uses My Home Assistant to open this custom integration repository in
HACS.

> **Home Assistant 2026.8 and newer:**  
> Home Assistant OS uses port 80 by default for new installations. Home
> Assistant Container continues to use port 8123 by default.
>
> The HACS button itself does not contain the Home Assistant port. If My Home
> Assistant still opens an instance URL containing `:8123`, update the instance
> URL stored by My Home Assistant in the browser.

## Dynamic SOC plan

Beta 10 changes the dynamic SOC calculation into a time-based charging
schedule from sunrise to sunset.

The goal is to answer:

> Where should the battery SOC be at the current point of the daylight period,
> while still reacting earlier when the remaining PV forecast becomes weak?

### Daylight progress

Between sunrise and sunset, the integration calculates a daylight progress
factor `p` from `0` to `1`:

```text
p = elapsed time since sunrise / daylight duration
```

This gives:

```text
sunrise     p = 0
midday      p ≈ 0.5
sunset      p = 1
```

Outside daylight, the SOC schedule uses `p = 0`.

### Time-based SOC target

The base schedule is:

```text
time target
= minimum SOC
  + p × (target SOC - minimum SOC)
```

For a minimum SOC of `10%` and a target SOC of `100%`, the base curve is
approximately:

```text
sunrise          10.0%
25% of daylight  32.5%
50% of daylight  55.0%
75% of daylight  77.5%
sunset          100.0%
```

### Forecast pressure

The remaining PV forecast is still evaluated conservatively:

```text
PV energy available for battery
= effective remaining forecast
  - expected household energy
  - additional energy reserve
```

The possible future SOC gain is:

```text
storable battery energy
= available PV energy × charging efficiency

possible SOC gain
= storable battery energy / battery capacity × 100
```

An internal forecast requirement is then calculated:

```text
forecast requirement
= target SOC - possible SOC gain
```

Beta 8 used this value directly as the dynamic SOC target. With a weak forecast,
that could force the target to `100%` very early in the day.

Beta 10 uses it only as progressive forecast pressure:

```text
forecast pressure
= max(forecast requirement - time target, 0)

dynamic SOC target
= time target + p × forecast pressure
```

The final target is clamped between minimum SOC and target SOC.

This means:

- with sufficient remaining PV, the dynamic target follows the time curve
- with weak remaining PV, the curve rises earlier
- a weak forecast no longer turns directly into a hard 100% target early in the day
- the daylight curve reaches target SOC at sunset
- outside daylight, the dynamic target returns to minimum SOC

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

When the battery is behind schedule, the integration calculates the charging
power required to recover the SOC shortfall within the configured **SOC
catch-up time**.

Default catch-up time:

```text
2.0 h
```

The effective catch-up window is never longer than the remaining time until
sunset.

Beta 12 corrects the catch-up target for the rising daytime SOC curve. Earlier
versions calculated the energy needed to reach only the **current** dynamic SOC
target. Because that target keeps rising during the catch-up interval, the
battery could remain permanently behind schedule even while catch-up was
active.

Beta 12 projects daylight progress to the end of the catch-up window and
evaluates the same dynamic SOC curve at that future point. The current forecast
requirement is kept for this short projection and is recalculated on every
coordinator update.

```text
catch-up target
= dynamic SOC target at the end of the catch-up window

SOC shortfall
= max(catch-up target - actual SOC, 0)

required PV energy
= battery capacity × SOC shortfall / 100 / charging efficiency

dynamic catch-up power
= required PV energy / catch-up window
```

Catch-up control still becomes active only when the battery is more than 2
percentage points behind the **current** dynamic SOC target. The ahead,
on-track, and behind status therefore remains unchanged.

### Safe opt-in

The switch:

```text
Dynamic SOC control
```

is disabled by default for a new setup.

Before updating to the current beta, disable active control and dynamic SOC control:

```text
Active NOAH control
Dynamic SOC control
```

After the update, the new SOC plan sensors can be observed before control is
enabled again.

Dynamic SOC control can affect the output target only when:

- optimizer calculation is enabled
- operating mode is `automatic`
- dynamic SOC control is enabled
- forecast data is available
- it is daytime
- SOC is above minimum SOC
- SOC is below target SOC
- the battery is more than 2 percentage points behind the dynamic SOC target

Manual, self-consumption, and charge-priority modes are not changed by the
dynamic SOC feature.

When active, the controller mode is:

```text
soc_catchup
```

## Predictive SOC release

Beta 11 adds predictive SOC release for situations where the battery is safely
ahead of the charging schedule. The goal is to use part of that safe SOC
surplus for current household demand instead of importing from the grid, while
preserving enough SOC to remain on track for the evening target.

The feature has a separate switch:

```text
Predictive SOC release enabled
```

It is disabled by default and only operates together with dynamic SOC control
in `automatic` mode.

### Forecast-required minimum SOC

Predictive SOC release uses a separate forecast-based refill reserve.

The dynamic charging schedule remains conservative and still calculates its
forecast requirement from:

```text
PV energy for charging schedule
= effective remaining forecast
  - expected household energy
  - additional energy reserve
```

Predictive release answers a different question: how much battery SOC may be
released now if later forecast PV can be reserved for restoring that SOC?

For the release reserve:

```text
PV energy available for refilling
= effective remaining forecast
  - additional energy reserve

storable refill energy
= PV energy available for refilling × charging efficiency

possible refill SOC
= storable refill energy / battery capacity × 100

forecast-required minimum SOC
= target SOC - possible refill SOC
```

The result is clamped between minimum SOC and target SOC.

Expected household energy is intentionally **not deducted from the predictive
release refill reserve**. If necessary, later household demand may be supplied
from the grid while remaining forecast PV is used to restore the battery.

This prevents a full battery from being locked at 100% merely because the
normal forecast margin is negative due to expected household demand.

### SOC release floor

The release floor protects both the active time-based schedule and the
forecast-required minimum SOC:

```text
base release floor
= max(dynamic SOC target, forecast-required minimum SOC)

SOC release floor
= min(base release floor + 2 percentage points, 100%)
```

The extra 2 percentage points use the existing dynamic SOC tolerance as a
safety buffer.

### Releasable battery energy

```text
releasable SOC
= max(actual SOC - SOC release floor, 0)

releasable battery energy
= battery capacity × releasable SOC / 100
```

Only energy above the release floor is considered available for predictive
release.

### SOC release target

When positive grid import exists, the release target is calculated as:

```text
SOC release target
= current NOAH output + current positive grid import
```

The target is limited to maximum output power and then processed through the
normal output step logic.

This aims to reduce current grid import without intentionally requesting
battery export to the grid. Small temporary deviations around zero can still
occur because of output step size, measurement delay, and changing household
load.

### Activation conditions

The `soc_release` controller mode requires all of the following:

- optimizer calculation enabled
- operating mode `automatic`
- dynamic SOC control enabled
- predictive SOC release enabled
- forecast available
- daytime
- actual SOC above the SOC release floor
- releasable battery energy greater than zero
- positive grid import

SOC catch-up is evaluated before SOC release. If the forecast later worsens,
the release floor rises and predictive release stops automatically; dynamic SOC
control can then switch to `soc_catchup` when charging recovery becomes
necessary.

If the previous output command was issued in `soc_release` mode and the new
target must decrease, that reduction bypasses the normal two-minute command
interval and deadband. This prevents a stale high discharge target from
remaining active while the release floor rises or household load falls.

### Forecast-based safety

The release floor is based on two deliberately different forecast views:

```text
Dynamic charging schedule:
remaining forecast - expected household energy - energy reserve

Predictive release refill reserve:
remaining forecast - energy reserve
```

The predictive release calculation assumes that remaining PV may be prioritized
for restoring released battery SOC. Later household demand can therefore cause
grid import if the PV energy is needed for battery refilling.

This is intentional: predictive release uses safe battery headroom for current
household demand and creates capacity for later PV surplus.

The controller does not intentionally discharge below the calculated release
floor. The calculation is still forecast-based and cannot guarantee the evening
target if actual PV production is lower than forecast.

If the previous output command was issued in `soc_release` mode and the new
target must decrease, that reduction bypasses the normal two-minute command
interval and deadband. This prevents a stale high discharge target from
remaining active while the release floor rises or household load falls.

## Beta 12 predictive-release correction

Beta 12 corrects the forecast reserve used by predictive SOC release.

Beta 11 reused the same conservative forecast requirement as the dynamic
charging schedule. That calculation deducted expected household energy and
could therefore raise the forecast-required minimum SOC to the target SOC even
when a full battery still had forecast PV available for later refilling.

Beta 12 separates the two forecast views:

```text
Dynamic charging schedule:
effective remaining forecast
- expected household energy
- additional energy reserve

Predictive release refill reserve:
effective remaining forecast
- additional energy reserve
```

Expected household energy is deliberately not deducted from the predictive
release refill reserve.

The dynamic charging schedule itself is unchanged.

No new entities or dashboard elements are added in Beta 12, so dashboard
template version remains `10`.

## Beta 13 faster predictive-release response

Beta 13 changes only the low-level command cadence used while predictive SOC
release is active. The predictive SOC calculations and release floor remain
unchanged.

The controller is evaluated every 15 seconds. Normal controller modes keep the
existing two-minute minimum command interval, while `soc_release` may increase
the NOAH output target every 30 seconds when a real target change is pending.

During `soc_release`, the effective command deadband is limited to at most
`25 W`; a smaller configured deadband is preserved. Final command-step rounding
remains unchanged. Safety-relevant reductions after a SOC-release command still
bypass the command interval and deadband.

The `rate_limited` controller status is now set only when an actual command is
required but still has to wait for the applicable minimum interval.

No new entities or dashboard elements are added in Beta 13, so dashboard
template version remains `10`.

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

Beta 8 introduced dashboard template version 8.

Existing Beta 6 and Beta 7 dashboards are migrated selectively rather than
replaced. The migration can add the dynamic SOC controls and sensors while
preserving unrelated user changes.

If the exact old Beta 6 battery mapping is still present, it is corrected to
the Beta 7 mapping during migration.

### Beta 9 dashboard repair

Beta 9 increased the dashboard template version to 9.

Beta 8 contained an error in the targeted migration of an existing controller
status Markdown card. The generated Jinja expression for the SOC schedule could
end with only one closing brace and cause:

```text
TemplateSyntaxError: unexpected '}'
```

Beta 9 detects this exact malformed SOC schedule line and repairs it
automatically.

The repair is intentionally targeted. Other user changes to the dashboard are
not replaced.

### Beta 10 dashboard behavior

Beta 10 does not change the dashboard structure.

Dashboard template version remains:

```text
9
```

The existing dynamic SOC chart automatically displays the new time-based target
curve because the same `dynamic_soc_target` sensor is used.

### Beta 11 dashboard migration

Beta 11 adds new release controls and diagnostics, so the dashboard template
version increases to:

```text
10
```

Existing dashboards are migrated selectively. The integration adds the
predictive release switch, forecast-required minimum SOC, SOC release floor,
releasable battery energy, SOC release target, and the `soc_release` controller
mode where the standard cards can be identified. Unrelated user customizations
are preserved.

## Dashboard requirements

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

Four switches are available:

- `Optimizer calculation enabled`
- `Active NOAH control`
- `Dynamic SOC control`
- `Predictive SOC release enabled`

The active controller includes:

- configurable command deadband
- minimum interval between normal output commands
- retry handling
- failsafe after prolonged loss of critical data
- persistent Home Assistant failsafe notification
- legacy YAML controller interlock

Beta 10 changes the dynamic SOC calculation used in automatic mode.

Beta 11 adds predictive SOC release as an additional automatic controller mode.

The controller in `control.py` is also extended so that downward target
corrections after a SOC-release command bypass the normal command interval and
deadband. This allows falling household load or a rising SOC release floor to
reduce battery discharge without waiting for the normal rate limit.

Predictive SOC release is disabled by default.

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

Added the dynamic SOC plan with:

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

### 2.0.0-beta.9

Dashboard migration hotfix:

- fixes the malformed SOC schedule Jinja expression
- repairs dashboards already migrated by Beta 8
- increases dashboard template version to 9
- preserves user dashboard customizations
- does not change optimizer or active-control logic

### 2.0.0-beta.10

Dynamic SOC load-plan rework:

- adds a time-based SOC curve from sunrise to sunset
- keeps minimum SOC as the start of the daytime curve
- reaches target SOC at sunset
- applies weak remaining PV forecast as progressive forecast pressure
- prevents weak forecast from forcing an immediate 100% target early in the day
- keeps existing dashboard entities and template version 9
- leaves manual, self-consumption, and charge-priority modes unchanged

### 2.0.0-beta.11

Predictive SOC release:

- adds a separate opt-in predictive release switch
- calculates a forecast-required minimum SOC
- protects the dynamic schedule and forecast requirement with an SOC release floor
- exposes releasable battery energy and an SOC release target
- adds the `soc_release` controller mode
- uses safe SOC surplus to reduce current grid import
- does not intentionally request battery export to the grid
- increases dashboard template version to 10
- preserves manual, self-consumption, charge-priority, and night behavior

### 2.0.0-beta.12

Predictive SOC release reserve and dynamic catch-up fix:

- separates the predictive-release refill reserve from the dynamic charging schedule
- no longer deducts expected household demand from the refill reserve
- prevents a negative normal forecast margin from unnecessarily locking the release floor at 100%
- keeps the dynamic SOC target curve unchanged
- projects the catch-up target to the end of the configured catch-up window
- prevents catch-up charging from permanently trailing a rising SOC target
- keeps dashboard template version 10
- adds no new entities, switches, or controller modes

### 2.0.0-beta.13

Faster predictive SOC release response:

- evaluates the active controller every 15 seconds
- allows SOC-release target increases every 30 seconds
- keeps the two-minute minimum interval for normal controller modes
- uses a release-specific effective deadband of at most 25 W
- keeps immediate safety reductions after SOC release
- reports `rate_limited` only for an actual pending command
- keeps dashboard template version 10
- adds no new entities, switches, or controller modes

## Current limitations 

The beta does not yet include:

- learned household load
- multiple independent NOAH systems
- an hourly Forecast.Solar production profile for shaping the SOC curve

Active control should still be treated as beta functionality and monitored
during testing.

# 2.1.0-beta.13 – Stable SOC release and resilient forecast planning

Beta 13 addresses three behaviors observed during real operation of the NOAH
Optimizer.

## Fixed: predictive SOC release oscillation

When the battery was safely ahead of its SOC schedule, predictive SOC release
could oscillate between **SOC release** and **Hold SOC schedule** around zero
grid power.

Previously, any positive grid import enabled SOC release, while even a very
small export disabled it again. Because reductions from SOC release are applied
immediately, this could create a repeating pattern of grid import, release,
small export and hold.

Beta 13 adds hysteresis:

- SOC release keeps the existing entry condition of positive grid import.
- Once active, SOC release remains latched across a small export overshoot.
- The export hysteresis is the largest of 50 W, the configured residual grid
  reserve and two output-command steps.
- While release remains active, signed grid power is used for the target. A
  small export therefore reduces the NOAH output toward zero grid power instead
  of immediately switching modes.
- Release still stops immediately when safe releasable battery headroom is no
  longer available.
- Disabling predictive SOC release takes effect immediately; the hysteresis never keeps a disabled release mode latched.

No new user option is required.

## Fixed: temporary Forecast.Solar curve loss

The optimizer uses the native time-resolved Forecast.Solar curve when it is
available. A short runtime-data interruption could previously make the native
curve disappear while the remaining-energy sensor was still valid. The
optimizer then fell back to the old daylight schedule, which can approach
100 % near sunset and caused an artificial jump in the dynamic SOC target.

Beta 13 keeps the last valid same-day native Forecast.Solar curve for up to
three hours when the runtime curve temporarily disappears.

The cached curve is only reused when:

- it belongs to the current local calendar day,
- it is not older than three hours, and
- the planning parameters that define the curve have not changed.

After the cache expires, or on a new day, the existing daylight fallback is
used again if no native curve is available.

## Fixed: dynamic SOC target during expected night shutdown

When the NOAH reaches minimum SOC at night it may intentionally power down.
Source updates remain blocked during that expected shutdown for safety.

Previously this could leave the `Dynamic SOC target` sensor frozen at the last
value from the previous evening, often 100 %, and produce an artificial
vertical line in the historical SOC schedule.

Beta 13 publishes the configured minimum SOC as the dynamic SOC target while
this expected minimum-SOC night shutdown is active. No cached NOAH measurement
is consumed and all existing offline safety blocks remain active.

## Safety

The update does not weaken any existing safety mechanism:

- no normal output command is sent while NOAH Connectivity is not online,
- no missing-data 0 W failsafe command is sent while the NOAH is offline,
- cached Noah-MQTT measurements are still blocked while offline,
- PV learning remains protected against cached PV power,
- predictive SOC release remains limited by the forecast-based release floor
  and safely releasable battery energy.

## Version

```text
2.1.0-beta.13
```

Base: `main` commit `0f0b426e5480050624b363ab737413bd5c26d824`
(`2.1.0-beta.12`).

No dashboard-template migration and no translation migration are required.

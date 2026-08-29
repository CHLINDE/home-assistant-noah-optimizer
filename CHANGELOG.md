## [2.1.0-beta.8] - 2026-08-29

### Fixed

- Fixed the dashboard color migration for installations that already contain explicit series colors from an earlier generated dashboard.
- Recognized generated NOAH standard ApexCharts cards are realigned to the documented stable color palette instead of skipping every series that already has a `color` value.
- The migration is deliberately limited by known standard chart titles and entity sets so additional/user-created ApexCharts cards remain untouched.
- Dashboard template version increased from 17 to 18 so systems already migrated by Beta 7 run the corrected color migration once.
- History-card frontend cache version increased from `v=7` to `v=8`.
- Corrected `manifest.json` version to `2.1.0-beta.8`.

### Documentation

- Updated README, installation, configuration, HACS beta and troubleshooting documentation for dashboard template version 18.
- Documented the one-time reset of stale generated standard-chart colors.
- Documented that unrelated custom ApexCharts cards are not modified.

### Safety / transparency

- No optimizer calculation or active-control logic is changed.
- Manual colors inside recognized generated NOAH standard charts are reset once by the template-v18 migration; unrelated custom charts are not modified.

---

## [2.1.0-beta.7] - 2026-08-29

### Dashboard color consistency

- Completed the explicit color alignment of generated NOAH standard charts.
- Aligned controller behavior to blue / green / orange / yellow / cyan / violet.
- Aligned the historical SOC view to blue / green / orange / yellow.
- Increased dashboard template version to 17.
- Migrated the previous NOAH default red target-SOC color to orange while leaving other explicit colors untouched.
- Increased the bundled history-card frontend cache version from `v=6` to `v=7`.

### Safety / transparency

- No optimizer calculation or active-control logic changed.

---

## [2.1.0-beta.4] - 2026-08-26

### Added

- Added a bundled date-selectable SOC schedule history card with previous/next day controls, direct date selection and a Today shortcut.
- Added historical display of actual SOC, the dynamic SOC target that was active at the time, and configured target SOC using Home Assistant History/Recorder.
- Added persistent forecast/SOC-plan snapshots for the last 31 rolling days, with multiple distinct plan versions per day.
- Added a plan-snapshot selector so an older full-day forecast plan can be overlaid on recorded SOC history.
- Snapshot metadata includes Forecast.Solar update time, raw/effective forecast curves, effective daily forecast, forecast end SOC, forecast factors and plan-relevant settings.
- Added the bundled `noah-soc-history-card.js`; no separate HACS frontend repository is required.

### Changed

- Registered the bundled SOC history card as a persistent Lovelace module resource in storage mode.
- Declared the Home Assistant frontend/history/http/websocket dependencies required by the bundled card and history endpoint.
- Migrated the standard dynamic-SOC chart to the date-selectable history card while preserving user-created charts with a different title.
- Deduplicated stored forecast/plan snapshots.
- Clipped history series to the selected local day and extended the selected saved plan across the full day.

### Safety / transparency

- Historical states come from Home Assistant Recorder and are not recalculated from current settings.
- Stored snapshots are diagnostic only and never feed back into active NOAH control.
- Existing forecast-curve planning and active control behavior remain unchanged.

---

## [2.1.0-beta.3] - 2026-08-26

### Added

- Reuse of the complete time-resolved Forecast.Solar power curve already loaded by Home Assistant; no additional Forecast.Solar API requests are made.
- `PV forecast curve` diagnostic sensor with raw forecast power, effective forecast power and derived SOC plan attributes.
- Sensors for effective daily forecast, Forecast.Solar update timestamp, forecast plan end SOC and SOC schedule basis.
- Dashboard PV forecast chart comparing raw Forecast.Solar power, effective forecast power and actual PV production.
- `forecast_curve` / `daylight_fallback` schedule-source diagnostics.

### Fixed

- Corrected Forecast-curve planning so PV power below expected household load is not incorrectly treated as unavailable for battery charging.
- Corrected dashboard migration so a diagnostics row is not mistaken for an existing forecast chart.
- Fall back to the legacy daylight schedule if Forecast.Solar runtime data is unavailable.

### Changed

- Dynamic SOC planning follows the time distribution of the native Forecast.Solar power curve when available.
- The effective forecast curve applies the configured forecast safety factor and optional learned PV correction factor.
- Expected household demand remains part of forecast-margin and output-control calculations rather than being subtracted from every native forecast interval.
- SOC catch-up targets the future point of the same forecast-shaped SOC plan.
- Dashboard template version increased from 13 to 14.

---

## [2.1.0-beta.2] - 2026-08-24

### Added

- Added automatic `soc_hold` controller mode (`SOC-Ladeplan halten` / `Hold SOC schedule`) for a satisfied dynamic SOC charging schedule.

### Fixed

- Prevented legacy forecast-margin logic from selecting charge priority a second time when dynamic SOC control is active and the battery is within tolerance at or ahead of the dynamic SOC target.
- Limited schedule-hold output to PV-only operation so it does not intentionally discharge the battery.
- Required output reductions in `soc_hold` bypass the normal command interval so falling PV cannot temporarily cause unintended battery discharge.

### Changed

- Predictive SOC release remains the mechanism for intentionally using safely releasable battery energy.
- Dashboard template version increased from 12 to 13.

---

## [2.1.0-beta.1] - 2026-08-24

### Added

- Passive PV learning based on measured NOAH solar power and Forecast.Solar.
- Persistent PV-learning history across Home Assistant restarts.
- Robust learned correction factor using valid learning days.
- Minimum number of valid learning days before learned correction can be applied.
- Opt-in switch for applying the learned PV correction.
- Button for resetting PV-learning data.
- Diagnostic sensors for learning factor, effective forecast factor, learning days, daily ratio, measured PV energy and forecast reference.
- PV-learning readiness binary sensor.
- PV-learning diagnostics and controls in the automatic dashboard.

### Changed

- Effective remaining PV forecast can optionally use the learned correction.
- Dashboard template version increased from 11 to 12.
- Existing forecast and control behavior remains unchanged while learned PV correction is disabled.

---

## [2.0.0]

### Release

- First stable release of the 2.x integration.
- Promoted the tested `2.0.0-beta.14` feature set to stable `2.0.0`.
- No optimizer-calculation, active-control, entity-model or dashboard-logic changes compared with `2.0.0-beta.14`.

### Safety

Active NOAH control remains opt-in and all existing controller safeguards remain unchanged.

---

## [2.0.0-beta.14]

### Added / fixed

- Added automatic `pv_redirect` controller mode for redirecting simultaneous battery charging to household consumption when the battery is already at or above the dynamic SOC target.
- Added a dedicated translated `controller_status` enum sensor.
- Added `night` as a dedicated state of the dynamic SOC schedule sensor.
- Replaced misleading night/ahead and retry status text.
- Dashboard template version increased from 10 to 11.

---

## [2.0.0-beta.13]

- Faster predictive SOC-release response with 15-second controller evaluation and 30-second command cadence for applicable load-following modes.

## [2.0.0-beta.12]

- Corrected predictive SOC-release refill reserve and dynamic SOC catch-up projection.

## [2.0.0-beta.11]

- Added predictive SOC release, release diagnostics and dashboard template version 10.

## [2.0.0-beta.10]

- Reworked dynamic SOC target into a time-based charging schedule from sunrise to sunset.

## [2.0.0-beta.9]

- Repaired the Beta-8 controller-status Jinja migration and increased dashboard template version to 9.

## [2.0.0-beta.8]

- Added dynamic SOC target, deviation, plan status, catch-up power and opt-in dynamic SOC control.

## [2.0.0-beta.7]

- Corrected battery energy-flow direction in the dashboard.

## [2.0.0-beta.6]

- Added the automatic NOAH Optimizer Lovelace dashboard.

## [2.0.0-beta.5]

- Added optional active NOAH output control, rate limiting, retry and failsafe handling.

## [2.0.0-beta.4]

- Added the missing `select.py` platform.

## [2.0.0-beta.3]

- Ported the legacy YAML optimizer calculation logic to Python while remaining observation-only.

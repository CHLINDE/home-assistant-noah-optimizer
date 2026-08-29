## [2.1.0-beta.4] - 2026-08-26

### Dashboard color consistency

- Added explicit series colors to the generated German and English ApexCharts cards
- Uses `#2196F3` / `#009B21` / `#F44336` consistently for actual SOC, dynamic target and final target SOC
- Aligns the historical SOC card with the same palette and uses `#FFD800` for the saved plan
- Dashboard template version increased from 15 to 16; migration only fills missing colors and preserves explicit user colors
- History-card frontend cache version increased from `v=5` to `v=6`
- Fixed the generated Python chart definitions so the new `color` values are valid dictionary entries

### Added

- Added a bundled date-selectable SOC schedule history card with previous/next day controls, direct date selection and a Today shortcut
- Added historical display of actual SOC, the dynamic SOC target that was active at the time, and configured target SOC using Home Assistant History/Recorder
- Added persistent forecast/SOC-plan snapshots for the last 31 rolling days, with up to 48 distinct plan versions per day
- Added a Plan snapshot selector so an older full-day forecast plan can be overlaid on the recorded SOC history
- Snapshot metadata includes Forecast.Solar update time, raw/effective forecast curves, effective daily forecast, forecast end SOC, forecast factors and plan-relevant settings
- Added the bundled `noah-soc-history-card.js`; no separate HACS frontend repository is required

### Changed

- The bundled SOC history card is registered as a persistent Lovelace module resource in storage mode to avoid custom-card load-order races
- Home Assistant `http` and `websocket_api` are explicitly declared for the bundled frontend resource and history WebSocket endpoint

- Dashboard template version increased from 14 to 15
- The standard dynamic-SOC ApexCharts card is migrated to the date-selectable NOAH history card while user-created charts with a different title are preserved
- The integration now declares Home Assistant `frontend` and `history` as dependencies for the bundled history card and recorder-backed historical chart
- Forecast/plan snapshots are deduplicated so an unchanged plan is not written repeatedly on every coordinator refresh
- Date changes during an in-flight history request now invalidate stale requests so rapid previous/next navigation cannot display the wrong day
- History series are clipped to the selected local day and the saved plan is extended across the full day for a consistent 00:00–24:00 view
- Current documentation is aligned with the Beta 3 forecast allocation: the native Forecast.Solar SOC schedule integrates the complete effective PV curve, while expected household load remains separate in forecast-margin/output control; the legacy load subtraction applies only to the daylight fallback

### Safety / transparency

- Historical SOC lines come from states actually recorded by Home Assistant; a past day is not recalculated from today's forecast or settings
- Stored snapshots are diagnostic only and never feed back into active NOAH control
- Snapshot retention is bounded to 31 days and 48 distinct snapshots per day
- Existing Beta 3 forecast-curve planning and all active control behavior remain unchanged

---

## [2.1.0-beta.3] - 2026-08-26

### Added

- Added reuse of the complete time-resolved Forecast.Solar power curve already loaded by Home Assistant; no additional Forecast.Solar API requests are made
- Added the `PV forecast curve` diagnostic sensor with raw Forecast.Solar power, effective forecast power, and the derived SOC plan as attributes
- Added sensors for effective daily forecast, Forecast.Solar update timestamp, forecast plan end SOC, and SOC schedule basis
- Added a dashboard PV forecast chart comparing raw Forecast.Solar power, effective forecast power, and actual PV production
- Added `forecast_curve` / `daylight_fallback` schedule-source diagnostics in German and English

### Fixed

- Fixed Forecast-curve planning so PV power below the configured expected household load is not incorrectly treated as unavailable for battery charging; the controller can reserve that PV for the battery and let the grid supply the household when required to maintain the SOC plan
- Fixed the Beta 3 dashboard migration so an existing diagnostics row for the forecast-curve sensor is not mistaken for an already existing ApexCharts forecast chart
- Fall back to the legacy daylight schedule when the Forecast.Solar config entry exists but has no loaded `runtime_data`, instead of allowing an `AttributeError` to fail the optimizer update

### Changed

- Dynamic SOC planning now follows the time distribution of the native Forecast.Solar power curve instead of astronomical daylight progress when a native Forecast.Solar source can be resolved
- The effective forecast curve applies the configured forecast safety factor and, when enabled and ready, the learned PV correction factor
- The SOC plan now integrates the complete effective PV profile instead of subtracting expected household load from every forecast interval; household demand remains part of forecast-margin and output-control calculations
- Charging efficiency and the configured forecast energy reserve remain part of the SOC planning calculation
- SOC catch-up targets the future point of the same forecast-shaped SOC plan
- The legacy daylight-progress calculation remains available automatically when no native Forecast.Solar curve can be resolved
- Dashboard template version increased from 13 to 14; existing generated dashboards are migrated with the new forecast chart and diagnostics

### Safety / transparency

- Actual PV production and actual battery SOC do not retroactively reshape the forecast-derived SOC plan; forecast errors therefore remain visible instead of being hidden by adapting the plan to actual results
- A new SOC plan is produced when Forecast.Solar updates its forecast or when relevant planning parameters change
- Forecast.Solar runtime data is reused only when the configured remaining-forecast entity belongs directly to the Forecast.Solar integration; template or other forecast entities use the existing daylight fallback
- Historical date browsing and persistent forecast snapshots are intentionally deferred to a later release

---

## [2.1.0-beta.2] - 2026-08-24

### Added

- Added the automatic `soc_hold` controller mode (`SOC-Ladeplan halten` / `Hold SOC schedule`) for a satisfied dynamic SOC charging schedule

### Fixed

- Prevented the legacy forecast-margin logic from selecting charge priority a second time when dynamic SOC control is active and the battery is already within tolerance at or ahead of the dynamic SOC target
- Prevented the schedule-hold mode from intentionally discharging the battery by limiting its raw output target to the smaller of current PV power and the self-consumption target
- Schedule-hold output is rounded down to the configured command step so rounding cannot request more output than the safe PV-only target
- Required output reductions in `soc_hold` bypass the normal two-minute command interval so falling PV cannot temporarily cause unintended battery discharge

### Changed

- Predictive SOC release remains the dedicated automatic mechanism for intentionally using safely releasable battery energy
- SOC catch-up, SOC release and PV diversion keep their existing priorities
- Dashboard template version increased from 12 to 13 and existing controller-status cards are migrated with the new mode label
- PV learning itself is unchanged from `2.1.0-beta.1`

---

## [2.1.0-beta.1] - 2026-08-24

### Added

- Passive PV learning based on measured NOAH solar power and Forecast.Solar
- Persistent PV-learning history across Home Assistant restarts
- Robust learned correction factor using the median of up to 7 valid learning days
- Minimum of 3 valid learning days before learned correction can be applied
- Opt-in switch for applying the learned PV correction
- Button for resetting all PV-learning data
- Diagnostic sensors for learning factor, effective forecast factor, learning days, last daily ratio, measured PV energy, and forecast reference
- PV-learning readiness binary sensor
- PV-learning diagnostics and controls in the automatic dashboard

### Changed

- Effective remaining PV forecast can optionally use `forecast safety factor × learned PV factor`
- Dashboard template version increased from 11 to 12
- Existing forecast and control behavior remains unchanged while learned PV correction is disabled

### Safety

- PV learning runs passively by default
- Applying learned PV correction is opt-in and disabled by default
- Individual daily learning factors are limited to `0.50 ... 1.50`
- At least 3 valid learning days are required before the learned factor can affect the forecast
- A learning day must reach at least 85% of the daylight window before it can be accepted
- Daytime measurement gaps longer than 10 minutes invalidate the complete learning day instead of treating missing production as zero
- A forecast reference is no longer captured at night after daytime observation has already started
- The current PV-learning state is saved immediately during controlled integration unloads/reloads so a short Home Assistant restart does not appear as a long measurement gap
- Existing active-control safeguards remain unchanged

---

## [2.0.0]

### Release

- First stable release of the 2.x integration
- Promoted the tested `2.0.0-beta.14` feature set to stable `2.0.0`
- No optimizer-calculation, active-control, entity-model, or dashboard-logic changes compared with `2.0.0-beta.14`

### Changed

- Integration version changed from `2.0.0-beta.14` to `2.0.0`
- README, installation, configuration, HACS pre-release, and troubleshooting documentation updated for the stable release
- Dashboard template version remains 11

### Safety

Active NOAH control remains opt-in and all existing controller safeguards remain
unchanged. Upgrading from `2.0.0-beta.14` does not change the configured control
behavior.

---

## [2.0.0-beta.14]

### Added

- Added the automatic `pv_redirect` controller mode for redirecting simultaneous battery charging to household consumption when the battery is already at or above the dynamic SOC target
- Added a dedicated `controller_status` enum sensor for the low-level active-control state
- Added central German and English state translations for all controller-status values
- Added `night` as a dedicated state of the dynamic SOC schedule status sensor

### Fixed

- Prevented avoidable grid import while PV power is simultaneously charging the battery and the battery is already at or above the dynamic SOC target
- Replaced the misleading `ahead` / `Vor Ladeplan` classification during night operation with the dedicated night status
- Replaced the misleading `waiting_for_retry` display text with `Warte auf Stellwertübernahme` / `Waiting for setpoint confirmation`
- PV diversion now rounds its final target down to the configured output step so command-step rounding cannot intentionally request more power than the simultaneously available battery charging power

### Changed

- PV diversion is limited to `min(grid import, battery charging power)` and therefore reduces charging before any battery discharge is requested
- Predictive SOC release remains the separate mechanism for intentionally using safely releasable battery energy
- SOC catch-up keeps higher priority than PV diversion while the battery is behind the dynamic SOC schedule
- The 15-second controller evaluation and 30-second load-following command interval now apply to both `soc_release` and `pv_redirect`
- Downward corrections after either load-following mode can still bypass the normal command interval and deadband
- The existing `control_status` switch attribute is retained for compatibility, while dashboards use the new translated enum sensor
- Dashboard template version increased from 10 to 11
- Existing stored controller-status cards are migrated selectively to use the translated controller-status sensor and to display `PV-Umlenkung` / `PV diversion` and the dedicated night SOC status

### Documentation

- Updated README, installation, configuration, HACS beta, and troubleshooting documentation for PV diversion, the controller-status sensor, the revised retry text, and the dedicated night status
- Added troubleshooting guidance for simultaneous grid import and battery charging

### Safety

PV diversion does not require predictive SOC release to be enabled because it is
not intended to discharge the battery. Its raw increase is capped by the lower
of current grid import and current battery charging power, and the final target
is rounded downward to the configured command step.

If battery energy must be used beyond the simultaneously available charging
power, the existing predictive SOC-release limits continue to apply.

---

## [2.0.0-beta.13]

### Fixed

- Reduced the delayed response of predictive SOC release to changing household load and grid import
- `rate_limited` is now reported only when an actual pending command is waiting for its minimum command interval

### Changed

- Controller evaluation interval reduced from 60 seconds to 15 seconds
- Output increases while `soc_release` is active may be written every 30 seconds instead of using the normal two-minute command interval
- Normal controller modes keep the existing two-minute minimum command interval
- Predictive SOC release uses an internal deadband of at most 25 W while respecting any smaller configured command deadband
- Command-step rounding remains unchanged and still defines the final output target granularity
- Safety-relevant target reductions after SOC-release commands continue to bypass command interval and deadband
- Dashboard structure and dashboard template version remain unchanged at version 10
- No new entities, switches, or controller modes are introduced

### Documentation

- Updated README, installation, configuration, HACS beta, and troubleshooting documentation for the faster predictive-release controller response
- Documented the different command intervals for normal control and predictive SOC release

### Safety

The faster command cadence applies only while the calculated controller mode is
`soc_release`. Normal forecast-driven modes keep the existing conservative
two-minute minimum command interval.

Downward corrections after an SOC-release command remain immediate so falling
household load or a rising release floor cannot leave an unnecessarily high
discharge target active.

---

## [2.0.0-beta.12]

### Fixed

- Corrected the predictive SOC-release refill reserve introduced in Beta 11
- The forecast-required minimum SOC for predictive release no longer deducts expected household demand
- Prevented a full battery from being locked at a 100% SOC release floor solely because the normal forecast margin is negative due to expected household demand
- Predictive release now correctly evaluates how much SOC can be restored later from effective remaining PV forecast after the configured energy reserve
- Corrected dynamic SOC catch-up so it no longer aims only at the current moving SOC target

### Changed

- The dynamic SOC target curve remains unchanged and continues to deduct expected household demand from its conservative forecast calculation
- Dynamic catch-up now projects the SOC target to the end of the configured catch-up window and sizes charging power for that future target
- The catch-up projection keeps the current forecast requirement and is recalculated on every coordinator update
- Predictive SOC release now uses a separate refill reserve based on effective remaining PV forecast minus the configured energy reserve
- Later household demand may be supplied from the grid while remaining PV is reserved for restoring released battery SOC if required
- Dashboard structure and dashboard template version remain unchanged at version 10
- No new entities, switches, or controller modes are introduced

### Documentation

- Updated README, installation, configuration, HACS beta, and troubleshooting documentation for the corrected predictive-release refill reserve
- Added the distinction between the dynamic charging-schedule forecast calculation and the predictive-release refill calculation
- Added a worked example for a full battery with remaining PV forecast
- Documented the projected catch-up target used while the battery is behind the rising SOC schedule

### Safety

Predictive SOC release remains disabled by default for a new setup.

The corrected release reserve is forecast-based. It protects the calculated
release floor but cannot guarantee the evening target SOC if actual PV
production is lower than forecast.

Before enabling active control after the update, verify the forecast-required
minimum SOC, SOC release floor, releasable battery energy, and SOC release
target in observation mode.

---

## [2.0.0-beta.11]

### Added

- Predictive SOC release for using safely available battery headroom to reduce grid import before sunset
- Separate opt-in switch for predictive SOC release, disabled by default
- New `soc_release` controller mode
- Forecast-required minimum SOC sensor
- SOC release floor sensor with an additional 2-percentage-point safety buffer
- Releasable battery energy sensor
- SOC release target sensor
- Predictive SOC release diagnostics in the automatic Lovelace dashboard

### Changed

- Automatic mode can cover current grid import from safely releasable battery SOC when predictive SOC release is enabled
- SOC release is limited by the higher of the dynamic SOC target and the forecast-required minimum SOC, plus the existing 2-percentage-point SOC tolerance as a safety buffer
- SOC release requires dynamic SOC control to be enabled so catch-up charging remains available if the forecast later worsens
- SOC release only reacts to positive grid import and does not intentionally request battery export to the grid
- Manual, self-consumption, charge-priority, and night behavior remain unchanged
- Dashboard template storage version increased from 9 to 10
- Existing dashboards are migrated selectively with the new switch and release diagnostics while preserving user customizations
- Downward target corrections after SOC-release commands bypass the normal two-minute command interval and deadband so a rising release floor or falling household load can reduce discharge promptly

### Documentation

- Updated README, installation, configuration, HACS beta, and troubleshooting documentation for predictive SOC release
- Added formulas for forecast-required SOC, release floor, releasable battery energy, and release target
- Documented that the release safety is forecast-based and cannot guarantee the evening target if actual PV production or household demand differs materially from the forecast

### Safety

Predictive SOC release is disabled by default.

Before enabling it, verify the forecast-required minimum SOC, SOC release floor,
releasable battery energy, and SOC release target in observation mode.

The release logic never intentionally discharges below the calculated release
floor. It is nevertheless based on the currently available forecast and load
assumptions and therefore cannot provide an absolute guarantee for the evening
SOC if conditions change unexpectedly.

---

## [2.0.0-beta.10]

### Changed

- Reworked the dynamic SOC target into a real time-based charging schedule from sunrise to sunset
- Added daylight progress as the time basis for the dynamic SOC plan
- The base SOC schedule now rises continuously from minimum SOC at sunrise to target SOC at sunset
- The remaining PV forecast now raises the time-based schedule progressively instead of acting as an immediate hard SOC requirement
- Prevented poor remaining forecasts from forcing the dynamic SOC target directly to 100% for most of the day
- Dynamic catch-up power and `ahead` / `on_track` / `behind` status now use the new time-based forecast-aware target
- Nighttime dynamic SOC target remains at minimum SOC
- Dashboard template version remains 9 because no dashboard structure changes are required

### Documentation

- Updated README, installation, configuration, HACS beta, and troubleshooting documentation for the Beta 10 load-plan calculation
- Added an explanation of the time-based SOC curve and forecast pressure
- Added guidance for validating that the dynamic target changes gradually during daylight

### Safety

Beta 10 changes the automatic dynamic SOC calculation and can therefore change
the calculated output target when dynamic SOC control is enabled.

Before updating, disable active NOAH control and dynamic SOC control. After the
update, observe the new dynamic SOC target and schedule status before enabling
dynamic SOC control again.

Manual, self-consumption, and charge-priority operating modes remain unchanged.

---

## [2.0.0-beta.9]

### Fixed

- Fixed `TemplateSyntaxError: unexpected '}'` in the controller status Markdown card after upgrading an existing dashboard to Beta 8
- Corrected the Jinja expression generated for the dynamic SOC schedule status
- Added a targeted repair for dashboard configurations already migrated and stored by Beta 8
- Existing user dashboard customizations remain preserved during the repair

### Changed

- Dashboard template storage version increased from 8 to 9
- Beta 8 dashboard additions remain idempotent when upgrading directly from older beta versions

### Documentation

- Added troubleshooting information for the Beta 8 controller-status template error
- Updated installation documentation for Beta 9
- Added a note about the Home Assistant 2026.8 HTTP port change and My Home Assistant instance URLs

### Safety

Beta 9 does not change the optimizer calculation or active NOAH control logic.

The release only repairs the automatically generated Lovelace dashboard migration.

---

## [2.0.0-beta.8]

### Added

- Dynamic SOC target calculated from the remaining PV forecast, expected household demand, energy reserve, battery capacity, charging efficiency, minimum SOC, and target SOC
- SOC deviation sensor showing actual SOC minus the dynamic SOC target
- Dynamic SOC plan status with `ahead`, `on_track`, and `behind` states
- Dynamic required charging power for catching up when the battery falls behind the SOC plan
- Separate opt-in switch for dynamic SOC control
- Configurable SOC catch-up time, defaulting to 2 hours
- New `soc_catchup` controller mode
- Dynamic SOC planning information in the automatic Lovelace dashboard
- Actual-SOC, dynamic-target-SOC, and configured target-SOC chart
- Targeted dashboard migration for existing Beta 6 and Beta 7 installations

### Changed

- Automatic mode can reserve additional PV power for battery charging when dynamic SOC control is enabled and the battery is more than 2 percentage points behind the dynamic SOC target
- Dynamic SOC calculations remain visible even while dynamic SOC control is disabled
- Manual, self-consumption, and charge-priority operating modes remain unaffected by the new dynamic SOC control
- Dashboard template version set to 8 for targeted dashboard migrations
- Existing dashboards are migrated selectively instead of being replaced
- Beta 6 battery-flow mapping is corrected during dashboard migration when the old exact mapping is still present
- Documentation updated for the dynamic SOC feature and Beta 8 installation
- README now includes a My Home Assistant button for opening the repository directly in HACS

### Safety

Dynamic SOC control is disabled by default.

Updating from Beta 7 does not automatically change the existing optimizer
output behavior. The new dynamic SOC sensors can be monitored first and the
feature can then be enabled explicitly.

The active NOAH control safety mechanisms introduced in Beta 5 remain
unchanged.

---

## [2.0.0-beta.7]

### Fixed

- Corrected the battery energy-flow direction in the NOAH Optimizer dashboard
- Fixed Power Flow Card Plus battery mapping so charging power is displayed as energy flowing into the battery
- Fixed Power Flow Card Plus battery mapping so discharging power is displayed as energy flowing out of the battery
- Corrected the battery-flow mapping in the German dashboard template
- Corrected the battery-flow mapping in the English dashboard template
- Corrected the battery-flow mapping in the legacy YAML dashboard
- Updated related documentation to use the correct battery-flow direction

### Documentation

- Updated the README for Beta 7
- Added third-party attribution for Noah-MQTT
- Added third-party attribution for Power Flow Card Plus
- Added third-party attribution for ApexCharts Card
- Clarified that dashboard dependencies are installed separately and are not bundled with the integration

### Safety

This release did not change the active optimizer control logic introduced in
Beta 5.

---

## [2.0.0-beta.6]

### Added

- Automatic NOAH Optimizer dashboard creation
- Dashboard shown in the Home Assistant sidebar by default
- Optional sidebar visibility setting during initial setup
- Dynamic resolution of optimizer entity IDs through the Home Assistant entity registry
- Power-flow visualization with separate import/export and charge/discharge values
- Controller status and last-command diagnostics
- Forecast and energy-planning charts
- Controller behavior chart
- Calibration and diagnostic sections

### Changed

- Dashboard updated for the active Beta 5 controller
- Separate optimizer calculation and active-control switches are shown
- Direct manual access to the NOAH System Output Power actuator has been removed from the dashboard
- Existing user-modified dashboards are not overwritten

### Dashboard requirements

The enhanced dashboard uses:

- Power Flow Card Plus
- ApexCharts Card

The optimizer integration itself continues to work if these dashboard cards are not installed.

---

## [2.0.0-beta.5]

### Added

- Active NOAH output control
- Separate opt-in switch for active control
- Minimum interval between output commands
- Command deadband handling
- Automatic retry when a requested setpoint is not applied
- Failsafe output of 0 W after prolonged loss of critical data
- Protection against simultaneous control by the legacy YAML optimizer
- Controller diagnostics on the active-control switch

### Safety

Active control is disabled by default.

Updating from an earlier beta does not automatically enable writing to
the NOAH System Output Power entity.

The legacy YAML optimizer and the HACS optimizer must never control the
same NOAH simultaneously.

---

## [2.0.0-beta.4]

### Fixed

- Added the missing `select.py` platform.
- Fixed integration setup failure introduced in `2.0.0-beta.3`.

### Safety

This release remains observation-only and does not write to the
NOAH System Output Power entity.

---

## [2.0.0-beta.3]

### Added

- configurable optimizer parameters as Home Assistant number entities
- operating mode selector
- optimizer enable switch for calculation state
- five-minute grid power average
- remaining hours until sunset
- available battery energy
- required charging energy
- effective remaining PV forecast
- expected remaining household energy demand
- forecast margin
- forecast coverage
- required average charging power
- estimated time to target SOC
- self-consumption output target
- charge-priority output target
- calculated final output target
- calculated controller mode

### Changed

- Existing YAML optimizer calculation logic has been ported to Python.
- Source and sun state changes trigger immediate recalculation.

### Safety

Version 2.0.0-beta.3 remains observation-only.

It calculates the desired NOAH output power but does not write the
calculated value to the NOAH System Output Power entity.

---

## [2.0.0-beta.2]

### Fixed

- Changed the Home Assistant integration type from `helper` to `device`.
- The NOAH Optimizer is now handled as a regular device integration.
- Improved visibility of the integration under Settings → Devices & services.

### Changed

- Integration version updated to `2.0.0-beta.2`.

### Safety

This release remains observation-only and does not send commands to the NOAH.

---

## [2.0.0-beta.1]

### Added

- first HACS-compatible custom integration
- Home Assistant Config Flow
- source entity selection through the UI
- power normalization from W and kW
- energy normalization from Wh and kWh
- grid import and export sensors
- calculated home load
- calculated battery power
- Forecast.Solar availability monitoring
- NOAH output control availability monitoring
- German and English translations
- observation-only mode for safe parallel testing

### Safety

This release does not send commands to the NOAH.

The existing YAML optimizer can remain active during testing.

### Not yet included

- learned home load
- multi-system support

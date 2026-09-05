## [2.1.0-beta.10]

### Added

- Automatic discovery of the Noah-MQTT `Connectivity` binary sensor belonging
  to the configured NOAH device
- NOAH offline/stale connectivity protection
- Persistent Home Assistant notification `NOAH Optimizer: NOAH offline`
- Automatic notification dismissal after connectivity recovers

### Fixed

- Cached Noah-MQTT values can no longer leave the active controller appearing
  synchronized while the physical NOAH is offline
- Offline controller ticks no longer refresh the coordinator from retained
  Noah-MQTT values
- Source-state changes now check NOAH connectivity before source values are
  consumed
- Every coordinator refresh path now passes through the same connectivity gate,
  including the built-in scheduled refresh, startup refresh, option changes and
  PV-learning reset actions
- Prevented retained PV-power values from being integrated by PV learning as
  fictitious PV production during a NOAH outage

### Safety

- Normal output commands are blocked while the NOAH is offline
- The missing-data `0 W` failsafe command is also blocked while offline
- Existing failsafe timing state is reset during the offline condition so an
  old outage interval cannot trigger an immediate write after recovery
- After connectivity returns, fresh source values are read before the normal
  controller resumes

### Changed

- Integration version updated to `2.1.0-beta.10`
- No dashboard-template migration is required
- Existing `actuator_unavailable` data/controller status is reused while the
  persistent notification provides the explicit `NOAH offline` diagnosis

---

## [2.1.0-beta.9]

### Fixed

- Fixed the remaining controller-behavior color migration for existing dashboards using the older five-series chart variant
- `Reglerverhalten` / `Controller behavior` is now recognized with the five core series; the later dynamic catch-up series is optional
- Existing Beta-8 installations are migrated again so stale controller-chart colors are actually corrected

### Changed

- Dashboard template storage version increased from 18 to 19
- Integration version updated to `2.1.0-beta.9`
- The current six-series controller chart remains fully supported
- Custom ApexCharts protection based on known title and expected NOAH series remains in place

### Controller behavior palette

- Controller target: blue `#2196F3`
- Actual output: green `#009B21`
- Self-consumption target: orange `#FF6A00`
- Charge-priority target: yellow `#FFD800`
- Required charging power: cyan `#00FFFF`
- Dynamic catch-up charging power, when present: violet `#B200FF`

### Safety

This release changes dashboard migration and documentation only.

Optimizer calculations and active NOAH control behavior are unchanged.

---

## [2.1.0-beta.8]

### Fixed

- Corrected migration of stale explicit series colors in already stored NOAH dashboards
- Existing standard charts are no longer left with outdated colors merely because a `color` field already exists
- Standard-chart recognition requires the known German or English card title and the expected NOAH entity set
- User-created or additional ApexCharts are not modified by the template-v18 color migration

### Changed

- Dashboard template storage version increased from 17 to 18
- The strict template-v18 migration replaces the older broad series-color migration
- Bundled SOC history-card frontend cache version increased to `v8`
- Integration version updated to `2.1.0-beta.8`

### Standard palette

- Blue `#2196F3`
- Green `#009B21`
- Orange `#FF6A00`
- Yellow `#FFD800`
- Cyan `#00FFFF`
- Violet `#B200FF`

### Safety

This release changes dashboard presentation and migration only.

Optimizer calculations and active NOAH control behavior are unchanged.

---

## [2.1.0-beta.7]

### Fixed

- Completed the remaining standard-series color alignment
- Corrected the controller-behavior chart palette
- Corrected the historical SOC target color to orange

### Changed

- Dashboard template storage version increased to 17
- Historical SOC presentation uses blue / green / orange / yellow

### Safety

No optimizer-calculation or active-control logic changes.

---

## [2.1.0-beta.6]

### Changed

- Standardized explicit series colors in generated dashboard charts
- Introduced a consistent NOAH dashboard palette

### Safety

No optimizer-calculation or active-control logic changes.

---

## [2.1.0-beta.5]

### Changed

- Prepared and aligned generated dashboard series colors

### Safety

No optimizer-calculation or active-control logic changes.

---

## [2.1.0-beta.4]

### Added

- Date-selectable historical SOC schedule card
- Previous / next day navigation and direct date selection
- Recorder history for actual SOC, dynamic SOC target, and configured target SOC
- Persistent forecast / plan snapshots
- Selectable historical plan snapshots
- Rolling snapshot retention of up to 31 days
- Bundled frontend history card

### Changed

- Stored snapshots are diagnostic only and never affect active control

---

## [2.1.0-beta.3]

### Added

- Reuse of the complete time-resolved Forecast.Solar power curve already loaded by Home Assistant
- Raw and effective forecast-curve diagnostics
- Forecast update timestamp
- Effective daily forecast
- Forecast-shaped SOC schedule
- Daylight fallback

### Changed

- No additional Forecast.Solar API calls are made
- Expected household load remains a separate part of forecast margin and output control

---

## [2.1.0-beta.2]

### Added

- `soc_hold` controller mode

### Fixed

- Prevented unnecessary charge priority after the dynamic SOC schedule is already satisfied

### Changed

- SOC hold uses current PV for household consumption without intentionally requesting battery discharge

---

## [2.1.0-beta.1]

### Added

- Passive persistent PV learning
- Daily PV-production comparison against Forecast.Solar
- Median learning factor from up to seven valid days
- Minimum three valid days before application
- Optional learned forecast correction
- Learning diagnostics and reset

### Safety

Applying the learned factor is disabled by default.

---

## [2.0.0]

### Release

- First stable release of the 2.x integration
- Promoted the tested `2.0.0-beta.14` feature set to stable `2.0.0`
- No optimizer-calculation or active-control changes compared with Beta 14

### Changed

- Dashboard template version remains 11

---

## [2.0.0-beta.14]

### Added

- `pv_redirect` controller mode
- Dedicated `controller_status` enum sensor
- Central German and English translations
- Dedicated `night` schedule state

### Fixed

- Prevented avoidable grid import while the battery is charging above the dynamic SOC target
- Replaced misleading night `ahead` status
- Improved `waiting_for_retry` wording
- PV-diversion targets round down safely

### Changed

- PV diversion limited to `min(grid import, battery charging power)`
- Fast load-following applies to `soc_release` and `pv_redirect`
- Dashboard template version increased to 11

---

## [2.0.0-beta.13]

### Fixed

- Faster predictive SOC-release response to changing household load
- `rate_limited` only for an actual pending command

### Changed

- Controller evaluation every 15 seconds
- SOC-release increases every 30 seconds
- Normal modes retain 120 seconds

---

## [2.0.0-beta.12]

### Fixed

- Corrected predictive SOC-release refill reserve
- Expected household demand is no longer deducted from the separate refill reserve
- Corrected dynamic catch-up to target the future point of a rising SOC schedule

### Changed

- Dashboard template version remains 10

---

## [2.0.0-beta.11]

### Added

- Predictive SOC release
- Separate opt-in switch
- `soc_release` controller mode
- Forecast-required minimum SOC
- SOC release floor
- Releasable battery energy
- SOC release target
- Dashboard diagnostics

### Changed

- Dashboard template version increased to 10

### Safety

Predictive SOC release is disabled by default.

---

## [2.0.0-beta.10]

### Changed

- Reworked dynamic SOC target into a time-based charging schedule
- Added progressive forecast pressure
- Prevented poor forecast from forcing an immediate 100% target
- Dashboard template version remains 9

---

## [2.0.0-beta.9]

### Fixed

- Fixed `TemplateSyntaxError: unexpected '}'`
- Repaired dashboards already migrated by Beta 8

### Changed

- Dashboard template version increased to 9

---

## [2.0.0-beta.8]

### Added

- Dynamic SOC target
- SOC deviation
- Ahead / on-track / behind state
- Dynamic catch-up charging power
- Separate dynamic SOC switch
- Configurable catch-up time
- `soc_catchup` controller mode
- Dynamic SOC dashboard chart

### Changed

- Dashboard template version set to 8

### Safety

Dynamic SOC control is disabled by default.

---

## [2.0.0-beta.7]

### Fixed

- Corrected battery energy-flow direction
- Charging shown as flow into battery
- Discharging shown as flow out of battery

---

## [2.0.0-beta.6]

### Added

- Integration-managed Lovelace dashboard
- Dynamic entity resolution
- German and English templates
- Power-flow visualization
- Charts, calibration, and diagnostics

---

## [2.0.0-beta.5]

### Added

- Optional active NOAH output control
- Separate active-control switch
- Command interval and deadband
- Retry handling
- Failsafe
- Legacy YAML interlock

### Safety

Active control is disabled by default.

---

## [2.0.0-beta.4]

### Fixed

- Added missing `select.py`
- Fixed integration setup failure

### Safety

Observation-only.

---

## [2.0.0-beta.3]

### Added

- Python implementation of the legacy optimizer calculations
- Configurable parameters and operating mode
- Forecast and energy-planning sensors
- Calculated controller mode and output target

### Safety

Observation-only.

---

## [2.0.0-beta.2]

### Fixed

- Changed integration type to `device`
- Improved HACS update handling

### Safety

Observation-only.

---

## [2.0.0-beta.1]

### Added

- First HACS-compatible custom integration
- Config Flow
- Source entity selection
- Unit normalization
- Grid and battery diagnostics
- German and English translations

### Safety

Observation-only.

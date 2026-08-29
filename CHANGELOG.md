## [2.1.0-beta.8] - 2026-08-29

### Fixed

- Corrected migration of stale explicit colors in already stored NOAH dashboards
- Recognized generated standard ApexCharts now receive the current stable palette even when an older `color` value already exists
- Fixed the remaining upgrade case where updated dashboard templates alone did not change the colors of an existing stored dashboard

### Changed

- Dashboard template storage version increased from 17 to 18
- Standard charts are identified by known title and expected entity combination before colors are changed
- Custom or additional ApexCharts cards are not modified by the v18 color migration
- Bundled SOC history card frontend cache version increased from `v7` to `v8`
- Integration version updated to `2.1.0-beta.8`

### Standard palette

- blue `#2196F3`
- green `#009B21`
- orange `#FF6A00`
- yellow `#FFD800`
- cyan `#00FFFF`
- violet `#B200FF`

### Safety

This release changes dashboard presentation and migration only. Optimizer
calculations and active NOAH control behavior are unchanged.

---

## [2.1.0-beta.7]

### Dashboard color consistency

- Completed the fixed series-color definitions in the generated dashboard templates
- Historical SOC presentation uses blue / green / orange / yellow
- Controller behavior uses blue / green / orange / yellow / cyan / violet
- Template version 17 aligned the final standard chart defaults

### Known issue fixed by beta.8

Existing stored dashboards could retain stale explicit colors because the
migration preserved already present `color` entries too broadly.

---

## [2.1.0-beta.4]

### Added

- Date-selectable SOC schedule history card
- Historical actual SOC, dynamic SOC target and configured target SOC
- Persistent forecast/SOC-plan snapshots
- Plan snapshot selection for past days
- Bundled history-card frontend resource

### Changed

- Standard dynamic-SOC chart migrated to the bundled history card
- Snapshot history limited to 31 rolling days
- Stored snapshots remain diagnostic and do not affect active control

---

## [2.1.0-beta.3]

### Added

- Reuse of the complete time-resolved Forecast.Solar power curve already loaded by Home Assistant
- PV forecast curve diagnostics
- Effective daily forecast and forecast update timestamp
- Forecast-shaped SOC schedule with daylight fallback
- Dashboard forecast chart

### Changed

- No additional Forecast.Solar API calls are made
- Actual PV production does not retroactively reshape the plan

---

## [2.1.0-beta.2]

### Added

- `soc_hold` controller mode

### Fixed

- Prevented the old forecast-margin path from selecting charge priority again after the dynamic schedule is already satisfied
- SOC-hold target is PV-only and rounded downward

---

## [2.1.0-beta.1]

### Added

- Passive persistent PV learning
- Median correction factor from up to seven valid days
- Minimum three valid days before application
- Opt-in learned forecast correction
- Reset button and diagnostics

### Safety

PV learning is passive by default and application of the learned factor is
disabled by default.

---

## [2.0.0]

### Release

- First stable release of the 2.x integration
- Promoted the tested Beta-14 feature set to stable

---

## [2.0.0-beta.14]

### Added

- `pv_redirect` controller mode
- dedicated translated controller-status enum sensor
- dedicated night state for the SOC schedule

### Fixed

- Reduced avoidable grid import while the battery charges although the SOC schedule is already met
- Replaced misleading night `ahead` status
- Improved `waiting_for_retry` display text

### Changed

- PV diversion is capped by `min(grid import, battery charging power)`
- load-following modes use the faster controller cadence
- dashboard migration updated the status card

---

## [2.0.0-beta.13]

### Fixed

- Faster predictive SOC-release response to changing household load
- `rate_limited` only when a command is actually pending

### Changed

- Controller evaluation every 15 seconds
- SOC-release increases may be written every 30 seconds
- Normal modes retain the two-minute interval

---

## [2.0.0-beta.12]

### Fixed

- Corrected predictive SOC-release refill reserve
- Corrected catch-up charging to target the future point of a rising schedule

---

## [2.0.0-beta.11]

### Added

- Predictive SOC release
- forecast-required minimum SOC
- SOC release floor
- releasable battery energy
- SOC release target
- `soc_release` mode

### Safety

Predictive SOC release is opt-in.

---

## [2.0.0-beta.10]

### Changed

- Dynamic SOC target rebuilt as a real time-based charging schedule
- Remaining forecast raises the schedule progressively

---

## [2.0.0-beta.9]

### Fixed

- Repaired malformed controller-status Jinja migration from Beta 8
- Existing migrated dashboards are repaired selectively

---

## [2.0.0-beta.8]

### Added

- Dynamic SOC target
- SOC deviation
- schedule status
- catch-up charging power
- separate dynamic SOC switch
- `soc_catchup` mode
- dashboard SOC chart

---

## [2.0.0-beta.7]

### Fixed

- Corrected battery energy-flow direction in the dashboard

---

## [2.0.0-beta.6]

### Added

- Integration-managed Lovelace dashboard
- Dynamic entity resolution
- Power-flow and diagnostics cards

---

## [2.0.0-beta.5]

### Added

- Optional active NOAH output control
- command deadband
- rate limiting
- retry handling
- failsafe
- legacy-controller interlock

---

## [2.0.0-beta.4]

### Fixed

- Added missing `select.py`
- Fixed integration setup failure

---

## [2.0.0-beta.3]

### Added

- Ported optimizer calculation logic to Python

---

## [2.0.0-beta.2]

### Fixed

- Integration type changed to `device`
- Improved HACS update handling

---

## [2.0.0-beta.1]

### Added

- First HACS-compatible custom integration
- Config Flow
- source entity selection
- unit normalization
- observation-only diagnostics

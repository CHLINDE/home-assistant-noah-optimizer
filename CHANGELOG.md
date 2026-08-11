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

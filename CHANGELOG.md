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

## [2.0.0-beta.4]

### Fixed

- Added the missing `select.py` platform.
- Fixed integration setup failure introduced in `2.0.0-beta.3`.

### Safety

This release remains observation-only and does not write to the
NOAH System Output Power entity.

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

## [2.0.0-beta.2]

### Fixed

- Changed the Home Assistant integration type from `helper` to `device`.
- The NOAH Optimizer is now handled as a regular device integration.
- Improved visibility of the integration under Settings → Devices & services.

### Changed

- Integration version updated to `2.0.0-beta.2`.

### Safety

This release remains observation-only and does not send commands to the NOAH.

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

- active optimizer control
- forecast-based output calculation
- configurable optimizer parameters
- dynamic SOC target curve
- learned home load
- failsafe
- multi-system support
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
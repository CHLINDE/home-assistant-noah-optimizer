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
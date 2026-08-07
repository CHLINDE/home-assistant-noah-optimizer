# HACS Integration Beta

## 2.0.0-beta.1

The first HACS beta is intended to validate installation, configuration
and sensor calculations before active control is implemented.

## Observation mode

This release does not modify the NOAH configuration.

It does not call:

`number.set_value`

The existing YAML optimizer can therefore remain active.

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

- positive = grid import
- negative = grid export

If the source sensor uses the opposite convention, enable
`Invert grid power sign` during setup.

## Limitations

Version 2.0.0-beta.1 does not yet include:

- optimizer parameters
- forecast-based control
- SOC target curve
- learned home load
- manual output control
- automatic output control
- failsafe control
- multiple independent NOAH systems
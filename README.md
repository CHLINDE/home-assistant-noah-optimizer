# Home Assistant Growatt NOAH Optimizer

Prognosebasierte Steuerung der Ausgangsleistung eines Growatt NOAH 2000
über Home Assistant und Noah-MQTT.

## Ziele

- Netzbezug reduzieren
- PV-Einspeisung bei nicht vollem Akku reduzieren
- Akku bis zum Abend auf einen konfigurierbaren Ziel-SOC laden
- Nachtentladung bis zu einem Mindest-SOC
- Wetterprognose über Forecast.Solar berücksichtigen
- vollständige Dashboardübersicht bereitstellen

## Dashboard

### HACS integration

Starting with `2.0.0-beta.6`, the HACS integration automatically creates
a dedicated NOAH Optimizer dashboard.

No changes to `configuration.yaml` are required.

### Legacy YAML optimizer

The file:

`dashboards/noah_dashboard.yaml`

remains the example dashboard for the legacy YAML optimizer and is not
used by the HACS integration.

### Browseransicht

![NOAH Optimizer Dashboard im Browser](screenshots/noah_dashboard_browser.png)

### Mobile Ansicht

![NOAH Optimizer Dashboard auf dem iPhone](screenshots/noah_dashboard_iPhone.jpeg)

## Voraussetzungen

- Home Assistant

### Home-Assistant-Komponenten

- [HACS](https://www.hacs.xyz/)
- [Noah-MQTT](https://github.com/mtrossbach/noah-mqtt)
- [Forecast.Solar](https://www.home-assistant.io/integrations/forecast_solar/)

### Erforderliche HACS-Dashboardkarten

- [Power Flow Card Plus](https://github.com/flixlix/power-flow-card-plus)
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card)

## Legacy-YAML-Installation

1. `noah_optimizer.yaml` nach `/config/packages/` kopieren.
2. Alle Platzhalter-Entity-IDs ersetzen.
3. Package-Unterstützung in `configuration.yaml` aktivieren.
4. Konfiguration prüfen.
5. Home Assistant neu starten.
6. Dashboard importieren.
7. Optimierer zunächst ausgeschaltet testen.

Eine ausführliche Anleitung befindet sich unter:

- [Installation](docs/installation.md)
- [Konfiguration](docs/configuration.md)
- [Fehlerbehebung](docs/troubleshooting.md)
- [HACS Integration Beta](docs/hacs-beta.md)

## Wichtiger Hinweis

Die Steuerung verwendet die inoffizielle Noah-MQTT-Anbindung und ist keine
offizielle Growatt-Lösung. Nutzung auf eigene Verantwortung.

## HACS Integration – Beta

A HACS-compatible Custom Integration is currently under development.

### Version 2.0.0-beta.1

The first beta is observation-only.

It:

- reads existing Home Assistant entities
- normalizes W/kW and Wh/kWh
- calculates grid import and grid export
- calculates home load and battery power
- checks Forecast.Solar availability
- checks NOAH System Output Power availability
- does not send any commands to the NOAH

The beta can therefore run in parallel with the existing YAML optimizer.

### Version 2.0.0-beta.2

Beta 2 focuses on integration structure and HACS update handling.

Changes include:

- changed the Home Assistant integration type from `helper` to `device`
- improved visibility under **Settings → Devices & services**
- verified that the existing configuration entry is preserved during a HACS update
- verified that the selected source entities remain configured after updating
- verified that existing entities are not duplicated or recreated
- verified the HACS update path from `2.0.0-beta.1` to `2.0.0-beta.2`

The optimizer remains observation-only in this version.

Version 2.0.0-beta.2 does **not** write to the NOAH System Output Power
entity.

### Version 2.0.0-beta.3

Beta 3 contains the complete calculation logic of the existing YAML
optimizer.

It calculates:

- forecast-based charging requirement
- remaining household energy requirement
- forecast margin and coverage
- self-consumption target
- charge-priority target
- controller mode
- final NOAH output target

The calculated output target is observation-only.

Version 2.0.0-beta.3 does **not** write to the NOAH System Output Power
entity and can therefore still be compared with the active YAML optimizer.

### Version 2.0.0-beta.4

Beta 4 fixes the integration setup failure introduced in Beta 3.

Changes include:

- added the missing `select.py` platform
- restored successful loading of the integration
- restored the operating mode selector
- verified that the existing configuration entry remains intact
- verified that all previously configured source entities remain available
- verified that the optimizer calculations continue to match the legacy YAML optimizer

The calculated values were compared against the legacy YAML optimizer.
For identical configuration parameters, the relevant calculation results,
controller mode, and final output target matched the YAML implementation.

Beta 4 remains observation-only.

Version 2.0.0-beta.4 does **not** write to the NOAH System Output Power
entity and can therefore still run in parallel with the active YAML optimizer.

### Version 2.0.0-beta.5

Beta 5 introduces optional active NOAH output control.

Active control:

- is disabled by default
- uses the calculated output target from the optimizer
- respects the configured command deadband
- rate-limits normal output commands
- retries a setpoint if the NOAH has not applied it
- sets the output to 0 W after prolonged loss of critical measurement data, if the actuator is reachable
- creates a Home Assistant notification after prolonged loss of critical measurement data
- blocks output commands while the legacy YAML optimizer is still enabled

The existing optimizer calculation switch and the new active-control
switch are intentionally separate.

Before enabling active HACS control, the legacy YAML optimizer must be
disabled.

## Important safety note

Versions `2.0.0-beta.1` through `2.0.0-beta.4` are observation-only.

Starting with version `2.0.0-beta.5`, optional active NOAH output control
is available. Active control is disabled by default and must be enabled
explicitly.

The legacy YAML optimizer and the HACS optimizer must never actively
control the same NOAH at the same time. Beta 5 contains an additional
software interlock that blocks HACS output commands while the legacy
`input_boolean.noah_optimizer_enabled` is on.

### Version 2.0.0-beta.6

Beta 6 introduces automatic dashboard installation.

The integration creates a dedicated **NOAH Optimizer** Home Assistant
dashboard when it is first set up or after upgrading from an earlier beta.

The dashboard:

- is shown in the Home Assistant sidebar by default
- dynamically resolves the integration's actual entity IDs
- supports entity IDs changed by Home Assistant area naming
- displays grid import and export separately
- displays battery charging and discharging separately
- includes active-controller status and command diagnostics
- includes forecast, energy-planning and controller-history charts
- includes optimizer configuration and calibration controls
- is only initialized once and is not overwritten after user customization

For new installations, sidebar visibility can be selected during setup.
Existing installations upgrading from an earlier beta default to showing
the dashboard in the sidebar.

The enhanced dashboard requires:

- Power Flow Card Plus
- ApexCharts Card

These dashboard cards are not installed automatically.
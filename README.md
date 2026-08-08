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

## Installation

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

## Wichtiger Hinweis

Die Steuerung verwendet die inoffizielle Noah-MQTT-Anbindung und ist keine
offizielle Growatt-Lösung. Nutzung auf eigene Verantwortung.

## HACS Integration – Beta

A new HACS-compatible Custom Integration is currently under development.

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

> The YAML optimizer remains the active controller during the beta test.

## Important safety note

Version 2.0.0-beta.1 does not write to the NOAH output power entity.

Future beta versions may add active control. Once active control is
introduced, the YAML optimizer and the HACS optimizer must never control
the same NOAH simultaneously.

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
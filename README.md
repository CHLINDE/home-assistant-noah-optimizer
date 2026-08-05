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

## Wichtiger Hinweis

Die Steuerung verwendet die inoffizielle Noah-MQTT-Anbindung und ist keine
offizielle Growatt-Lösung. Nutzung auf eigene Verantwortung.
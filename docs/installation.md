# Installation

Diese Anleitung beschreibt die Installation des **Home Assistant Growatt NOAH Optimizers**.

Ab Version `2.0.0-beta.6` ist die HACS-Integration der empfohlene
Installationsweg.

Die ältere YAML-Package-Version wird weiterhin unterstützt und ist weiter
unten separat beschrieben.

---

# 1. HACS-Integration

## 1.1 Voraussetzungen

Für den Optimierer werden benötigt:

- Home Assistant
- HACS
- ein funktionsfähiger MQTT-Broker
- eine laufende Noah-MQTT-Anbindung für den Growatt NOAH
- Forecast.Solar
- die Home-Assistant-Sun-Integration
- ein saldierter Netzleistungssensor
- eine beschreibbare `number`-Entität für NOAH System Output Power

Für das mitgelieferte Dashboard werden zusätzlich benötigt:

- Power Flow Card Plus
- ApexCharts Card

Die beiden Dashboardkarten sind nur für die Darstellung erforderlich.

Der Optimierer selbst funktioniert auch ohne Power Flow Card Plus und
ApexCharts Card.

---

## 1.2 Erforderliche Home-Assistant-Komponenten

Vor der Installation des Optimierers sollten folgende Komponenten
eingerichtet sein:

| Komponente | Zweck |
|---|---|
| MQTT | Übertragung der NOAH-Daten zwischen Noah-MQTT und Home Assistant |
| Noah-MQTT | Bereitstellung der NOAH-Sensoren und der Stellgröße System Output Power |
| Forecast.Solar | PV-Ertragsprognose |
| Sun | Sonnenuntergang und Tag-/Nachtberechnung |
| HACS | Installation der Custom Integration und der Dashboardkarten |
| Power Flow Card Plus | Darstellung des aktuellen Energieflusses |
| ApexCharts Card | Darstellung von Leistungs-, SOC- und Prognoseverläufen |

Weitere Informationen:

- MQTT: https://www.home-assistant.io/integrations/mqtt/
- Noah-MQTT: https://github.com/mtrossbach/noah-mqtt
- Forecast.Solar: https://www.home-assistant.io/integrations/forecast_solar/
- HACS: https://www.hacs.xyz/
- Power Flow Card Plus: https://github.com/flixlix/power-flow-card-plus
- ApexCharts Card: https://github.com/RomRider/apexcharts-card

---

## 1.3 Benötigte Quell-Entitäten

Vor dem Einrichten der Integration müssen folgende Entitäten in
Home Assistant vorhanden sein:

| Funktion | Entitätstyp | Typische Einheit |
|---|---|---|
| Saldierte Netzleistung | `sensor` | W oder kW |
| NOAH Solar Power | `sensor` | W oder kW |
| NOAH Output Power | `sensor` | W oder kW |
| NOAH SOC | `sensor` | % |
| NOAH Charging Power | `sensor` | W oder kW |
| NOAH Discharge Power | `sensor` | W oder kW |
| Forecast.Solar Restprognose heute | `sensor` | Wh oder kWh |
| NOAH System Output Power | `number` | W oder kW |

Die vorhandenen Entity-IDs können unter:

**Werkzeuge → Zustände**

ermittelt werden.

### Netzvorzeichen

Der Optimierer erwartet:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
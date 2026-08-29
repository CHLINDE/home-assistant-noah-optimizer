# Installation

Diese Anleitung beschreibt Installation und Update des **Home Assistant Growatt
NOAH Optimizers** für den Pre-Release `2.1.0-beta.8`.

## 1. Voraussetzungen

Benötigt werden:

- Home Assistant
- HACS
- MQTT
- Noah-MQTT
- Forecast.Solar
- Sun-Integration
- saldierter Netzleistungssensor
- beschreibbare `number`-Entität für NOAH System Output Power

Für das vollständige Dashboard zusätzlich:

- Power Flow Card Plus
- ApexCharts Card

Die historische SOC-Ladeplankarte wird mit der Integration ausgeliefert.

## 2. Quell-Entitäten

| Funktion | Entitätstyp | Einheit |
|---|---|---|
| Saldierte Netzleistung | `sensor` | W oder kW |
| NOAH Solar Power | `sensor` | W oder kW |
| NOAH Output Power | `sensor` | W oder kW |
| NOAH SOC | `sensor` | % |
| NOAH Charging Power | `sensor` | W oder kW |
| NOAH Discharge Power | `sensor` | W oder kW |
| Forecast.Solar Restprognose heute | `sensor` | Wh oder kWh |
| NOAH System Output Power | `number` | W oder kW |

Für den zeitaufgelösten Forecast-Ladeplan sollte die Restprognose direkt von
Forecast.Solar stammen. Bei Template-/Fremdsensoren wird automatisch der
Tageslicht-Fallback verwendet.

Erwartetes Netzvorzeichen:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

## 3. Dashboard-Abhängigkeiten

In HACS installieren:

```text
Power Flow Card Plus
ApexCharts Card
```

Browser/App danach vollständig neu laden.

## 4. Repository hinzufügen

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

## 5. Pre-Release installieren

In HACS Vorabversionen aktivieren und auswählen:

```text
2.1.0-beta.8
```

Danach Home Assistant vollständig neu starten.

## 6. Neue Installation

Unter:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

nach:

```text
Growatt NOAH Optimizer
```

suchen und die acht Quellentitäten auswählen.

Zusätzliche Setup-Optionen:

- Netzvorzeichen umkehren
- Dashboard in Seitenleiste anzeigen

## 7. Update auf beta.8

Vor dem Update wird empfohlen:

```text
NOAH-Steuerung aktiv = Aus
```

Beta 8 ändert keine Optimizer- oder Controllerberechnung. Die Änderung betrifft
die Migration des gespeicherten Dashboards.

Nach Installation und Neustart sollte die Integration ein Dashboard mit
Template-Version 18 speichern.

### Was wird bei der Migration geändert?

Nur eindeutig erkannte NOAH-Standard-ApexCharts:

- PV-Prognose
- älterer ApexCharts-SOC-Ladeplan
- Energieplanung bis Sonnenuntergang
- Leistung heute
- Reglerverhalten

Erkennung erfolgt über:

1. bekannten Kartentitel
2. passende Entity-Kombination

Zusätzliche benutzerdefinierte ApexCharts bleiben unangetastet.

### Reglerverhalten – erwartete Farben

```text
Regler-Soll                  #2196F3
Ist-Ausgang                  #009B21
Eigenverbrauch-Soll          #FF6A00
Ladepriorität-Soll           #FFD800
Nötige Ladeleistung          #00FFFF
Dynamische Nachladeleistung  #B200FF
```

### Historische SOC-Karte

```text
Ist-SOC             #2196F3
Dynamisches Soll    #009B21
Ziel-SOC            #FF6A00
Gespeicherter Plan  #FFD800
```

Der History-Card-Cache wird auf:

```text
v8
```

angehoben.

## 8. Update von 2.0.0

Zusätzlich zu den Beta-8-Farbkorrekturen enthält die 2.1-Reihe:

- PV-Learning
- SOC-Ladeplan halten
- zeitaufgelösten Forecast.Solar-Ladeplan
- Forecast-Diagnosekarte
- historische Ladeplanansicht
- Forecast-/Plan-Snapshots

Die gelernte PV-Korrektur bleibt standardmäßig aus.

## 9. Erste Prüfung

Nach Neustart zunächst:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Aus
Betriebsart = Automatik
```

Prüfen:

- Dashboard lädt ohne Fehler
- Template-Migration wurde durchgeführt
- Reglerverhalten hat die sechs definierten Farben
- historische SOC-Karte nutzt Blau/Grün/Orange/Gelb
- eigene zusätzliche ApexCharts wurden nicht verändert
- PV-Prognose und Leistung heute verwenden die Standardpalette

## 10. PV-Learning prüfen

Bei neuer Lernhistorie zunächst:

```text
Gelernte PV-Korrektur verwenden = Aus
PV-Learning bereit = Aus
```

Erst nach mindestens drei plausiblen Lerntagen die gelernte Korrektur
aktivieren.

## 11. Dynamischen SOC-Ladeplan prüfen

Bei nativer Forecast.Solar-Quelle sollte:

```text
Ladeplanbasis = Forecast.Solar-Kurve
```

angezeigt werden.

Andernfalls ist:

```text
Ladeplanbasis = Tageslicht-Fallback
```

zulässig.

## 12. SOC-Freigabe prüfen

Die Funktion benötigt:

- Automatik
- dynamische SOC-Steuerung
- eingeschaltete vorausschauende SOC-Freigabe
- Tagbetrieb
- positiven Netzbezug
- Ist-SOC oberhalb der Freigabegrenze

## 13. Stellgröße vor aktiver Steuerung testen

Unter **Werkzeuge → Aktionen**:

```yaml
action: number.set_value
target:
  entity_id: number.dein_noah_system_output_power
data:
  value: 300
```

Danach prüfen, ob die Stellgröße den Wert übernimmt.

## 14. Aktive Steuerung einschalten

Erst nach plausibler Prüfung:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Ein
```

Weitere Funktionen nach Bedarf aktivieren.

## 15. Schutzmechanismen

- Hysterese
- Stellgrößenraster
- Rate-Limit
- Retry
- Failsafe
- persistente Warnung
- Legacy-YAML-Sperre
- sichere Reduktionen nach Load-Following-Modi

## 16. Legacy-YAML-Optimizer

Nicht gleichzeitig mit der HACS-Steuerung aktiv verwenden.

Die HACS-Integration prüft weiterhin:

```text
input_boolean.noah_optimizer_enabled
```

## 17. Weiterführende Dokumentation

- [Konfiguration](configuration.md)
- [Fehlerbehebung](troubleshooting.md)
- [HACS Beta / Pre-Release](hacs-beta.md)

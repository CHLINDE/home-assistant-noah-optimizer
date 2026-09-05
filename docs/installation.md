# Installation

Diese Anleitung beschreibt Installation und Update des **Home Assistant
Growatt NOAH Optimizers** für den stabilen Release `2.0.0` und den aktuellen
Pre-Release `2.1.0-beta.11`.

## 1. Voraussetzungen

- Home Assistant
- HACS
- MQTT
- aktuelle Noah-MQTT-Version mit `Connectivity`-Binary-Sensor
- Forecast.Solar
- Sun-Integration
- saldierter Netzleistungssensor
- beschreibbare `number`-Entität für NOAH System Output Power

Dashboard zusätzlich:

- Power Flow Card Plus
- ApexCharts Card

Die historische SOC-Karte wird mit der Integration ausgeliefert.

Beta 10 wertet automatisch den Noah-MQTT-Binary-Sensor **Connectivity** aus,
der zum selben Home-Assistant-Gerät wie **NOAH System Output Power** gehört.
Eine zusätzliche Auswahl im Config Flow ist nicht erforderlich.

## 2. Benötigte Quell-Entitäten

| Funktion | Typ | Einheit |
|---|---|---|
| Netzleistung | `sensor` | W oder kW |
| Solar Power | `sensor` | W oder kW |
| Output Power | `sensor` | W oder kW |
| SOC | `sensor` | % |
| Charging Power | `sensor` | W oder kW |
| Discharge Power | `sensor` | W oder kW |
| Restprognose heute | `sensor` | Wh oder kWh |
| System Output Power | `number` | W oder kW |

Netzvorzeichen:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

## 3. Dashboardkarten

Über HACS installieren:

```text
Power Flow Card Plus
ApexCharts Card
```

Danach Frontend vollständig neu laden.

## 4. Repository

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

Alternativ:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

## 5. Pre-Release installieren

HACS-Vorabversionen aktivieren.

Installieren:

```text
2.1.0-beta.11
```

Home Assistant vollständig neu starten.

## 6. Neue Installation

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

Suche:

```text
Growatt NOAH Optimizer
```

Acht Quellentitäten wählen.

Optionen:

- Netzvorzeichen umkehren
- Dashboard in Seitenleiste anzeigen

## 7. Sichere Erstkonfiguration

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Aus
Dynamische SOC-Steuerung aktiv = Aus
Vorausschauende SOC-Freigabe aktiv = Aus
Gelernte PV-Korrektur verwenden = Aus
Betriebsart = Automatik
```

## 8. Update von 2.0.0 auf 2.1.0-beta.11

Vor dem Update:

```text
NOAH-Steuerung aktiv = Aus
```

Dann Beta 11 installieren und neu starten.

Beta 11 enthält gegenüber dem stabilen 2.0.0 zusätzlich:

- PV-Learning
- SOC-Ladeplan halten
- zeitaufgelöste Forecast.Solar-Kurve
- Forecast-Diagnose
- historische SOC-Karte
- Forecast-/Plan-Snapshots
- feste Serienfarben
- korrigierte Farbmigration
- erneute Reglerverhalten-Migration für ältere 5-Serien-Charts
- NOAH-Offline-Erkennung über Noah-MQTT Connectivity
- persistente Home-Assistant-Benachrichtigung bei Offline
- Sperre aller NOAH-Stellbefehle während Offline
- Schutz des PV-Learnings vor gecachten Offline-Messwerten

## Update von 2.1.0-beta.10 auf beta.11

Beta 11 korrigiert die Online-/Offline-Erkennung aus Beta 10.

Wenn das Dashboard trotz `Connectivity = on` nach einigen Minuten
**Stellgröße nicht verfügbar** anzeigt, ist dies der in Beta 11 behobene
`last_reported`-Fehler.

Nach dem Update:

1. Home Assistant vollständig neu starten.
2. Beim Noah-MQTT-Gerät prüfen, dass `Connectivity = Verbunden` / `on` ist.
3. Der NOAH Optimizer muss bei normal laufendem NOAH wieder einen verfügbaren
   Ausgangssollwert anzeigen.
4. Für einen echten Offline-Test die IoT-Verbindung des NOAH unterbrechen und
   prüfen, ob die persistente Offline-Benachrichtigung erscheint.
5. Nach Wiederherstellung von `Connectivity = on` muss die Sperre wieder
   aufgehoben werden.

Beta 11 benötigt keine Dashboard-Migration.

## 9. Update von 2.1.0-beta.4 bis beta.7

Wichtigster Beta-8-Punkt:

```text
Dashboard-Template-Version 17 -> 18
```

Alte explizite Serienfarben in gespeicherten Standardcharts werden korrigiert.

Eigene ApexCharts bleiben erhalten.

## 10. Update von 2.1.0-beta.8 auf beta.9

Beta 9 korrigiert speziell **Reglerverhalten** bei älteren gespeicherten
5-Serien-Charts.

Wichtig:

```text
Dashboard-Template-Version 18 -> 19
```

Der Versionssprung ist erforderlich, damit die Farbmigration bei einer bereits
mit Beta 8 auf Template 18 gespeicherten Installation erneut läuft.

Nach Installation Home Assistant vollständig neu starten und anschließend das
Dashboard neu öffnen.

## 11. Update von 2.1.0-beta.9 auf beta.10

Beta 10 ändert keine Dashboard-Template-Version.

Nach dem Neustart unter dem Noah-MQTT-Gerät prüfen:

```text
binary_sensor ... Connectivity = on
```

Der sichtbare Entity-Name darf durch Home Assistant umbenannt worden sein. Die
Zuordnung im Optimizer erfolgt über das Geräteobjekt und die Connectivity-
Geräteklasse bzw. Noah-MQTT-Unique-ID.

Zum Funktionstest kann die IoT-Verbindung des NOAH kurz unterbrochen werden.
Erwartet:

- persistente Benachrichtigung **NOAH Optimizer: NOAH offline**
- keine neuen Stellbefehle
- Daten-/Controllerstatus nicht mehr `OK` / `Synchron`
- nach Wiederverbindung automatische Entfernung der Benachrichtigung

## 12. Farben prüfen

Reglerverhalten:

```text
Regler-Soll                  #2196F3
Ist-Ausgang                  #009B21
Eigenverbrauch-Soll          #FF6A00
Ladepriorität-Soll           #FFD800
Nötige Ladeleistung          #00FFFF
Dynamische Nachladeleistung  #B200FF
```

Historischer SOC:

```text
Ist-SOC                      #2196F3
Dynamisches SOC-Soll         #009B21
Ziel-SOC                     #FF6A00
Gespeicherter Plan           #FFD800
```

History-Card-Cache:

```text
v8
```

## 13. Forecast.Solar prüfen

Bei nativer Quelle sollte die Ladeplanbasis auf die Forecast.Solar-Kurve
hinweisen.

Prüfen:

- Forecast-Aktualisierung
- rohe Forecast-Kurve
- wirksame Forecast-Kurve
- reale PV-Leistung

Bei nicht auflösbarer Quelle ist der Tageslicht-Fallback korrekt.

## 14. PV-Learning prüfen

Zunächst Anwendung aus lassen.

Beobachten:

- Prognosereferenz
- gemessene PV-Energie
- Lerntage
- Lernfaktor
- Learning bereit

Mindestens drei gültige Tage vor Anwendung.

Bei erkanntem NOAH-Offline-Zustand werden die Noah-MQTT-Messwerte nicht weiter
in das PV-Learning übernommen. Eine längere Tageslücke verwirft den Lerntag
gemäß der bestehenden Lernlogik.

## 15. Historische SOC-Karte prüfen

Testen:

- Heute
- vorheriger/nächster Tag
- Datumsauswahl
- gespeicherte Planstände

## 16. Dynamischen SOC-Ladeplan prüfen

Beobachten:

```text
Dynamisches SOC-Soll
SOC-Abweichung
SOC-Ladeplan
Dynamisch erforderliche Ladeleistung
```

Nachts:

```text
SOC-Ladeplan = Nachtbetrieb
```

## 17. SOC-Halten prüfen

Bei erfülltem Plan kann der Reglermodus **SOC-Ladeplan halten** erscheinen.

Keine absichtliche Akkuentladung.

## 18. SOC-Freigabe prüfen

Voraussetzungen:

- Automatik
- dynamische SOC-Steuerung
- SOC-Freigabe
- Tag
- Forecast
- Ist-SOC über Freigabegrenze
- positiver Netzbezug

## 19. PV-Umlenkung prüfen

Geeignet:

```text
Ist-SOC >= dynamisches SOC-Soll
Akkuladeleistung > 0
Netzbezug > 0
```

Erwartet:

```text
Reglermodus = PV-Umlenkung
```

## 20. Stellgröße manuell testen

Unter **Werkzeuge → Aktionen**:

```yaml
action: number.set_value
target:
  entity_id: number.dein_noah_system_output_power
data:
  value: 300
```

## 21. Aktive Steuerung

Erst nach plausibler Prüfung:

```text
NOAH-Steuerung aktiv = Ein
```

## 22. Schutzmechanismen

- Hysterese
- Stellgrößenraster
- Rate-Limit
- Retry
- Failsafe
- Legacy-Sperre
- schnelle sichere Reduzierungen
- NOAH-Connectivity-Guard
- Stale-Data-Erkennung
- Sperre von Normal- und Failsafe-Stellbefehlen bei Offline

## 23. Legacy-YAML

Nicht gleichzeitig aktiv verwenden.

## 24. Dashboard-Migrationsstände

```text
8   Dynamischer SOC
9   Jinja-Reparatur
10  SOC-Freigabe
11  Nachtstatus / PV-Umlenkung / Controllerstatus
12  PV-Learning
13  SOC-Ladeplan halten
14  Forecast.Solar-Kurve
15  Historische SOC-Karte
16  feste Serienfarben
17  Farbangleichung
18  Farbmigrationskorrektur
19  Reglerverhalten 5-/6-Serien-Migration
```

Beta 10 benötigt keine weitere Dashboard-Migration.

## Feste Dashboard-Farbpalette

Die von der Integration erzeugten Standarddiagramme verwenden eine feste
Farbpalette:

```text
Blau     #2196F3
Grün     #009B21
Orange   #FF6A00
Gelb     #FFD800
Cyan     #00FFFF
Violett  #B200FF
```

### Reglerverhalten

```text
Regler-Soll                  #2196F3  Blau
Ist-Ausgang                  #009B21  Grün
Eigenverbrauch-Soll          #FF6A00  Orange
Ladepriorität-Soll           #FFD800  Gelb
Nötige Ladeleistung          #00FFFF  Cyan
Dynamische Nachladeleistung  #B200FF  Violett
```

### Historischer SOC-Ladeplan

```text
Ist-SOC                      #2196F3  Blau
Dynamisches SOC-Soll         #009B21  Grün
Ziel-SOC                     #FF6A00  Orange
Gespeicherter Ladeplan       #FFD800  Gelb
```

### Dashboard-Migration in 2.1.0-beta.8

Beta 8 erhöht die Dashboard-Template-Version von `17` auf `18`.

Die vorherigen Farbänderungen hatten die Dashboardvorlagen bereits korrigiert.
In einem schon gespeicherten Lovelace-Dashboard konnten jedoch explizite alte
`color`-Werte erhalten bleiben. Dadurch waren nach einem Update weiterhin
falsche Farben sichtbar.

Template v18 korrigiert deshalb vorhandene Farben nur auf eindeutig erkannten
NOAH-Standard-ApexCharts. Für die Erkennung werden der bekannte deutsche oder
englische Kartentitel und die erwartete Entity-Kombination geprüft. Bei der
PV-Prognose werden zusätzlich die bekannten Data-Generatoren ausgewertet.

Eigene oder zusätzlich angelegte ApexCharts werden nicht pauschal verändert.

Die historische SOC-Karte verwendet bereits die aktuelle
Blau/Grün/Orange/Gelb-Palette. Ihr Frontend-Cache wird mit Beta 8 auf `v8`
angehoben.

Die Änderung betrifft ausschließlich Dashboarddarstellung und
Dashboardmigration. Optimizer-Berechnung und aktive NOAH-Regelung bleiben
unverändert.

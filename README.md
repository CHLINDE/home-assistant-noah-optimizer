# Home Assistant Growatt NOAH Optimizer

Prognosebasierte Steuerung der Ausgangsleistung eines Growatt NOAH 2000 über
Home Assistant und Noah-MQTT.

> **Status:** Stabiler Release `2.0.0`. Aktueller Pre-Release:
> `2.1.0-beta.8` mit korrigierter Dashboard-Farbmigration auf
> Template-Version 18.
>
> Die aktive Steuerung kann die NOAH-Ausgangsleistung verändern. Vor der
> Aktivierung sollten Quellwerte, Netzvorzeichen und Stellgröße geprüft werden.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

## Ziele

- Netzbezug reduzieren
- unnötige PV-Einspeisung bei noch aufnahmefähigem Speicher reduzieren
- Akku bis zum Abend auf einen konfigurierbaren Ziel-SOC laden
- Nachtentladung bis zu einem Mindest-SOC ermöglichen
- Forecast.Solar in die Ladeplanung einbeziehen
- dynamischen SOC-Ladeplan aus der zeitaufgelösten Forecast.Solar-Kurve ableiten
- systematische Abweichungen zwischen Forecast.Solar und realem PV-Ertrag lernen
- Regelzustand, Prognose und Energiefluss in einem Dashboard darstellen
- vergangene SOC-Ladepläne mit Ist-SOC, dynamischem Soll und Ziel-SOC nachvollziehen

## HACS-Integration

Aktuelle stabile Version:

```text
2.0.0
```

Aktueller Pre-Release:

```text
2.1.0-beta.8
```

Die 2.1-Betas erweitern den stabilen Regelstand schrittweise um PV-Learning,
SOC-Ladeplan halten, den zeitaufgelösten Forecast.Solar-Ladeplan und die
historische Ladeplanansicht.

`2.1.0-beta.8` repariert die Serienfarben-Migration für bereits vorhandene
Dashboards. Erkannte NOAH-Standarddiagramme werden einmalig auf die dokumentierte
Palette gesetzt; zusätzliche beziehungsweise benutzerdefinierte ApexCharts-Karten
bleiben unangetastet. Die Dashboard-Template-Version steigt dafür auf 18.

## Voraussetzungen

- Home Assistant
- HACS
- MQTT
- Noah-MQTT
- Forecast.Solar
- Sun-Integration
- saldierter Netzleistungssensor
- beschreibbare `number`-Entität für NOAH System Output Power

Für das erweiterte Dashboard zusätzlich:

- Power Flow Card Plus
- ApexCharts Card

Die beiden Custom Cards werden nicht automatisch installiert. Der Optimizer
selbst funktioniert auch ohne sie. Die historische SOC-Ladeplankarte wird mit
der Integration ausgeliefert.

## Installation über HACS

Repository:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

Danach **Growatt NOAH Optimizer** installieren und Home Assistant vollständig
neu starten. Für den Pre-Release müssen in HACS Vorabversionen berücksichtigt
werden.

> **Hinweis zu Home Assistant 2026.8 und neuer:** Home Assistant OS verwendet
> bei neuen Installationen standardmäßig Port 80 statt Port 8123. Home Assistant
> Container verwendet weiterhin standardmäßig Port 8123.

Weitere Dokumentation:

- [Installation](docs/installation.md)
- [Konfiguration](docs/configuration.md)
- [Fehlerbehebung](docs/troubleshooting.md)
- [HACS Beta / Pre-Release](docs/hacs-beta.md)

## Quell-Entitäten

Der Config Flow erwartet acht Quell-Entitäten:

| Funktion | Typ | Einheit |
|---|---|---|
| Saldierte Netzleistung | `sensor` | W oder kW |
| NOAH Solar Power | `sensor` | W oder kW |
| NOAH Output Power | `sensor` | W oder kW |
| NOAH SOC | `sensor` | % |
| NOAH Charging Power | `sensor` | W oder kW |
| NOAH Discharge Power | `sensor` | W oder kW |
| Forecast.Solar Restprognose heute | `sensor` | Wh oder kWh |
| NOAH System Output Power | `number` | W oder kW |

Erwartete Netzkonvention:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Bei umgekehrter Konvention kann **Netzvorzeichen umkehren** aktiviert werden.

## Regelung

Die Integration trennt Berechnung und aktive Stellwertausgabe. Die Berechnung
kann beobachtet werden, ohne die NOAH-Ausgangsleistung zu verändern.

Wichtige Betriebsarten und interne Reglermodi sind unter anderem:

- Automatik
- Eigenverbrauch
- Ladepriorität
- Manuell
- Nachtbetrieb
- SOC-Nachladung
- SOC-Freigabe
- PV-Umlenkung
- SOC-Ladeplan halten

Die aktive Steuerung bleibt opt-in. Legacy-YAML-Optimizer und HACS-Controller
dürfen nicht gleichzeitig denselben NOAH steuern.

## Dynamischer SOC-Ladeplan

Bei einer nativen Forecast.Solar-Quelle verwendet die Integration die von Home
Assistant geladene zeitaufgelöste Forecast.Solar-Leistungskurve. Daraus wird –
unter Berücksichtigung von Prognosefaktor, optionalem PV-Lernfaktor,
Ladeeffizienz und Energiereserve – der dynamische SOC-Ladeplan gebildet.

Die erwartete Hauslast wird separat in Prognosemarge und Ausgangsregelung
berücksichtigt. Es erfolgen keine zusätzlichen Forecast.Solar-API-Aufrufe.

Ist keine native Forecast.Solar-Kurve verfügbar, bleibt der Tageslicht-Ladeplan
als Fallback aktiv.

## PV-Learning

PV-Learning vergleicht den gemessenen PV-Tagesertrag mit Forecast.Solar und
bildet aus gültigen Lerntagen einen robusten Korrekturfaktor. Die Anwendung der
gelernten Korrektur ist optional und nach einer neuen Installation zunächst
ausgeschaltet.

## Historischer SOC-Ladeplan

Die integrierte Historienkarte ermöglicht:

- vorherigen/nächsten Tag auswählen
- Datum direkt auswählen
- zum heutigen Tag springen
- Ist-SOC, dynamisches SOC-Soll und Ziel-SOC aus Recorder/History anzeigen
- gespeicherte Forecast-/Plan-Snapshots für vergangene Tage vergleichen

Snapshots sind diagnostisch und beeinflussen die aktive Regelung nicht.

## Automatisches Dashboard

Die Integration erstellt ein eigenes Lovelace-Dashboard **NOAH Optimizer** und
löst die Entity-IDs dynamisch über die Home-Assistant-Entity-Registry auf.

Die initiale Sprache folgt Home Assistant:

- Deutsch → `dashboard_de.yaml`
- andere Sprachen → `dashboard_en.yaml`

### Dashboard-Migration in 2.1.0-beta.8

`2.1.0-beta.8` erhöht die Dashboard-Template-Version von 17 auf **18**. Die
Migration korrigiert die in Beta 7 verbliebenen alten `color`-Werte in eindeutig
erkannten NOAH-Standarddiagrammen. Sie erkennt diese Karten über die bekannten
Kartentitel und Entity-Kombinationen. Zusätzliche oder benutzerdefinierte
ApexCharts-Karten werden nicht verändert.

### Feste Serienfarben

Die generierten Standarddiagramme verwenden eine feste Palette:

```text
Blau    #2196F3
Grün    #009B21
Orange  #FF6A00
Gelb    #FFD800
Cyan    #00FFFF
Violett #B200FF
```

**Dynamischer SOC-Ladeplan**:

- Ist-SOC: Blau
- Dynamisches Soll: Grün
- Ziel-SOC: Orange
- gespeicherter historischer Plan: Gelb

**Reglerverhalten**:

- Regler-Soll: Blau
- Ist-Ausgang: Grün
- Eigenverbrauch-Soll: Orange
- Ladepriorität-Soll: Gelb
- erforderliche Ladeleistung: Cyan
- dynamische Nachladeleistung: Violett

Mit Template-Version 18 werden die Farben eindeutig erkannter generierter
NOAH-Standarddiagramme einmalig auf diese Palette ausgerichtet, auch wenn dort
bereits alte `color`-Werte gespeichert sind. Zusätzliche oder benutzerdefinierte
ApexCharts-Karten bleiben unangetastet.

## Energiefluss im Dashboard

Für Power Flow Card Plus gilt:

```text
Netz:
consumption = Netzbezug
production  = Netzeinspeisung

NOAH:
consumption = Entladeleistung
production  = Ladeleistung
```

## Sicherheit

- aktive Steuerung ist separat schaltbar
- Stellbefehle werden gerastert und mit Hysterese verarbeitet
- normale Regelzustände besitzen einen konservativen Mindestabstand
- Wiederholungsversuche und Stellwertübernahme werden überwacht
- bei länger fehlenden kritischen Daten greift ein Failsafe
- Legacy-Sperre verhindert parallele Steuerung durch den alten YAML-Optimizer

`2.1.0-beta.8` verändert **keine** Optimizer-Berechnung und **keine** aktive
Regellogik. Der Release betrifft Dashboard-Migration, Frontend-Cache,
Versionierung und Dokumentation.

## Versionshistorie

### 2.1.0-beta.8

- Dashboard-Farbmigration für bereits gespeicherte Standarddiagramme repariert
- Dashboard-Template-Version 17 → 18
- erkannte Standarddiagramme werden einmalig auf die definierte Palette gesetzt
- zusätzliche/benutzerdefinierte ApexCharts-Karten bleiben unverändert
- History-Card-Frontend-Cache `v=7` → `v=8`
- Manifest-Version auf `2.1.0-beta.8` korrigiert

### 2.1.0-beta.4 bis beta.7

Historische SOC-Ladeplanansicht, Forecast-/Plan-Snapshots und die abschließende
Farbangleichung der generierten Charts.

### 2.1.0-beta.3

Zeitaufgelöster Forecast.Solar-Ladeplan, Forecast-Diagnosesensoren und
PV-Prognosekarte.

### 2.1.0-beta.2

Reglermodus **SOC-Ladeplan halten** und Korrektur der doppelten
Prognosemargen-Auswertung bei erfülltem dynamischem Ladeplan.

### 2.1.0-beta.1

Passives PV-Learning mit persistentem Lernverlauf und optionaler Anwendung des
gelernten Faktors.

### 2.0.0

Erster stabiler Release der 2.x-Reihe auf Basis des getesteten
`2.0.0-beta.14`-Funktionsstands.

## Lizenz und Drittkomponenten

Die Integration verwendet Home Assistant und kann mit Noah-MQTT,
Forecast.Solar, Power Flow Card Plus und ApexCharts Card zusammenarbeiten.
Diese Komponenten werden nicht mit der Integration gebündelt, sofern oben nicht
explizit anders beschrieben.

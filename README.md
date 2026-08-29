# Home Assistant Growatt NOAH Optimizer

Prognosebasierte Steuerung der Ausgangsleistung eines Growatt NOAH 2000 über
Home Assistant und Noah-MQTT.

> **Status:** Stabiler Release `2.0.0`. Aktueller Pre-Release:
> `2.1.0-beta.8`.
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
- vergangene SOC-Ladepläne nachvollziehen
- Dashboardfarben für die Standarddiagramme konsistent halten

## Versionen

Aktuelle stabile Version:

```text
2.0.0
```

Aktueller Pre-Release:

```text
2.1.0-beta.8
```

### 2.1.0-beta.1 – PV-Learning

Passives PV-Learning vergleicht gemessenen PV-Tagesertrag mit Forecast.Solar.
Aus bis zu sieben gültigen Lerntagen wird ein robuster Lernfaktor gebildet.
Mindestens drei gültige Tage sind erforderlich. Die Anwendung des gelernten
Faktors ist standardmäßig ausgeschaltet.

### 2.1.0-beta.2 – SOC-Ladeplan halten

Ist der dynamische Ladeplan erfüllt, wird die alte Prognosemarge nicht nochmals
als Ladepriorität ausgewertet. Der Modus `soc_hold` nutzt aktuelle PV-Leistung
für den Hausverbrauch, ohne absichtlich Batterieenergie freizugeben.

### 2.1.0-beta.3 – zeitaufgelöste Forecast.Solar-Kurve

Wenn die konfigurierte Restprognose direkt von Forecast.Solar stammt, verwendet
der Optimizer die bereits von Home Assistant geladene Leistungskurve. Es werden
keine zusätzlichen Forecast.Solar-API-Aufrufe erzeugt.

Der Ladeplan berücksichtigt:

- Prognose-Sicherheitsfaktor
- optionalen PV-Lernfaktor
- Ladeeffizienz
- Forecast-Energiereserve
- zeitliche Verteilung der erwarteten PV-Leistung

Die erwartete Hauslast bleibt separat Bestandteil von Prognosemarge und
Ausgangsregelung.

### 2.1.0-beta.4 bis beta.7 – Historie und Farbpalette

Die Integration enthält eine datumsabhängige historische SOC-Ladeplanansicht
mit:

- Ist-SOC
- tatsächlich aktivem dynamischen SOC-Soll
- Ziel-SOC
- auswählbaren gespeicherten Forecast-/Planständen
- bis zu 31 Tagen Snapshot-Historie

Die Standarddiagramme verwenden eine feste Palette. Die historische SOC-Karte
nutzt:

```text
Ist-SOC:             #2196F3  Blau
Dynamisches Soll:    #009B21  Grün
Ziel-SOC:            #FF6A00  Orange
Gespeicherter Plan:  #FFD800  Gelb
```

`Reglerverhalten` verwendet:

```text
Regler-Soll:                    #2196F3  Blau
Ist-Ausgang:                    #009B21  Grün
Eigenverbrauch-Soll:            #FF6A00  Orange
Ladepriorität-Soll:             #FFD800  Gelb
Nötige Ladeleistung:            #00FFFF  Cyan
Dynamische Nachladeleistung:    #B200FF  Violett
```

### 2.1.0-beta.8 – Korrektur bestehender Dashboardfarben

Beta 8 behebt die Migration bereits gespeicherter Dashboards.

Die vorherige Migration ließ vorhandene explizite `color`-Werte weitgehend
unangetastet. Deshalb konnten alte Serienfarben trotz aktualisierter
Dashboardvorlagen erhalten bleiben.

Beta 8 erhöht die Dashboard-Template-Version auf:

```text
18
```

Bei eindeutig erkannten, von NOAH erzeugten Standard-ApexCharts werden die
Serienfarben auf die definierte Palette gesetzt. Erkannt wird nicht nur am
Titel, sondern zusätzlich an den erwarteten Entity-Kombinationen.

Dadurch werden insbesondere korrigiert:

- PV-Prognose
- Dynamischer SOC-Ladeplan bei älteren ApexCharts-Dashboards
- Energieplanung bis Sonnenuntergang
- Leistung heute
- Reglerverhalten

Zusätzliche oder selbst erstellte ApexCharts werden nicht pauschal verändert.

Die gebündelte historische SOC-Karte verwendet weiterhin Blau/Grün/Orange/Gelb.
Der Frontend-Cache wird auf `v8` erhöht, damit die aktuelle JavaScript-Datei
sicher neu geladen wird.

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

Die historische SOC-Karte wird direkt mit der Integration ausgeliefert.

## Installation über HACS

Repository:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

Bei Verwendung eines Pre-Releases müssen in HACS Vorabversionen für das
Repository angezeigt werden.

Nach Installation oder Update Home Assistant vollständig neu starten.

## Benötigte Quell-Entitäten

Beim Einrichten werden ausgewählt:

- saldierte Netzleistung
- NOAH Solar Power
- NOAH Output Power
- NOAH SOC
- NOAH Charging Power
- NOAH Discharge Power
- Forecast.Solar Restprognose heute
- NOAH System Output Power

Unterstützte Einheiten:

```text
Leistung: W oder kW
Energie:  Wh oder kWh
SOC:      %
```

Erwartete Netzkonvention:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

## Optimizer-Berechnung

Die Integration berechnet unter anderem:

- Netzbezug und Netzeinspeisung
- Hauslast
- Batterieleistung
- 5-Minuten-Mittelwert der Netzleistung
- Zeit bis Sonnenuntergang
- verfügbare Akkuenergie
- benötigte Ladeenergie
- wirksame PV-Restprognose
- vollständige Forecast.Solar-Leistungskurve
- Forecast-Aktualisierungszeitpunkt
- wirksame Tagesprognose
- prognostizierten End-SOC
- Ladeplanbasis
- PV-Prognosereferenz
- gemessene PV-Energie
- PV-Lernfaktor
- wirksamen Prognosefaktor
- erwarteten Hausenergiebedarf
- Prognosemarge
- Prognosedeckung
- erforderliche mittlere Ladeleistung
- Eigenverbrauch-Sollwert
- Ladeprioritäts-Sollwert
- dynamisches SOC-Soll
- SOC-Abweichung
- dynamisch erforderliche Nachladeleistung
- prognosebasierten Mindest-SOC
- SOC-Freigabegrenze
- freigebare Akkuenergie
- SOC-Freigabe-Sollwert
- Reglermodus
- Controllerstatus
- endgültigen Ausgangssollwert

## PV-Learning

Das Learning arbeitet passiv. Für einen gültigen Lerntag wird näherungsweise
gebildet:

```text
Tagesverhältnis
= gemessene PV-Energie / PV-Prognosereferenz
```

Der Lernfaktor ist der Median der letzten maximal sieben gültigen Tage.
Einzelwerte werden auf `0,50 ... 1,50` begrenzt.

Bei aktivierter gelernter Korrektur gilt:

```text
wirksamer Prognosefaktor
= Prognose-Sicherheitsfaktor × PV-Lernfaktor
```

## Betriebsarten

```text
Automatik
Eigenverbrauch
Ladepriorität
Manuell
```

### Automatik

Automatik kann abhängig von Situation und aktivierten Funktionen unter anderem
folgende internen Reglermodi verwenden:

- Mindest-SOC
- Ladepriorität
- Eigenverbrauch
- SOC-Nachladung
- SOC-Ladeplan halten
- SOC-Freigabe
- PV-Umlenkung
- Nachtbetrieb

### SOC-Ladeplan halten

Wenn der dynamische Ladeplan erfüllt ist:

```text
SOC-Halten-Soll
= min(aktuelle PV-Leistung, Eigenverbrauchs-Soll)
```

Das Ergebnis wird auf das Stellgrößenraster abgerundet, um keine absichtliche
Batterieentladung durch Aufrundung zu erzeugen.

### PV-Umlenkung

Bei gleichzeitigem Netzbezug und Akkuladung, obwohl der Akku mindestens am
dynamischen Soll liegt:

```text
PV-Umlenkungsleistung
= min(Netzbezug, Akkuladeleistung)
```

Die Umlenkung reduziert zunächst die Akkuladung. Eine absichtliche
Batterieentladung bleibt Aufgabe der SOC-Freigabe.

## Dynamischer SOC-Ladeplan

Bei nativer Forecast.Solar-Quelle folgt der Ladeplan der zeitlichen Verteilung
der wirksamen PV-Prognose. Die erwartete Hauslast wird nicht aus jedem
Forecast-Intervall abgezogen; sie bleibt separat Bestandteil der
Prognosemarge und Ausgangsregelung.

Bei nicht auflösbarer Forecast.Solar-Kurve wird automatisch der ältere
Tageslicht-Fallback verwendet.

Die Abweichung lautet:

```text
SOC-Abweichung = Ist-SOC - dynamisches SOC-Soll
```

Mehr als zwei Prozentpunkte Rückstand können `SOC-Nachladung` aktivieren.

## Historische Ladeplanansicht

Die Historienkarte erlaubt:

- vorheriger/nächster Tag
- Heute
- direkte Datumsauswahl
- Auswahl gespeicherter Planstände

Recorder-Daten werden nicht nachträglich neu berechnet. Die Snapshot-Historie
dient ausschließlich der Diagnose und greift nicht in die aktive Regelung ein.

## Vorausschauende SOC-Freigabe

Die optionale SOC-Freigabe verwendet eine separate Wiederauflade-Reserve:

```text
PV-Energie für Wiederaufladung
= wirksame Restprognose - zusätzliche Energiereserve
```

Die sichere Freigabegrenze schützt den größeren Wert aus dynamischem SOC-Soll
und prognosebasiertem Mindest-SOC plus Sicherheitsreserve.

Die Funktion ist standardmäßig ausgeschaltet.

## Aktive NOAH-Steuerung

Aktive Steuerung ist separat von der Optimizer-Berechnung schaltbar.

Schutzmechanismen:

- Stellgrößenraster
- Hysterese
- Mindestabstand zwischen normalen Stellbefehlen
- schnelleres Load-Following bei SOC-Freigabe/PV-Umlenkung
- Wiederholungsversuche
- Failsafe bei länger fehlenden kritischen Daten
- persistente Home-Assistant-Warnung
- Sperre gegen gleichzeitige Legacy-YAML-Steuerung

Der Legacy-YAML-Optimizer und die HACS-Steuerung dürfen denselben NOAH nicht
gleichzeitig aktiv regeln.

## Automatisches Dashboard

Das Dashboard wird durch die Integration verwaltet und nutzt dynamisch
aufgelöste Entity-IDs.

Inhalte unter anderem:

- Energiefluss
- SOC und Prognosedeckung
- historische SOC-Ladeplanansicht
- PV-Prognose
- Energieplanung
- Leistung heute
- Reglerverhalten
- Planungsdetails
- Kalibrierung
- Diagnose
- PV-Learning

### Dashboard-Migrationen

Die Migrationen sind gezielt und ersetzen das Dashboard nicht vollständig.

Wichtige Stände:

```text
11  Beta 14: Nachtstatus/PV-Umlenkung/Controllerstatus
12  2.1 beta1: PV-Learning
13  2.1 beta2: SOC-Ladeplan halten
14  2.1 beta3: Forecast.Solar-Kurve
15  2.1 beta4: historische SOC-Karte
16  Serienfarben
17  abschließende Farbangleichung
18  Korrektur stale expliziter Farben auf erkannten Standardcharts
```

## Sicherheit beim Update

Vor einem Pre-Release-Update empfiehlt sich:

```text
NOAH-Steuerung aktiv = Aus
```

Nach Neustart zuerst Dashboard, Sensoren und berechneten Sollwert prüfen.
Anschließend aktive Steuerung wieder einschalten.

## Projektstruktur

```text
home-assistant-noah-optimizer/
├── custom_components/
│   └── noah_optimizer/
├── dashboards/
├── docs/
├── screenshots/
├── CHANGELOG.md
├── LICENSE
├── README.md
├── THIRD_PARTY.md
└── hacs.json
```

## Lizenz

MIT License. Siehe `LICENSE` und `THIRD_PARTY.md`.

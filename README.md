# Home Assistant Growatt NOAH Optimizer

Prognosebasierte Steuerung der Ausgangsleistung eines Growatt NOAH 2000
über Home Assistant und Noah-MQTT.

> **Status:** Stabiler Release `2.0.0`. Aktueller Pre-Release:
> `2.1.0-beta.10`.
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
- einen erfüllten SOC-Ladeplan halten, ohne unnötig Ladepriorität auszulösen
- sicheren SOC-Vorsprung kontrolliert für den Hausverbrauch freigeben
- gleichzeitig vorhandene Akkuladung bei Netzbezug zum Haus umlenken
- Regelzustand, Prognose und Energiefluss im Dashboard darstellen
- historische SOC-Ladepläne und gespeicherte Forecast-Stände nachvollziehen
- konsistente Farben in allen NOAH-Standarddiagrammen verwenden
- einen offline bzw. nicht mehr aktualisierten NOAH erkennen
- Stellbefehle und PV-Learning gegen gecachte Offline-Daten absichern
- bei NOAH-Offline-Zustand eine persistente Home-Assistant-Benachrichtigung anzeigen

## HACS-Integration

Aktuelle stabile Version:

```text
2.0.0
```

Aktueller Pre-Release:

```text
2.1.0-beta.10
```

### 2.1.0-beta.1 – PV-Learning

PV-Learning arbeitet zunächst passiv. Die Integration vergleicht den
gemessenen PV-Tagesertrag mit der Forecast.Solar-Prognosereferenz.

Für einen gültigen Lerntag wird näherungsweise gebildet:

```text
Tagesverhältnis
= gemessene PV-Energie / PV-Prognosereferenz
```

Der PV-Lernfaktor ist der Median der letzten maximal sieben gültigen
Tagesverhältnisse. Ein Tageswert wird auf einen plausiblen Bereich begrenzt,
damit einzelne Ausreißer das Ergebnis nicht dominieren.

Mindestens drei gültige Lerntage sind erforderlich, bevor der Faktor
angewendet werden kann.

Ohne angewendetes Learning:

```text
wirksamer Prognosefaktor
= Prognose-Sicherheitsfaktor
```

Bei bereitem und aktiviertem Learning:

```text
wirksamer Prognosefaktor
= Prognose-Sicherheitsfaktor × PV-Lernfaktor
```

Die Anwendung ist standardmäßig ausgeschaltet.

### 2.1.0-beta.2 – SOC-Ladeplan halten

Ist der dynamische SOC-Ladeplan erfüllt, wird die alte Prognosemarge nicht
nochmals als Grund für eine unnötige Ladepriorität ausgewertet.

Der interne Modus **SOC-Ladeplan halten** verwendet die aktuelle
PV-Leistung für den Hausverbrauch, ohne absichtlich Akkuenergie freizugeben.

```text
SOC-Halten-Soll
= min(aktuelle PV-Leistung, Eigenverbrauchs-Soll)
```

Der Wert wird auf das Stellgrößenraster abgerundet.

### 2.1.0-beta.3 – zeitaufgelöste Forecast.Solar-Kurve

Wenn die konfigurierte Restprognose direkt zu Forecast.Solar gehört, verwendet
der Optimizer die bereits von Home Assistant geladene zeitaufgelöste
Leistungskurve.

Es werden keine zusätzlichen Forecast.Solar-API-Aufrufe erzeugt.

### 2.1.0-beta.4 – historische Ladeplanansicht

Die Integration liefert eine eigene historische SOC-Karte mit Datumsauswahl,
Recorder-Historie und gespeicherten Forecast-/Plan-Snapshots.

Forecast-/Plan-Snapshots werden für bis zu 31 Tage gespeichert.

### 2.1.0-beta.5 bis beta.7 – Serienfarben

Die Dashboard-Serienfarben wurden schrittweise auf eine feste Palette
vereinheitlicht.

### 2.1.0-beta.8 – Farbmigration

Beta 8 behebt den Upgrade-Fall, bei dem ein bestehendes gespeichertes
Dashboard trotz korrekter neuer Vorlagen noch alte explizite Serienfarben
enthielt.

Die Dashboard-Template-Version steigt auf 18.

### 2.1.0-beta.9 – Reglerverhalten-Migration

Beta 9 behebt den verbleibenden Upgrade-Fall beim Diagramm
**Reglerverhalten**. Bereits gespeicherte Dashboards können noch die ältere
5-Serien-Variante des Charts enthalten.

Die Migration akzeptiert sowohl die alte 5-Serien- als auch die aktuelle
6-Serien-Variante. Die Dashboard-Template-Version steigt auf **19**.

### 2.1.0-beta.10 – NOAH-Offline-Erkennung

Beta 10 wertet automatisch den von Noah-MQTT bereitgestellten
**Connectivity**-Binary-Sensor des konfigurierten NOAH aus.

Die Zuordnung erfolgt über dasselbe Home-Assistant-Gerät wie die konfigurierte
Entität **NOAH System Output Power**. Eine zusätzliche Auswahl im Config Flow
ist nicht erforderlich.

Als nicht sicher erreichbar gelten:

- `Connectivity = off`
- `unknown`
- `unavailable`
- eine zuvor erkannte Connectivity-Entität ist verschwunden
- ein weiterhin als `on` angezeigter Connectivity-Zustand wurde länger als
  drei Minuten nicht mehr gemeldet

Während des Offline-Zustands:

- werden keine normalen Stellbefehle gesendet
- wird auch kein 0-W-Failsafe-Befehl gesendet
- erscheint einmalig die persistente Benachrichtigung
  **NOAH Optimizer: NOAH offline**
- werden gecachte Noah-MQTT-Quellwerte nicht erneut in den Coordinator
  übernommen
- wird insbesondere PV-Learning pausiert, damit ein letzter gecachter
  PV-Leistungswert nicht als fiktive weitere Produktion integriert wird

Nach einem frischen Online-Status wird die Benachrichtigung automatisch
entfernt. Anschließend werden neue Quellwerte eingelesen und die normale
Regelung fortgesetzt.

Beta 10 benötigt keine neue Dashboard-Template-Version.

## Voraussetzungen

- Home Assistant
- HACS
- MQTT
- aktuelle Noah-MQTT-Version mit Connectivity-Binary-Sensor
- Forecast.Solar
- Sun-Integration
- saldierter Netzleistungssensor
- beschreibbare `number`-Entität für NOAH System Output Power

Für das erweiterte Dashboard zusätzlich:

- Power Flow Card Plus
- ApexCharts Card

Die beiden Custom Cards werden nicht automatisch installiert. Der Optimizer
selbst funktioniert auch ohne sie.

Die historische SOC-Karte wird mit der Integration ausgeliefert.

## Installation über HACS

### Direkt in HACS öffnen

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

> **Hinweis zu Home Assistant 2026.8 und neuer:**  
> Home Assistant OS verwendet bei neuen Installationen standardmäßig Port 80
> statt Port 8123. Home Assistant Container verwendet weiterhin standardmäßig
> Port 8123.

Alternativ:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

Für `2.1.0-beta.10` müssen in HACS Vorabversionen für dieses Repository
angezeigt werden.

Nach Installation oder Update Home Assistant vollständig neu starten.

Ausführliche Dokumentation:

- [Installation](docs/installation.md)
- [Konfiguration](docs/configuration.md)
- [Fehlerbehebung](docs/troubleshooting.md)
- [HACS Beta / Pre-Release](docs/hacs-beta.md)
- [NOAH-Offline-Erkennung](docs/offline-detection.md)

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

Zusätzlich wird automatisch der Noah-MQTT-Connectivity-Binary-Sensor des
NOAH-Geräts gesucht.

Unterstützte Einheiten:

```text
Leistung: W oder kW
Energie:  Wh oder kWh
SOC:      %
```

Die erwartete Netzkonvention lautet:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Bei umgekehrter Konvention kann **Netzvorzeichen umkehren** aktiviert werden.

## Optimizer-Berechnung

Die Integration berechnet unter anderem:

- Netzbezug und Netzeinspeisung
- Hauslast
- Batterieleistung
- 5-Minuten-Mittelwert der Netzleistung
- verbleibende Zeit bis Sonnenuntergang
- verfügbare Akkuenergie
- benötigte Ladeenergie
- wirksame PV-Restprognose
- vollständige Forecast.Solar-Leistungskurve
- Zeitpunkt der letzten Forecast-Aktualisierung
- wirksame Tagesprognose
- prognostizierten End-SOC
- Ladeplanbasis
- PV-Prognosereferenz
- gemessene PV-Energie
- PV-Lernfaktor
- wirksamen Prognosefaktor
- Bereitschaftsstatus des PV-Learnings
- erwarteten Hausenergiebedarf
- Prognosemarge
- Prognosedeckung
- erforderliche mittlere Ladeleistung
- verbleibende Zeit bis Ziel-SOC
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

## Betriebsarten

```text
Automatik
Eigenverbrauch
Ladepriorität
Manuell
```

### Automatik

Abhängig von Situation und freigeschalteten Funktionen sind unter anderem
möglich:

```text
Mindest-SOC
Eigenverbrauch
Ladepriorität
SOC-Nachladung
SOC-Ladeplan halten
SOC-Freigabe
PV-Umlenkung
Nachtbetrieb
Ziel-SOC erreicht
Konservativ ohne Prognose
```

### Eigenverbrauch

Die Ausgangsleistung wird so geregelt, dass der Netzbezug möglichst reduziert
wird.

### Ladepriorität

Ein Teil der verfügbaren PV-Leistung wird für das Erreichen des Ziel-SOC
reserviert.

### Manuell

Die konfigurierte manuelle Ausgangsleistung wird verwendet.

## Dynamischer SOC-Ladeplan

### Tagesfortschritt im Fallback

Zwischen Sonnenaufgang und Sonnenuntergang:

```text
p = vergangene Zeit seit Sonnenaufgang / Tageslichtdauer
```

### Zeitbasiertes Grund-Soll

```text
Zeit-Soll
= Mindest-SOC
  + p × (Ziel-SOC - Mindest-SOC)
```

### Native Forecast.Solar-Kurve

Bei direkt auflösbarer Forecast.Solar-Quelle wird die zeitaufgelöste
Leistungskurve verwendet.

### SOC-Abweichung

```text
SOC-Abweichung
= Ist-SOC - dynamisches SOC-Soll
```

Tagsüber:

```text
> +2 %-Punkte  = Vor Ladeplan
-2 ... +2      = Im Ladeplan
< -2           = Hinter Ladeplan
```

Nachts:

```text
Nachtbetrieb
```

## SOC-Ladeplan halten

Ist der Ladeplan erfüllt, kann der Modus **SOC-Ladeplan halten** verhindern,
dass die alte Prognosemarge unnötig wieder Ladepriorität auswählt.

## Vorausschauende SOC-Freigabe

Die Funktion ist separat schaltbar und standardmäßig aus.

```text
SOC-Freigabegrenze
= max(Dynamisches SOC-Soll, Prognosebasierter Mindest-SOC)
  + 2 %-Punkte
```

Die Funktion fordert keine absichtliche Netzeinspeisung aus dem Akku an.

## PV-Umlenkung

Wenn:

```text
Ist-SOC >= dynamisches SOC-Soll
Akkuladeleistung > 0 W
Netzbezug > 0 W
```

kann die Automatik vorhandene Akkuladung zum Haus umleiten:

```text
PV-Umlenkungsleistung
= min(Netzbezug, Akkuladeleistung)
```

Die Funktion fordert keine zusätzliche Akkuentladung an.

## Aktive Steuerung

Getrennte Schalter:

```text
Optimierer-Berechnung aktiv
NOAH-Steuerung aktiv
Dynamische SOC-Steuerung aktiv
Vorausschauende SOC-Freigabe aktiv
Gelernte PV-Korrektur verwenden
```

Schutzmechanismen:

- Stellgrößenraster
- Hysterese
- Mindestabstand zwischen normalen Stellbefehlen
- 15-Sekunden-Controllerauswertung
- 30-Sekunden-Lastnachführung bei SOC-Freigabe und PV-Umlenkung
- sofortige sicherheitsrelevante Sollwertreduzierungen
- Retry bei nicht bestätigtem Stellwert
- Failsafe
- persistente Home-Assistant-Warnung
- Sperre gegen gleichzeitige Legacy-YAML-Steuerung
- NOAH-Connectivity-Guard
- Stale-Data-Erkennung
- Sperre aller Stellbefehle bei erkanntem Offline-Zustand
- Pause der Quellwertübernahme/PV-Lernintegration während Offline

## Controllerstatus

Typische Rohzustände:

```text
disabled
optimizer_disabled
legacy_controller_active
critical_data_missing
actuator_unavailable
target_unavailable
rate_limited
waiting_for_retry
in_sync
command_sent
command_failed
failsafe
```

Während Beta 10 einen NOAH-Offline-Zustand erkennt, wird der bestehende Zustand
`actuator_unavailable` verwendet. Die persistente Benachrichtigung nennt die
Ursache ausdrücklich als **NOAH offline**.

## Automatisches Dashboard

Die Integration erzeugt das Dashboard:

```text
NOAH Optimizer
```

Standardsprache:

```text
Deutsch -> dashboard_de.yaml
sonst   -> dashboard_en.yaml
```

Dashboard-Inhalte:

- Energiefluss
- SOC und Prognosedeckung
- historische SOC-Ladeplanansicht
- PV-Prognose
- Energieplanung bis Sonnenuntergang
- Leistung heute
- Reglerverhalten
- Planungsdetails
- PV-Learning
- Kalibrierung
- Diagnose

## Feste Dashboard-Farbpalette

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

## Dashboard-Migrationshistorie

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
17  abschließende Farbangleichung
18  Korrektur alter expliziter Farben
19  Reglerverhalten: alte 5-Serien-Variante migrieren
```

Beta 10 benötigt keine neue Dashboard-Migration.

## Legacy-YAML-Optimizer

Die ältere Package-Variante bleibt im Repository:

```text
noah_optimizer.yaml
dashboards/noah_dashboard.yaml
```

Legacy-YAML und HACS dürfen denselben NOAH nicht gleichzeitig aktiv regeln.

## Sicherheit

Nach einem Pre-Release-Update zunächst:

```text
NOAH-Steuerung aktiv = Aus
```

Prüfen:

- Quellwerte
- Netzvorzeichen
- Forecast
- dynamisches SOC-Soll
- Controllerstatus
- Ausgangssollwert
- Noah-MQTT Connectivity
- Offline-Benachrichtigung
- Dashboard

Danach aktive Steuerung wieder freigeben.

## Versionshistorie

### 2.1.0-beta.10

- NOAH-Offline-Erkennung über Noah-MQTT Connectivity
- persistente Home-Assistant-Benachrichtigung
- normale und Failsafe-Stellbefehle bei Offline gesperrt
- Stale-Data-Erkennung
- gecachte Noah-MQTT-Werte werden während Offline nicht erneut verarbeitet
- PV-Learning integriert während Offline keine fiktive PV-Energie
- keine neue Dashboard-Template-Version

### 2.1.0-beta.9

- Template-Version 19
- Reglerverhalten erkennt alte 5-Serien- und aktuelle 6-Serien-Variante
- bestehende falsche Farben werden nach Beta 8 erneut migriert
- keine Änderung der Regelalgorithmen

### 2.1.0-beta.8

- Template-Version 18
- alte explizite Serienfarben auf eindeutig erkannten Standardcharts korrigiert
- eigene ApexCharts geschützt
- History-Card-Cache v8

### 2.1.0-beta.7

- abschließende Farbangleichung
- Reglerverhalten und historischer SOC-Ladeplan korrigiert
- Template-Version 17

### 2.1.0-beta.6

- Standardfarben der Dashboardserien vereinheitlicht

### 2.1.0-beta.5

- erste Vereinheitlichung der Serienfarben

### 2.1.0-beta.4

- historische SOC-Ladeplanansicht
- Recorder-Historie
- persistente Forecast-/Plan-Snapshots

### 2.1.0-beta.3

- zeitaufgelöste Forecast.Solar-Kurve
- keine zusätzlichen Forecast-API-Aufrufe
- Tageslicht-Fallback

### 2.1.0-beta.2

- SOC-Ladeplan halten

### 2.1.0-beta.1

- PV-Learning
- persistente Lernhistorie
- optionaler Lernfaktor

### 2.0.0

Erster stabiler Release der 2.x-Reihe. Funktionsstand entspricht
`2.0.0-beta.14`.

## Lizenz

MIT License. Siehe `LICENSE` und `THIRD_PARTY.md`.

# Konfiguration

Dieses Dokument beschreibt die HACS-Integration **Growatt NOAH Optimizer**
für den stabilen Release `2.0.0` und den aktuellen Pre-Release
`2.1.0-beta.10`.

Die tatsächlichen Entity-IDs können durch Bereichsnamen oder manuelle
Umbenennungen abweichen. Die Integration und das automatische Dashboard lösen
eigene Entitäten über stabile Unique IDs auf.

## 1. Schalter

### Optimierer-Berechnung aktiv

Aktiviert die Berechnung des Ausgangssollwerts.

### NOAH-Steuerung aktiv

Erlaubt das Schreiben auf die konfigurierte `NOAH System Output Power`-Entität.

Standard:

```text
Aus
```

### Dynamische SOC-Steuerung aktiv

Die dynamischen SOC-Sensoren werden auch bei ausgeschaltetem Schalter
berechnet. Ein aktiver Eingriff erfolgt nur in Automatik.

Standard:

```text
Aus
```

### Vorausschauende SOC-Freigabe aktiv

Erlaubt die kontrollierte Nutzung eines sicheren SOC-Vorsprungs.

Standard:

```text
Aus
```

### Gelernte PV-Korrektur verwenden

Der Lernprozess läuft passiv weiter. Erst dieser Schalter erlaubt die Anwendung
des Lernfaktors.

Standard:

```text
Aus
```

### PV-Lerndaten zurücksetzen

Löscht die persistente Lernhistorie.

## 2. Betriebsarten

```text
Automatik
Eigenverbrauch
Ladepriorität
Manuell
```

Mögliche interne Automatik-Modi:

```text
Eigenverbrauch
Ladepriorität
SOC-Nachladung
SOC-Ladeplan halten
SOC-Freigabe
PV-Umlenkung
Mindest-SOC
Nachtbetrieb
Ziel-SOC erreicht
Konservativ ohne Prognose
```

## 3. Dynamischer SOC-Ladeplan

### Tageslicht-Fallback

```text
p = vergangene Zeit seit Sonnenaufgang / Tageslichtdauer
```

```text
Zeit-Soll
= Mindest-SOC
  + p × (Ziel-SOC - Mindest-SOC)
```

### Konservative Prognose-Anforderung

```text
PV-Energie für Ladeplan
= wirksame Restprognose
  - erwarteter Hausenergiebedarf
  - zusätzliche Energiereserve
```

```text
Speicherbare Energie
= PV-Energie für Ladeplan × Ladewirkungsgrad
```

Aus dem möglichen zukünftigen SOC-Zuwachs entsteht die
Prognose-Anforderung.

### Prognosedruck im Fallback

```text
Prognosedruck
= max(Prognose-Anforderung - Zeit-Soll, 0)
```

```text
Dynamisches SOC-Soll
= Zeit-Soll + p × Prognosedruck
```

### Native Forecast.Solar-Kurve

Wenn die Restprognose sicher zu Forecast.Solar gehört, wird die bereits von
Home Assistant geladene zeitaufgelöste Leistungskurve verwendet.

Keine zusätzlichen API-Aufrufe.

Die wirksame Leistung berücksichtigt:

```text
Forecast-Leistung
× Prognose-Sicherheitsfaktor
× optionaler PV-Lernfaktor
```

Die erwartete Hauslast bleibt separat.

### Ladeplanbasis

Diagnosewert:

```text
Forecast.Solar-Kurve
```

oder:

```text
Tageslicht-Fallback
```

### SOC-Abweichung

```text
SOC-Abweichung = Ist-SOC - dynamisches SOC-Soll
```

Tagsüber:

```text
mehr als +2 %-Punkte    = Vor Ladeplan
-2 bis +2 %-Punkte      = Im Ladeplan
weniger als -2 %-Punkte = Hinter Ladeplan
```

Nachts:

```text
Nachtbetrieb
```

### Dynamische Nachladeleistung

Die Aktivierung erfolgt weiterhin erst bei mehr als zwei Prozentpunkten
Rückstand.

Das Nachholziel wird bis zum Ende des Nachholfensters projiziert:

```text
Nachholfenster
= min(SOC-Nachholzeit, Zeit bis Sonnenuntergang)
```

```text
Nachholziel
= dynamisches SOC-Soll am Ende des Nachholfensters
```

## 4. SOC-Ladeplan halten

Wenn der Plan erfüllt ist:

```text
SOC-Halten-Soll
= min(PV-Leistung, Eigenverbrauchs-Soll)
```

Der Sollwert wird nach unten auf das Stellgrößenraster gerundet.

Keine absichtliche Batterieentladung.

## 5. Vorausschauende SOC-Freigabe

Separate Wiederauflade-Reserve:

```text
PV-Energie für Wiederaufladung
= wirksame Restprognose
  - zusätzliche Energiereserve
```

Der erwartete Hausenergiebedarf wird nicht abgezogen.

```text
Prognosebasierter Mindest-SOC
= Ziel-SOC - möglicher Wiederauflade-SOC
```

```text
SOC-Freigabegrenze
= max(Dynamisches SOC-Soll, Prognosebasierter Mindest-SOC)
  + 2 %-Punkte
```

```text
Freigebare Akkuenergie
= Akkukapazität × max(Ist-SOC - SOC-Freigabegrenze, 0) / 100
```

Bei Netzbezug:

```text
SOC-Freigabe-Soll
= aktuelle NOAH-Ausgangsleistung + Netzbezug
```

## 6. PV-Umlenkung

Voraussetzungen:

- Automatik
- Tag
- Forecast verfügbar
- dynamische SOC-Steuerung aktiv
- Ist-SOC mindestens am dynamischen Soll
- Akkuladeleistung > 0
- Netzbezug > 0
- keine priorisierte SOC-Nachladung

```text
PV-Umlenkungsleistung
= min(Netzbezug, Akkuladeleistung)
```

Das Ergebnis wird sicher nach unten gerastert.

## 7. PV-Learning

### Tagesfaktor

```text
Tagesfaktor
= gemessene PV-Energie / PV-Prognosereferenz
```

Die letzten maximal sieben gültigen Tagesverhältnisse werden persistent
gespeichert. Ihr Median ergibt den PV-Lernfaktor.

Die im aktuellen Code verwendeten Gültigkeitskriterien sind:

```text
Lernfenster:                    7 gültige Tage
Mindestens erforderlich:        3 gültige Tage
Lernfaktor pro Tag:             0,50 ... 1,50
Mindest-Prognosereferenz:       0,25 kWh
Mindestbeobachtungszeit:        2 Stunden Tagesbetrieb
Mindest-Tageslichtfortschritt:  85 %
Maximale Tages-Messlücke:       10 Minuten
```

Ein erster deutlich zu spät begonnener Teil-Tag wird nicht gelernt. Ein neuer
Lerntag ist nur dann von Anfang an berechtigt, wenn die Beobachtung nachts oder
spätestens bei 15 % des Tageslichtfensters beginnt.

Die Prognosereferenz wird möglichst früh am Tag gebildet. Eine verfügbare
Restprognose kann vor Sonnenaufgang übernommen werden. Nach Sonnenaufgang wird
die Referenz nur innerhalb der ersten 20 % des Tageslichtfensters erfasst; der
bis dahin bereits gemessene PV-Ertrag wird zur Restprognose addiert.

Eine Messlücke von mehr als zehn Minuten, die die Tagesbeobachtung berührt,
verwirft den gesamten Lerntag, statt die fehlende PV-Produktion als Nullertrag
zu behandeln.

Das Learning läuft passiv. Der Faktor beeinflusst die Regelung erst, wenn
**Gelernte PV-Korrektur verwenden** eingeschaltet ist und mindestens drei
gültige Lerntage vorliegen.

### Verhalten bei NOAH offline

Ab Beta 10 werden Noah-MQTT-Quellwerte **nicht** erneut in das PV-Learning
übernommen, solange der Connectivity-Status des NOAH offline oder veraltet ist.
Das verhindert, dass ein gecachter letzter PV-Leistungswert über die
Offline-Zeit weiter integriert wird.

Nach Wiederverbindung bewertet die vorhandene PV-Learning-Logik die entstandene
Messlücke. Überschreitet eine Tageslücke zehn Minuten, wird der Lerntag
verworfen.

### Wirksamer Prognosefaktor

Ohne angewendetes Learning:

```text
wirksamer Prognosefaktor
= Prognose-Sicherheitsfaktor
```

Mit bereitem und aktiviertem Learning:

```text
wirksamer Prognosefaktor
= Prognose-Sicherheitsfaktor × PV-Lernfaktor
```

## 8. Wichtige Parameter

Die folgenden Standardwerte und Einstellbereiche entsprechen den aktuell in
`number.py` und `const.py` definierten Werten.

### Nutzbare Akkukapazität

```text
Standard:  2,048 kWh
Bereich:   0,500 ... 16,000 kWh
Schritt:   0,001 kWh
```

Gesamte nutzbare Kapazität der angeschlossenen NOAH-Speicher.

### Ziel-SOC bei Sonnenuntergang

```text
Standard:  95 %
Bereich:   50 ... 100 %
Schritt:   1 %
```

### Mindest-SOC

```text
Standard:  10 %
Bereich:   0 ... 30 %
Schritt:   1 %
```

Untergrenze und Startpunkt des Tagesplans.

### Angenommener Ladewirkungsgrad

```text
Standard:  0,90
Bereich:   0,70 ... 1,00
Schritt:   0,01
```

### Prognose-Sicherheitsfaktor

```text
Standard:  0,80
Bereich:   0,30 ... 1,20
Schritt:   0,01
```

Ohne angewendetes PV-Learning:

```text
wirksame Restprognose
= Restprognose × Prognose-Sicherheitsfaktor
```

Beispiel:

```text
Restprognose:                5,0 kWh
Prognose-Sicherheitsfaktor:  0,80
Wirksame Restprognose:       4,0 kWh
```

### Zusätzliche Energiereserve

```text
Standard:  0,25 kWh
Bereich:   0,00 ... 3,00 kWh
Schritt:   0,05 kWh
```

### Freigabemarge

```text
Standard:  0,50 kWh
Bereich:   0,05 ... 3,00 kWh
Schritt:   0,05 kWh
```

### Erwartete mittlere Hauslast

```text
Standard:  250 W
Bereich:   0 ... 1500 W
Schritt:   10 W
```

### Gewünschter Rest-Netzbezug

```text
Standard:  50 W
Bereich:   0 ... 250 W
Schritt:   10 W
```

### Maximale Ausgangsleistung

```text
Standard:  800 W
Bereich:   0 ... 800 W
Schritt:   10 W
```

### Maximale Ausgangsleistung nachts

```text
Standard:  400 W
Bereich:   0 ... 800 W
Schritt:   10 W
```

### Manuelle Ausgangsleistung

```text
Standard:  200 W
Bereich:   0 ... 800 W
Schritt:   10 W
```

### Stellgrößenraster

```text
Standard:  50 W
Bereich:   10 ... 200 W
Schritt:   10 W
```

### Schalt-Hysterese

```text
Standard:  50 W
Bereich:   10 ... 250 W
Schritt:   10 W
```

In den Lastfolgemodi **SOC-Freigabe** und **PV-Umlenkung** wird intern höchstens
eine Deadband von 25 W verwendet. Ist die konfigurierte Hysterese kleiner,
bleibt der kleinere konfigurierte Wert maßgeblich.

### SOC-Nachholzeit

```text
Standard:  2,0 h
Bereich:   0,5 ... 6,0 h
Schritt:   0,5 h
```

Ein kleinerer Wert reagiert aggressiver auf einen SOC-Rückstand. Ein größerer
Wert verteilt die Nachladung über einen längeren Zeitraum.

## 9. Diagnosewerte

- Netzbezug
- Netzeinspeisung
- Hauslast
- Batterieleistung
- Netzleistung 5 min
- Ladebedarf
- wirksame Restprognose
- Forecast-Aktualisierung
- wirksame Tagesprognose
- prognostizierter End-SOC
- Ladeplanbasis
- PV-Prognosereferenz
- gemessene PV-Energie
- PV-Lernfaktor
- PV-Learning bereit
- erwarteter Hausenergiebedarf
- Prognosemarge
- Prognosedeckung
- dynamisches SOC-Soll
- SOC-Abweichung
- SOC-Ladeplan
- dynamisch erforderliche Ladeleistung
- prognosebasierter Mindest-SOC
- SOC-Freigabegrenze
- freigebare Akkuenergie
- SOC-Freigabe-Soll
- Ausgangssollwert
- Reglermodus
- Controllerstatus

## 10. Controllerstatus

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

Während eines erkannten NOAH-Offline-Zustands verwendet Beta 10 bewusst den
bereits vorhandenen Status `actuator_unavailable`. Die eindeutige Diagnose
**NOAH offline** steht in der persistenten Home-Assistant-Benachrichtigung.

## 11. Befehlsintervalle

Die aktive Regelung wird unabhängig vom normalen Stellintervall alle 15
Sekunden ausgewertet.

```text
Controller-Auswertung:                  15 s
Normale Stellbefehle:                  120 s Mindestabstand
SOC-Freigabe / PV-Umlenkung:            30 s Mindestabstand
Deadband in Lastfolgemodi:          max. 25 W
Retry bei nicht übernommenem Soll:      20 min
```

Sicherheitsrelevante Sollwertreduzierungen nach **SOC-Freigabe**,
**PV-Umlenkung** oder beim Wechsel in **SOC-Ladeplan halten** können die normale
Wartezeit umgehen.

## 12. Failsafe

Fehlen kritische Daten mindestens zehn Minuten:

- persistente Home-Assistant-Warnung
- wenn die Stellgröße erreichbar ist, Anforderung von `0 W`
- Rücksetzen des Failsafe-Zustands und Schließen der Warnung nach Datenrückkehr

Bei einem erkannten NOAH-Offline-Zustand wird auch der 0-W-Failsafe-Befehl
blockiert. Ein vorhandener Failsafe-Zähler wird zurückgesetzt, damit nach der
Wiederverbindung kein alter Offline-Zeitraum sofort einen Schreibbefehl
auslöst.

## 13. NOAH-Offline-Erkennung

Beta 10 findet den Noah-MQTT-Binary-Sensor **Connectivity** automatisch über
dasselbe Home-Assistant-Gerät wie die konfigurierte Entität
**NOAH System Output Power**.

Als offline bzw. nicht sicher erreichbar gelten:

- `Connectivity = off`
- `unknown`
- `unavailable`
- eine zuvor erkannte Connectivity-Entität ist verschwunden
- ein weiterhin als `on` angezeigter Connectivity-Zustand wurde länger als
  drei Minuten nicht mehr gemeldet

Während Offline:

- keine normalen Stellbefehle
- kein Failsafe-Stellbefehl
- keine erneute Übernahme gecachter Noah-MQTT-Quellwerte in Coordinator und
  PV-Learning
- persistente Benachrichtigung **NOAH Optimizer: NOAH offline**
- Daten-/Controllerstatus `actuator_unavailable`

Nach einem frischen Online-Status wird die Benachrichtigung entfernt. Danach
werden die aktuellen Quellwerte neu eingelesen und der normale Controller
fortgesetzt.

Falls noch nie ein Connectivity-Sensor gefunden wurde, arbeitet die Integration
aus Kompatibilitätsgründen mit dem bisherigen Verhalten weiter und schreibt
eine Warnung in das Home-Assistant-Protokoll.

## 14. Legacy-Sperre

Wenn:

```text
input_boolean.noah_optimizer_enabled = on
```

werden konkurrierende HACS-Stellbefehle blockiert.

## 15. Historische Ladeplanansicht

Recorder-Daten:

- Ist-SOC
- dynamisches SOC-Soll
- Ziel-SOC

Gespeicherte Forecast-/Plan-Snapshots können zusätzlich überlagert werden.

Die Historie ist diagnostisch.

## 16. Dashboard

Das Dashboard enthält unter anderem:

- Energiefluss
- historische SOC-Karte
- PV-Prognose
- Energieplanung
- Leistung heute
- Reglerverhalten
- Planungsdetails
- PV-Learning
- Kalibrierung
- Diagnose

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

### Ergänzung in 2.1.0-beta.9

Die Template-Version steigt von `18` auf `19`, damit die Korrektur auch auf
Installationen ausgeführt wird, die Beta 8 bereits erfolgreich auf Version 18
gespeichert haben.

Für **Reglerverhalten** gelten fünf Kernserien als Standardchart:

```text
Regler-Soll
Ist-Ausgang
Eigenverbrauch-Soll
Ladepriorität-Soll
Nötige Ladeleistung
```

Die sechste Serie **Dynamische Nachladeleistung** ist optional. Damit werden
sowohl ältere gespeicherte 5-Serien-Charts als auch die aktuelle
6-Serien-Variante korrekt migriert.

## 17. Dashboard-Migrationshistorie

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
19  Reglerverhalten: 5-/6-Serien-Migration
```

Beta 10 benötigt keine neue Dashboard-Template-Version.

## 18. Sicherheit

Vor aktiver Steuerung prüfen:

- Quellwerte
- Netzvorzeichen
- Forecast
- Stellgröße
- berechneten Ausgangssollwert
- dynamisches SOC-Soll
- Freigabegrenze
- Controllerstatus
- Noah-MQTT Connectivity

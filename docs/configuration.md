# Konfiguration

Dieses Dokument beschreibt die HACS-Integration **Growatt NOAH Optimizer**
für den stabilen Release `2.0.0` und den aktuellen Pre-Release
`2.1.0-beta.8`.

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

Regeln:

- maximal sieben gültige Tage
- Median
- mindestens drei gültige Tage vor Anwendung
- Ausreißerbegrenzung
- große Messlücken können einen Tag ungültig machen

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

### Nutzbare Akkukapazität

Nutzbare Gesamtkapazität der angeschlossenen NOAH-Speicher.

### Ziel-SOC

Gewünschter SOC am Tagesende.

### Mindest-SOC

Untergrenze und Startpunkt des Tagesplans.

### Ladewirkungsgrad

Umrechnung von PV-Energie in speicherbare Batterieenergie.

### Prognose-Sicherheitsfaktor

Beispiel:

```text
Restprognose  5,0 kWh
Faktor        0,80
wirksam       4,0 kWh
```

### Zusätzliche Energiereserve

Sicherheitsreserve.

### Erwartete mittlere Hauslast

Verwendung in Prognosemarge und Energieplanung.

### Gewünschter Rest-Netzbezug

Kleiner positiver Zielbezug.

### Maximale Ausgangsleistung

Obergrenze der Stellgröße.

### Maximale Ausgangsleistung nachts

Separate Nachtgrenze.

### Manuelle Ausgangsleistung

Sollwert im Modus Manuell.

### Stellgrößenraster

Diskrete Schrittweite.

### Schalt-Hysterese

Verhindert unnötige Stellbefehle.

### SOC-Nachholzeit

Zeitfenster für das Aufholen eines SOC-Rückstands.

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

## 11. Befehlsintervalle

Normal:

```text
120 s
```

SOC-Freigabe / PV-Umlenkung:

```text
15 s Auswertung
30 s Mindestabstand für erforderliche Erhöhungen
```

Sicherheitsrelevante Reduzierungen können schneller erfolgen.

## 12. Failsafe

Fehlen kritische Daten länger:

- persistente Warnung
- wenn möglich 0 W
- Rücksetzen nach Datenrückkehr

## 13. Legacy-Sperre

Wenn:

```text
input_boolean.noah_optimizer_enabled = on
```

werden konkurrierende HACS-Stellbefehle blockiert.

## 14. Historische Ladeplanansicht

Recorder-Daten:

- Ist-SOC
- dynamisches SOC-Soll
- Ziel-SOC

Gespeicherte Forecast-/Plan-Snapshots können zusätzlich überlagert werden.

Die Historie ist diagnostisch.

## 15. Dashboard

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


## 16. Dashboard-Migrationshistorie

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
```

## 17. Sicherheit

Vor aktiver Steuerung prüfen:

- Quellwerte
- Netzvorzeichen
- Forecast
- Stellgröße
- berechneten Ausgangssollwert
- dynamisches SOC-Soll
- Freigabegrenze
- Controllerstatus

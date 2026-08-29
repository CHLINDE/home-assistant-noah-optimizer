# Konfiguration

## 1. Grundprinzip

Der Optimizer liest vorhandene Home-Assistant-Entitäten, normalisiert Einheiten,
berechnet einen Sollwert und kann diesen optional an eine beschreibbare
`number`-Entität des NOAH übertragen.

Berechnung und aktive Steuerung sind getrennt schaltbar.

## 2. Quellwerte

Erforderlich:

- Netzleistung
- PV-Leistung
- NOAH-Ausgang
- SOC
- Ladeleistung
- Entladeleistung
- Restprognose
- System Output Power

Netzkonvention:

```text
positiv = Netzbezug
negativ = Einspeisung
```

## 3. Betriebsarten

```text
Automatik
Eigenverbrauch
Ladepriorität
Manuell
```

### Automatik

Automatik berücksichtigt unter anderem:

- Mindest-SOC
- Ziel-SOC
- Forecast
- dynamischen SOC-Ladeplan
- SOC-Rückstand
- PV-Umlenkung
- SOC-Freigabe
- Nachtbetrieb

### Eigenverbrauch

Versucht den Netzbezug auf den konfigurierten Restbezug zu reduzieren.

### Ladepriorität

Reserviert PV-Leistung für notwendige Akkuladung.

### Manuell

Verwendet den konfigurierten manuellen Ausgangssollwert.

## 4. Schalter und Bedienung

### Optimierer-Berechnung aktiv

Aktiviert/deaktiviert die Berechnung.

### NOAH-Steuerung aktiv

Erlaubt das Schreiben des Ausgangssollwerts.

### Dynamische SOC-Steuerung aktiv

Erlaubt SOC-Nachladung und die dynamischen Automatikpfade.

### Vorausschauende SOC-Freigabe aktiv

Erlaubt kontrollierte Nutzung eines sicheren SOC-Vorsprungs.

### Gelernte PV-Korrektur verwenden

Wendet den PV-Lernfaktor auf den Prognosefaktor an. Standard: Aus.

### PV-Lerndaten zurücksetzen

Löscht die persistente Lernhistorie.

## 5. Wichtige Parameter

### Nutzbare Akkukapazität

Gesamte nutzbare Kapazität der angeschlossenen NOAH-Speicher.

### Ziel-SOC bei Sonnenuntergang

Gewünschter Tagesziel-SOC.

### Mindest-SOC

Untergrenze für reguläre Entladung.

### Ladewirkungsgrad

Faktor zur Umrechnung von PV-Energie in speicherbare Batterieenergie.

### Prognose-Sicherheitsfaktor

Beispiel:

```text
Restprognose: 5,0 kWh
Faktor:        0,80
wirksam:       4,0 kWh
```

### Zusätzliche Energiereserve

Wird bei der Planung als Sicherheitsreserve berücksichtigt.

### Erwartete mittlere Hauslast

Dient Prognosemarge und verbleibendem Hausenergiebedarf.

### Gewünschter Rest-Netzbezug

Kleiner positiver Zielbezug zur Vermeidung unnötiger Einspeisung durch
Mess-/Regelverzögerung.

### Maximale Ausgangsleistung

Obergrenze der aktiven Regelung.

### Maximale Ausgangsleistung nachts

Separate Nachtgrenze.

### Manuelle Ausgangsleistung

Sollwert für Betriebsart Manuell.

### Stellgrößenraster

Ausgangssollwerte werden auf dieses Raster gebracht.

### Schalt-Hysterese

Verhindert unnötige Stellbefehle bei kleinen Abweichungen.

### SOC-Nachholzeit

Legt fest, über welchen Zeitraum ein SOC-Rückstand aufgeholt werden soll.

## 6. Dynamischer SOC-Ladeplan

### Native Forecast.Solar-Kurve

Wenn die Restprognose direkt Forecast.Solar zugeordnet werden kann, verwendet
der Optimizer die bereits in Home Assistant vorhandene zeitaufgelöste Kurve.

Wirksame Forecast-Leistung:

```text
Forecast-Leistung
× Prognose-Sicherheitsfaktor
× optionaler PV-Lernfaktor
```

Die Kurve wird über den Tagesverlauf integriert.

Die erwartete Hauslast wird nicht aus jedem Forecast-Intervall abgezogen. Sie
bleibt separat in Prognosemarge und Ausgangsregelung berücksichtigt.

### Tageslicht-Fallback

Wenn keine native Forecast-Kurve verfügbar ist, wird der ältere Tageslichtpfad
verwendet.

### SOC-Abweichung

```text
SOC-Abweichung = Ist-SOC - dynamisches SOC-Soll
```

Typische Zustände:

```text
ahead
on_track
behind
night
```

Mehr als zwei Prozentpunkte Rückstand können SOC-Nachladung auslösen.

## 7. SOC-Ladeplan halten

Wenn der dynamische Plan erfüllt ist:

```text
SOC-Halten-Soll
= min(PV-Leistung, Eigenverbrauchs-Soll)
```

Abrundung auf das Stellgrößenraster verhindert absichtliche Batterieentladung.

## 8. PV-Umlenkung

Voraussetzungen:

- Automatik
- dynamischer SOC mindestens erfüllt
- Akkuladung > 0
- Netzbezug > 0

Berechnung:

```text
Umlenkung = min(Netzbezug, Akkuladeleistung)
```

Die Funktion reduziert zunächst nur Akkuladung zugunsten des Hausverbrauchs.

## 9. Vorausschauende SOC-Freigabe

Wiederauflade-Reserve:

```text
PV-Energie für Wiederaufladung
= wirksame Restprognose - Energiereserve
```

Der erwartete spätere Hausverbrauch wird für diese separate Reserve nicht
abgezogen.

Freigabegrenze:

```text
max(dynamisches SOC-Soll, prognosebasierter Mindest-SOC)
+ Sicherheitsreserve
```

Freigabe erfolgt nur bei positivem Netzbezug und nicht nachts.

## 10. PV-Learning

Tagesverhältnis:

```text
gemessene PV-Energie / Prognosereferenz
```

Regeln:

- maximal 7 gültige Tage
- Median statt Mittelwert
- Tagesfaktor begrenzt auf 0,50 ... 1,50
- mindestens 3 Tage vor Anwendung
- große Messlücken machen den Tag ungültig
- Learning arbeitet auch bei ausgeschalteter Anwendung passiv weiter

## 11. Historische Ladeplanansicht

Die Karte zeigt Recorder-Daten für:

- Ist-SOC
- dynamisches Soll
- Ziel-SOC

Zusätzlich können gespeicherte Forecast-/Plan-Snapshots überlagert werden.

Snapshot-Retention:

```text
31 Tage
max. 48 unterschiedliche Planstände pro Tag
```

## 12. Dashboardfarben

Stabile Palette:

```text
Blau     #2196F3
Grün     #009B21
Orange   #FF6A00
Gelb     #FFD800
Cyan     #00FFFF
Violett  #B200FF
```

### Historische SOC-Karte

```text
Ist-SOC             Blau
Dynamisches Soll    Grün
Ziel-SOC            Orange
Gespeicherter Plan  Gelb
```

### Reglerverhalten

```text
Regler-Soll                  Blau
Ist-Ausgang                  Grün
Eigenverbrauch-Soll          Orange
Ladepriorität-Soll           Gelb
Nötige Ladeleistung          Cyan
Dynamische Nachladeleistung  Violett
```

## 13. Dashboard-Migration Version 18

Version 18 behebt eine Lücke der vorherigen Farbmigration.

Früher wurden Serien mit bereits gesetztem `color`-Feld grundsätzlich
übersprungen. Deshalb konnten alte Farben in gespeicherten Dashboards bleiben.

Version 18 überschreibt einen alten expliziten Farbwert nur dann, wenn das
Diagramm als NOAH-Standarddiagramm erkannt wird.

Erkennungsmerkmale:

- bekannter Standardtitel
- vollständige erwartete Entity-Kombination
- bei PV-Prognose zusätzlich bekannte Data-Generatoren

Nicht erkannte oder eigene ApexCharts bleiben unverändert.

## 14. Controllerstatus

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

Der separate Enum-Sensor liefert zentrale Übersetzungen.

## 15. Command-Cadence

Normaler Regelbetrieb:

```text
120 s Mindestabstand
```

Load-Following bei SOC-Freigabe/PV-Umlenkung:

```text
15 s Auswertung
30 s für erforderliche Erhöhungen
```

Sicherheitsrelevante Reduzierungen dürfen schneller erfolgen.

## 16. Failsafe

Bei länger fehlenden kritischen Messdaten:

- Controllerstatus wechselt auf Failsafe
- wenn möglich wird 0 W angefordert
- persistente Home-Assistant-Warnung wird erzeugt

## 17. Legacy-Sperre

Wenn:

```text
input_boolean.noah_optimizer_enabled = on
```

werden HACS-Stellbefehle blockiert.

## 18. Diagnose

Für Fehlersuche besonders relevant:

- Datenstatus
- Controllerstatus
- Reglermodus
- Ausgangssollwert
- letzter Stellwert
- dynamisches SOC-Soll
- SOC-Abweichung
- Ladeplanbasis
- Forecast-Aktualisierungszeit
- PV-Learning bereit
- PV-Lernfaktor

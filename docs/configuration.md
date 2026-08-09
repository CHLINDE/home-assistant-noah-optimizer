# Konfiguration

Dieses Dokument beschreibt die HACS-Integration **Growatt NOAH Optimizer** ab
Version `2.0.0-beta.8`.

Die tatsächlichen Entity-IDs können durch Bereichsnamen oder manuelle
Umbenennungen abweichen. Die Integration und das automatische Dashboard lösen
die eigenen Entitäten über stabile Unique IDs auf.

## 1. Schalter

### Optimierer-Berechnung aktiv

Aktiviert die Berechnung des Ausgangssollwerts.

Ist dieser Schalter aus, wird der Reglermodus auf `off` gesetzt und es werden
keine normalen Stellbefehle ausgeführt.

### NOAH-Steuerung aktiv

Gibt das aktive Schreiben auf die konfigurierte `NOAH System Output Power`-
Entität frei.

Standard:

```text
Aus
```

Berechnung und aktive Stellregelung sind absichtlich getrennt.

### Dynamische SOC-Steuerung aktiv

Neu in Beta 8.

Die dynamische SOC-Berechnung läuft unabhängig von diesem Schalter, sodass die
neuen Sensoren zunächst beobachtet werden können.

Erst bei:

```text
Dynamische SOC-Steuerung aktiv = Ein
Betriebsart = Automatik
```

kann ein SOC-Rückstand den Ausgangssollwert beeinflussen.

Standard:

```text
Aus
```

Die Betriebsarten **Manuell**, **Eigenverbrauch** und **Ladepriorität** werden
durch diesen Schalter nicht verändert.

## 2. Betriebsarten

Der Select **Betriebsart** bietet:

```text
Automatik
Eigenverbrauch
Ladepriorität
Manuell
```

### Automatik

Der Optimizer wählt seinen internen Reglermodus abhängig von:

- SOC
- Mindest-SOC
- Ziel-SOC
- PV-Restprognose
- erwarteter Hauslast
- Netzbezug beziehungsweise Einspeisung
- verbleibender Zeit bis Sonnenuntergang
- optional dem dynamischen SOC-Ladeplan

Mögliche interne Reglermodi sind:

```text
Aus
Manuell
Eigenverbrauch
Ladepriorität
SOC-Nachladung
Mindest-SOC
Nachtbetrieb
Ziel-SOC erreicht
Konservativ ohne Prognose
Gleitende Reserve
```

### Eigenverbrauch

Die Ausgangsleistung wird so berechnet, dass der Netzbezug möglichst klein
bleibt und der gewünschte Rest-Netzbezug berücksichtigt wird.

### Ladepriorität

Ein Teil der verfügbaren PV-Leistung wird für das Erreichen des Ziel-SOC
reserviert. Die Ausgangsleistung wird entsprechend begrenzt.

### Manuell

Der Parameter **Manuelle Ausgangsleistung** wird als Sollwert verwendet.

## 3. Dynamischer SOC-Ladeplan

Beta 8 berechnet, welchen SOC der Speicher **jetzt mindestens haben sollte**,
damit der Ziel-SOC bis Sonnenuntergang mit der konservativ noch erwarteten
PV-Energie erreichbar bleibt.

### 3.1 Verfügbare PV-Energie für den Akku

```text
PV-Energie für Akku
= wirksame Restprognose
  - erwarteter Hausenergiebedarf
  - zusätzliche Energiereserve
```

Negative Ergebnisse werden auf `0 kWh` begrenzt.

### 3.2 Möglicher SOC-Zuwachs

```text
Speicherbare Energie
= PV-Energie für Akku × Ladewirkungsgrad

Möglicher SOC-Zuwachs
= Speicherbare Energie / nutzbare Akkukapazität × 100
```

### 3.3 Dynamisches SOC-Soll

```text
Dynamisches SOC-Soll
= Ziel-SOC - möglicher SOC-Zuwachs
```

Der Wert wird begrenzt auf:

```text
Mindest-SOC <= dynamisches SOC-Soll <= Ziel-SOC
```

Je mehr nutzbare PV-Energie noch erwartet wird, desto niedriger darf der Akku
aktuell stehen. Nimmt die Restprognose im Tagesverlauf ab, steigt das
dynamische SOC-Soll automatisch Richtung Ziel-SOC.

### 3.4 SOC-Abweichung

```text
SOC-Abweichung
= Ist-SOC - dynamisches SOC-Soll
```

Beta 8 verwendet eine feste Toleranz von 2 Prozentpunkten:

```text
mehr als +2 %-Punkte  = Vor Ladeplan
-2 bis +2 %-Punkte    = Im Ladeplan
weniger als -2 %-Punkte = Hinter Ladeplan
```

### 3.5 Dynamisch erforderliche Ladeleistung

Liegt der Speicher hinter dem Ladeplan, wird die zum Aufholen des Rückstands
benötigte Ladeleistung berechnet.

```text
Fehlende Batterieenergie
= Akkukapazität × SOC-Rückstand / 100

Benötigte PV-Energie
= fehlende Batterieenergie / Ladewirkungsgrad

Dynamische Ladeleistung
= benötigte PV-Energie / Nachholzeit
```

Die verwendete Nachholzeit ist auf die noch verbleibende Zeit bis
Sonnenuntergang begrenzt.

### 3.6 Einfluss auf die Regelung

Nur wenn alle folgenden Bedingungen erfüllt sind, wird der neue Reglermodus
**SOC-Nachladung** aktiv:

- Optimierer-Berechnung ist aktiv
- Betriebsart ist **Automatik**
- Dynamische SOC-Steuerung ist aktiv
- Forecast.Solar ist verfügbar
- es ist Tag
- SOC liegt über dem Mindest-SOC
- SOC liegt unter dem Ziel-SOC
- der Speicher liegt mehr als 2 Prozentpunkte hinter dem dynamischen SOC-Soll

Dann wird für die Batterieladung mindestens der größere Wert aus:

```text
bisher erforderliche mittlere Ladeleistung
oder
dynamisch erforderliche Ladeleistung
```

reserviert.

Der NOAH-Ausgang wird entsprechend reduziert, ohne negative Ausgangsleistung
anzufordern.

## 4. Parameter

### Nutzbare Akkukapazität

Standard:

```text
2,048 kWh
```

Gesamte nutzbare Kapazität der angeschlossenen NOAH-Speicher.

### Ziel-SOC bei Sonnenuntergang

Standard:

```text
95 %
```

### Mindest-SOC

Standard:

```text
10 %
```

### Angenommener Ladewirkungsgrad

Standard:

```text
0,90
```

### Prognose-Sicherheitsfaktor

Standard:

```text
0,80
```

Beispiel:

```text
Restprognose: 5,0 kWh
Faktor:        0,80
wirksam:       4,0 kWh
```

### Zusätzliche Energiereserve

Standard:

```text
0,25 kWh
```

### Freigabemarge

Standard:

```text
0,50 kWh
```

### Erwartete mittlere Hauslast

Standard:

```text
250 W
```

### Gewünschter Rest-Netzbezug

Standard:

```text
50 W
```

### Maximale Ausgangsleistung

Standard:

```text
800 W
```

### Maximale Ausgangsleistung nachts

Standard:

```text
400 W
```

### Manuelle Ausgangsleistung

Standard:

```text
200 W
```

### Stellgrößenraster

Standard:

```text
50 W
```

### Schalt-Hysterese

Standard:

```text
50 W
```

### SOC-Nachholzeit

Neu in Beta 8.

Standard:

```text
2,0 h
```

Bereich:

```text
0,5 ... 6,0 h
```

Ein kleinerer Wert reagiert aggressiver auf einen SOC-Rückstand. Ein größerer
Wert verteilt das Nachladen über einen längeren Zeitraum.

## 5. Wichtige berechnete Sensoren

### Netzleistung

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

### Netzbezug / Netzeinspeisung

Aus der saldierten Netzleistung abgeleitete positive Richtungswerte.

### Hauslast

Näherungsweise:

```text
Hauslast = Netzleistung + NOAH-Ausgangsleistung
```

### Batterieleistung

Kombinierter Batteriefluss. Positive Werte entsprechen Entladung, negative
Werte Ladung.

Für das Dashboard werden zusätzlich die getrennten Sensoren **Ladeleistung**
und **Entladeleistung** verwendet.

### Netzleistung 5 min

Zeitgewichteter gleitender Mittelwert der Netzleistung.

### Ladebedarf

Noch erforderliche Energie zum Ziel-SOC unter Berücksichtigung des
Ladewirkungsgrads.

### Wirksame Restprognose

Restprognose multipliziert mit dem Prognose-Sicherheitsfaktor.

### Erwarteter Hausenergiebedarf

Abschätzung aus verbleibender Zeit bis Sonnenuntergang und erwarteter mittlerer
Hauslast.

### Prognosemarge

Verbleibende Energiemarge nach Ladebedarf, erwartetem Hausenergiebedarf und
zusätzlicher Reserve.

### Prognosedeckung

Prozentuale Deckung des erwarteten Restbedarfs durch die wirksame Prognose.

### Dynamisches SOC-Soll

SOC, den der Speicher zum aktuellen Zeitpunkt mindestens haben sollte.

### SOC-Abweichung

Ist-SOC minus dynamisches SOC-Soll.

### SOC-Ladeplan

Enum-Sensor mit:

```text
ahead     = Vor Ladeplan
on_track  = Im Ladeplan
behind    = Hinter Ladeplan
```

### Dynamisch erforderliche Ladeleistung

Zusätzliche Ladeleistung zum Aufholen eines SOC-Rückstands innerhalb der
konfigurierten SOC-Nachholzeit.

### Ausgangssollwert

Endgültiger berechneter NOAH-Sollwert nach Betriebsart, Grenzwerten,
dynamischer SOC-Regelung und Stellgrößenraster.

## 6. Controllerdiagnose

Der Schalter **NOAH-Steuerung aktiv** stellt bereit:

```text
control_status
last_command_target
last_command_at
```

Typische `control_status`-Werte:

| Status | Bedeutung |
|---|---|
| `disabled` | Aktive Steuerung aus |
| `optimizer_disabled` | Berechnung aus |
| `legacy_controller_active` | Legacy-YAML-Regler blockiert HACS |
| `critical_data_missing` | Kritische Messwerte fehlen |
| `actuator_unavailable` | Stellgröße nicht erreichbar |
| `target_unavailable` | Kein gültiger Sollwert |
| `rate_limited` | Mindestabstand noch nicht erreicht |
| `waiting_for_retry` | Wartet auf Wiederholungsversuch |
| `in_sync` | Stellgröße liegt innerhalb der Hysterese |
| `command_sent` | Stellbefehl gesendet |
| `command_failed` | Stellbefehl fehlgeschlagen |
| `failsafe` | Failsafe aktiv |

## 7. Failsafe

Fehlen kritische Messwerte zehn Minuten ununterbrochen, während die aktive
Steuerung eingeschaltet ist:

1. Home Assistant erzeugt eine persistente Benachrichtigung.
2. Ist die Stellgröße erreichbar, versucht die Integration `0 W` zu setzen.
3. Ist sie nicht erreichbar, wird die Warnung trotzdem erzeugt.
4. Nach Wiederkehr der Daten werden Failsafe-Zustand und Benachrichtigung
   zurückgesetzt.

## 8. Legacy-Sperre

Existiert:

```text
input_boolean.noah_optimizer_enabled
```

und steht auf `on`, blockiert die HACS-Steuerung normale Ausgangsbefehle.

Legacy-YAML-Optimizer und HACS-Controller dürfen nicht gleichzeitig aktiv
denselben NOAH steuern.

## 9. Dashboard

Das automatische Dashboard verwendet für Power Flow Card Plus:

```text
Grid:
consumption = Netzbezug
production  = Netzeinspeisung

Battery:
consumption = Entladeleistung
production  = Ladeleistung
```

Damit entspricht die animierte Richtung dem realen Energiefluss.

Beta 8 ergänzt außerdem:

- Dynamische SOC-Steuerung aktiv
- Dynamisches SOC-Soll
- SOC-Abweichung
- SOC-Ladeplan
- Dynamisch erforderliche Ladeleistung
- SOC-Nachholzeit
- Diagramm mit Ist-SOC, dynamischem SOC-Soll und Ziel-SOC

Ein bestehendes Dashboard wird gezielt migriert und nicht vollständig durch
die Standardvorlage ersetzt.

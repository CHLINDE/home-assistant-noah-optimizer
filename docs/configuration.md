# Konfiguration

Dieses Dokument beschreibt die Parameter, Betriebsarten und Statuswerte der
HACS-Integration **Growatt NOAH Optimizer**.

Die tatsächlichen Entity-IDs können je nach Bereichszuordnung oder manueller
Umbenennung unterschiedlich sein. Deshalb werden hier vor allem die
angezeigten Entitätsnamen verwendet.

## 1. Schalter

### Optimierer-Berechnung aktiv

Aktiviert die Berechnung der Optimizer-Sollwerte.

Ist dieser Schalter aus, wird der Reglermodus auf den ausgeschalteten Zustand
gesetzt und die aktive Steuerung darf keine normalen Stellbefehle senden.

### NOAH-Steuerung aktiv

Gibt das aktive Schreiben auf die konfigurierte NOAH-System-Output-Power-
Entität frei.

Dieser Schalter ist standardmäßig aus.

Die beiden Schalter sind absichtlich getrennt. Dadurch kann die komplette
Berechnung geprüft werden, ohne den NOAH zu steuern.

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

Mögliche Reglermodi sind:

```text
Aus
Manuell
Eigenverbrauch
Ladepriorität
Mindest-SOC
Nachtbetrieb
Ziel-SOC erreicht
Konservativ ohne Prognose
Gleitende Reserve
```

### Eigenverbrauch

Die Ausgangsleistung wird so berechnet, dass der Netzbezug möglichst klein
bleibt und der eingestellte Rest-Netzbezug berücksichtigt wird.

### Ladepriorität

Ein Teil der verfügbaren PV-Leistung wird für das Erreichen des Ziel-SOC
reserviert. Die Ausgangsleistung wird entsprechend begrenzt.

### Manuell

Der Parameter **Manuelle Ausgangsleistung** wird als Sollwert verwendet.

## 3. Parameter

### Nutzbare Akkukapazität

Standard:

```text
2,048 kWh
```

Gesamte nutzbare Kapazität aller angeschlossenen NOAH-Module.

Beispiele:

```text
1 Modul: 2,048 kWh
2 Module: 4,096 kWh
3 Module: 6,144 kWh
```

### Ziel-SOC bei Sonnenuntergang

Standard:

```text
95 %
```

SOC, den die Ladeplanung bis Sonnenuntergang anstrebt.

### Mindest-SOC

Standard:

```text
10 %
```

Unterhalb beziehungsweise beim Erreichen dieses Werts wird in der Automatik
keine normale Entladung mehr angefordert.

### Angenommener Ladewirkungsgrad

Standard:

```text
0,90
```

Wirkungsgrad für die Berechnung der bis zum Ziel-SOC benötigten Ladeenergie.

### Prognose-Sicherheitsfaktor

Standard:

```text
0,80
```

Multipliziert die noch erwartete PV-Energie.

Beispiel:

```text
Restprognose: 5,0 kWh
Faktor:        0,80
wirksam:       4,0 kWh
```

Ein höherer Wert vertraut stärker auf die Forecast.Solar-Prognose.

### Zusätzliche Energiereserve

Standard:

```text
0,25 kWh
```

Zusätzliche Sicherheitsreserve in der Energieplanung.

### Freigabemarge

Standard:

```text
0,50 kWh
```

Positive Prognosemarge, ab der die Automatik vollständig in Richtung
Eigenverbrauch freigeben kann.

### Erwartete mittlere Hauslast

Standard:

```text
250 W
```

Wird verwendet, um aus der verbleibenden Zeit bis Sonnenuntergang einen
erwarteten Energiebedarf des Hauses abzuschätzen.

### Gewünschter Rest-Netzbezug

Standard:

```text
50 W
```

Kleine positive Netzreserve, die unnötiges Pendeln zwischen Bezug und
Einspeisung reduzieren soll.

### Maximale Ausgangsleistung

Standard:

```text
800 W
```

Obergrenze für den berechneten Ausgangssollwert.

### Maximale Ausgangsleistung nachts

Standard:

```text
400 W
```

Separate Obergrenze für den Nachtbetrieb.

### Manuelle Ausgangsleistung

Standard:

```text
200 W
```

Sollwert in der Betriebsart **Manuell**.

### Stellgrößenraster

Standard:

```text
50 W
```

Der endgültige Sollwert wird auf dieses Raster gerundet.

### Schalt-Hysterese

Standard:

```text
50 W
```

Erst eine ausreichend große Differenz zwischen Soll- und Referenzwert löst
einen normalen neuen Stellbefehl aus.

## 4. Wichtige berechnete Sensoren

### Netzleistung

Vorzeichenkonvention:

```text
positiv = Netzbezug
negativ = Einspeisung
```

### Netzbezug / Netzeinspeisung

Aus der saldierten Netzleistung abgeleitete, getrennte positive Sensoren.

### Hauslast

Aus Netzleistung und NOAH-Ausgangsleistung berechnete aktuelle Hauslast.

### Batterieleistung

Kombinierter Batteriefluss. Für das Dashboard werden zusätzlich die getrennten
Sensoren **Ladeleistung** und **Entladeleistung** verwendet.

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

Verbleibende Energiemarge nach Ladebedarf, erwarteter Hausenergie und Reserve.

### Prognosedeckung

Prozentuale Deckung des erwarteten Restbedarfs durch die wirksame Prognose.

### Erforderliche mittlere Ladeleistung

Mittlere Ladeleistung, die bis Sonnenuntergang noch benötigt wird, um den
Ziel-SOC zu erreichen.

### Ausgangssollwert

Endgültiger berechneter NOAH-Sollwert nach Betriebsart, Grenzwerten,
Hysterese-Vorbereitung und Stellgrößenraster.

## 5. Controllerdiagnose

Der Schalter **NOAH-Steuerung aktiv** stellt Attribute bereit:

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

## 6. Failsafe

Fehlen kritische Messwerte zehn Minuten ununterbrochen, während die aktive
Steuerung eingeschaltet ist:

1. Home Assistant erzeugt eine persistente Benachrichtigung.
2. Ist die Stellgröße erreichbar, versucht die Integration `0 W` zu setzen.
3. Ist sie nicht erreichbar, bleibt die Warnung trotzdem bestehen.
4. Nach Wiederkehr der Daten werden Failsafe-Zustand und Benachrichtigung
   zurückgesetzt.

## 7. Legacy-Sperre

Existiert:

```text
input_boolean.noah_optimizer_enabled
```

und steht auf `on`, blockiert die HACS-Steuerung normale Ausgangsbefehle.

Legacy-YAML-Optimizer und HACS-Controller dürfen nicht gleichzeitig aktiv
denselben NOAH steuern.

## 8. Dashboard-Konfiguration

Beta 6 erzeugt beim ersten Start ein eigenes Dashboard.

Die Standardvorlage wird nur verwendet, wenn noch keine gespeicherte
NOAH-Dashboard-Konfiguration existiert.

Benutzeränderungen werden deshalb bei Neustarts oder Integration-Reloads
nicht überschrieben.

Die Standardvorlage wird bei der ersten Erzeugung nach der
Home-Assistant-Sprache gewählt:

```text
Deutsch -> dashboard_de.yaml
sonst   -> dashboard_en.yaml
```

Für Power Flow Card Plus werden Netz und Batterie mit getrennten Richtungen
dargestellt:

```text
Grid:
consumption = Netzbezug
production  = Netzeinspeisung

Battery:
consumption = Entladeleistung
production  = Ladeleistung
```

## 9. Legacy-YAML

Die ältere Package-Variante verwendet weiterhin `input_*`-Helfer und
`sensor.noah_opt_*`-Entitäten.

Für neue Installationen wird die HACS-Integration empfohlen. Details zur
Legacy-Installation stehen in `installation.md`.

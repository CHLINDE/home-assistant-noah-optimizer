# Konfiguration

Dieses Dokument beschreibt die Parameter, Betriebsarten und Berechnungen des NOAH Optimizers.

## 1. Betriebsarten

Der Helfer `input_select.noah_optimizer_mode` bietet vier Betriebsarten.

### Automatik

Die Ausgangsleistung wird anhand von:

- SOC
- Mindest-SOC
- Ziel-SOC
- PV-Restprognose
- erwarteter Hauslast
- Netzbezug beziehungsweise Einspeisung
- Tageszeit und Sonnenstand

automatisch berechnet.

Mögliche interne Reglermodi sind:

- `Aus`
- `Mindest-SOC`
- `Nachtbetrieb`
- `Ziel-SOC erreicht`
- `Konservativ ohne Prognose`
- `Ladepriorität`
- `Eigenverbrauch`
- `Gleitende Reserve`

### Eigenverbrauch

Der Regler versucht, die NOAH-Ausgangsleistung an die aktuelle Hauslast anzupassen und einen kleinen Rest-Netzbezug einzuhalten.

### Ladepriorität

Der Regler reserviert einen Teil der PV-Leistung für die Akkuladung. Nur der darüber liegende Anteil darf als Ausgangsleistung verwendet werden.

### Manuell

Die Ausgangsleistung wird aus `input_number.noah_manual_output_w` übernommen.

Diese Betriebsart ist für die Inbetriebnahme und Fehlerdiagnose vorgesehen.

## 2. Konfigurationsparameter

### Nutzbare Akkukapazität

```text
input_number.noah_battery_capacity_kwh
```

Gesamte nutzbare Kapazität aller verbundenen NOAH-Module.

Beispiele:

```text
1 Modul: 2,048 kWh
2 Module: 4,096 kWh
3 Module: 6,144 kWh
```

### Ziel-SOC bei Sonnenuntergang

```text
input_number.noah_target_soc
```

SOC, den die Ladeplanung bis zum Abend anstrebt.

Empfehlung:

```text
95 %
```

95 % lassen eine kleine Aufnahmereserve. Für maximale Nachtenergie kann 100 % gewählt werden.

### Mindest-SOC

```text
input_number.noah_min_soc
```

Unterhalb oder bei Erreichen dieses Werts setzt die Automatik den Sollwert auf 0 W.

Der Wert sollte zur Entladeuntergrenze der Growatt-Konfiguration passen.

Empfehlung:

```text
10 %
```

### Angenommener Ladewirkungsgrad

```text
input_number.noah_charge_efficiency
```

Wirkungsgrad für die Berechnung der bis zum Ziel-SOC benötigten Ladeenergie.

Empfehlung:

```text
0,90
```

### Prognose-Sicherheitsfaktor

```text
input_number.noah_forecast_factor
```

Reduziert oder erhöht die Forecast.Solar-Restprognose für die interne Planung.

Berechnung:

```text
wirksame Restprognose =
Restprognose × Prognose-Sicherheitsfaktor
```

Interpretation:

| Wert | Verhalten |
|---:|---|
| 0,60–0,75 | konservativ, mehr Ladepriorität |
| 0,80 | empfohlener Startwert |
| 0,90–1,00 | optimistischer, mehr Eigenverbrauch |
| über 1,00 | nur bei systematisch zu niedriger Prognose |

### Zusätzliche Energiereserve

```text
input_number.noah_forecast_safety_kwh
```

Zusätzliche Energiemenge, die bei der Planung als Reserve abgezogen wird.

Empfehlung:

```text
0,25 kWh
```

Ein höherer Wert priorisiert die Akkuladung stärker.

### Freigabemarge

```text
input_number.noah_release_margin_kwh
```

Grenze, ab der vollständig auf Eigenverbrauchsregelung umgeschaltet wird.

- Prognosemarge kleiner oder gleich 0: Ladepriorität
- Prognosemarge größer oder gleich Freigabemarge: Eigenverbrauch
- dazwischen: gleitende Mischung

Empfehlung:

```text
0,50 kWh
```

### Erwartete mittlere Hauslast

```text
input_number.noah_expected_day_load_w
```

Durchschnittlich erwartete Hauslast bis Sonnenuntergang.

Berechnung:

```text
erwarteter Hausenergiebedarf =
Stunden bis Sonnenuntergang × erwartete Hauslast
```

Empfehlung zum Start:

```text
250 W
```

Dieser Wert sollte anhand des realen Grundverbrauchs angepasst werden.

### Gewünschter Rest-Netzbezug

```text
input_number.noah_grid_reserve_w
```

Bewusster kleiner Netzbezug zur Vermeidung von Einspeisung bei schwankender Hauslast.

Empfehlung:

```text
50 W
```

Höhere Werte reduzieren Einspeisung, erhöhen aber den Netzbezug.

### Maximale Ausgangsleistung

```text
input_number.noah_max_output_w
```

Obere Begrenzung des berechneten Sollwerts.

Typischer Wert:

```text
800 W
```

Der Wert muss zur zulässigen Ausgangsleistung des Systems passen.

### Maximale Ausgangsleistung nachts

```text
input_number.noah_night_max_output_w
```

Begrenzt die Entladeleistung im Nachtbetrieb.

Beispiele:

| Wert | Wirkung |
|---:|---|
| 300–400 W | Akku hält länger, höherer Netzbezug |
| 500–600 W | mittlerer Kompromiss |
| 800 W | geringerer Netzbezug, Akku schneller leer |

### Manuelle Ausgangsleistung

```text
input_number.noah_manual_output_w
```

Wird ausschließlich in der Betriebsart `Manuell` verwendet.

### Stellgrößenraster

```text
input_number.noah_command_step_w
```

Rundet den Sollwert auf feste Leistungsstufen.

Beispiele:

```text
50 W = robuste, grobe Regelung
20 W = feinere Regelung
```

Ein kleineres Raster kann die Einspeisung reduzieren, führt aber zu häufigeren Sollwertänderungen.

### Schalt-Hysterese

```text
input_number.noah_command_deadband_w
```

Ein neuer Stellbefehl wird nur gesendet, wenn die Abweichung mindestens diesem Wert entspricht.

Empfehlung:

```text
50 W
```

Bei feinerem Raster kann beispielsweise 30–40 W verwendet werden.

## 3. Berechnete Messwerte

### Netzbezug und Einspeisung

Aus der saldierten Netzleistung werden getrennte Sensoren erzeugt:

```text
sensor.noah_opt_netzbezug
sensor.noah_opt_netzeinspeisung
```

Dabei gilt:

```text
Netzleistung > 0  → Netzbezug
Netzleistung < 0  → Einspeisung
```

### Hauslast

```text
Hauslast =
Netzleistung + NOAH-Ausgangsleistung
```

Sensor:

```text
sensor.noah_opt_hauslast
```

### Batterieleistung

```text
Batterieleistung =
Entladeleistung − Ladeleistung
```

Positiv bedeutet netto Entladung, negativ bedeutet netto Ladung.

### Verfügbare Akkuenergie

```text
Kapazität × (SOC − Mindest-SOC) / 100
```

### Ladebedarf

```text
Kapazität × (Ziel-SOC − SOC) / 100 / Ladewirkungsgrad
```

Negative Ergebnisse werden auf 0 begrenzt.

### Prognosemarge

```text
wirksame Restprognose
− Ladebedarf
− erwarteter Hausenergiebedarf
− zusätzliche Reserve
```

Interpretation:

| Prognosemarge | Bedeutung |
|---:|---|
| kleiner 0 kWh | Prognose reicht laut Modell nicht für alle Ziele |
| um 0 kWh | knappe Deckung |
| größer 0 kWh | rechnerischer Überschuss |
| über Freigabemarge | vollständige Eigenverbrauchsfreigabe |

### Prognosedeckung

```text
wirksame Restprognose
÷ (Ladebedarf + Hausenergiebedarf + Reserve)
× 100 %
```

Die Prognosedeckung ist keine Wahrscheinlichkeit. Sie zeigt, welcher Anteil des geplanten verbleibenden Energiebedarfs durch die wirksame PV-Restprognose gedeckt werden kann.

### Erforderliche mittlere Ladeleistung

```text
Ladebedarf × 1000 / Stunden bis Sonnenuntergang
```

Dieser Wert wird bei der Ladeprioritätsberechnung von der verfügbaren PV-Leistung reserviert.

## 4. Eigenverbrauchsregelung

Der Eigenverbrauchs-Sollwert basiert auf:

```text
aktuelle NOAH-Ausgangsleistung
+ gemittelte Netzleistung
− gewünschter Rest-Netzbezug
```

Der Wert wird auf 0 W bis zur maximalen Ausgangsleistung begrenzt.

Der Netzleistungssensor wird über fünf Minuten geglättet. Dadurch reagiert der Regler nicht auf jede kurze Lastspitze, kann aber bei schnellen Lastwechseln kurzfristige Einspeisung oder Netzbezug nicht vollständig verhindern.

## 5. Ladeprioritätsregelung

Vereinfacht:

```text
Ladeprioritäts-Soll =
PV-Leistung − erforderliche mittlere Ladeleistung
```

Der Wert wird zusätzlich durch das Eigenverbrauchs-Soll begrenzt.

Dadurch wird ein Teil der aktuellen Solarleistung für die Akkuladung reserviert.

## 6. Nachtbetrieb

Der Nachtbetrieb wird aktiviert, wenn:

```text
sun.sun = below_horizon
```

oder wenn gleichzeitig gilt:

```text
Sonnenhöhe < 3°
PV-Leistung < 20 W
```

Dadurch beginnt die Akkuentladung bereits in der Abenddämmerung und nicht erst exakt nach dem astronomischen Sonnenuntergang.

Im Nachtbetrieb gilt:

```text
Sollwert =
Minimum aus Eigenverbrauchs-Soll und Nachtmaximum
```

## 7. Verhalten bei Ziel- und Mindest-SOC

### Mindest-SOC erreicht

```text
SOC <= Mindest-SOC
```

Ergebnis:

```text
Ausgangssollwert = 0 W
Reglermodus = Mindest-SOC
```

### Ziel-SOC erreicht

```text
SOC >= Ziel-SOC
```

Der Regler wechselt zur Eigenverbrauchsregelung. Der Akku kann durch vorhandenen Überschuss trotzdem weiter bis 100 % geladen werden.

## 8. Fehlende Prognose

Wenn Forecast.Solar nicht verfügbar ist, schaltet die Automatik auf:

```text
Konservativ ohne Prognose
```

und verwendet die Ladeprioritätsberechnung.

## 9. Ausfallsicherung

Fehlen kritische Messwerte mindestens zehn Minuten, versucht die Automatisierung:

```text
System Output Power = 0 W
```

Zusätzlich wird eine dauerhafte Home-Assistant-Benachrichtigung erzeugt.

Kritische Messwerte sind:

- Netzleistung
- PV-Leistung
- NOAH-Ausgangsleistung
- SOC

Die Ausfallsicherung kann nur wirken, wenn die Stellgrößen-Entität selbst noch erreichbar ist.

## 10. Empfohlene Abstimmung

### Akku wird zu früh voll

- Prognosefaktor erhöhen
- Reserve verringern
- Freigabemarge verringern
- erwartete Hauslast verringern
- Ziel-SOC auf 95 % setzen

### Akku wird abends nicht voll genug

- Ziel-SOC auf 100 % setzen
- Prognosefaktor verringern
- Reserve erhöhen
- Freigabemarge erhöhen
- erwartete Hauslast erhöhen

### Zu viel Einspeisung

- Rest-Netzbezug erhöhen
- Stellgrößenraster verkleinern
- Schalt-Hysterese moderat verringern
- Lastwechsel und Verzögerungen in den Diagrammen prüfen

### Zu viel Netzbezug

- Rest-Netzbezug verringern
- maximale Ausgangsleistung prüfen
- Nachtmaximum erhöhen
- Prognosefaktor nur erhöhen, wenn die Prognose systematisch zu vorsichtig ist

## 11. Remanenz der Helfer

Die meisten einstellbaren Helfer besitzen in der veröffentlichten Datei keinen festen `initial:`-Wert. Home Assistant kann dadurch den zuletzt gespeicherten Zustand wiederherstellen.

`input_number.noah_last_target_w` besitzt bewusst einen Startwert von 0 W, da es sich um einen internen Statuswert handelt.

Nach Änderungen am Package sollten die konfigurierten Werte nach einem Neustart kontrolliert werden.

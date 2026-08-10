# Fehlerbehebung

Dieses Dokument bezieht sich primär auf die HACS-Integration ab
`2.0.0-beta.9`.

## 1. Integration wird nicht geladen

Unter **Einstellungen → System → Protokolle** nach:

```text
noah_optimizer
```

suchen.

Zusätzlich prüfen:

- HACS-Installation vollständig
- Home Assistant nach dem Update neu gestartet
- `manifest.json` auf `2.0.0-beta.9`
- alle Quell-Entitäten vorhanden
- keine Python-Fehler im Protokoll

## 2. Datenstatus ist nicht OK

Unter **Werkzeuge → Zustände** die ausgewählten Quell-Entitäten prüfen.

Kritisch sind insbesondere:

- saldierte Netzleistung
- NOAH Solar Power
- NOAH Output Power
- NOAH SOC

Die Zustände dürfen nicht dauerhaft:

```text
unknown
unavailable
```

sein.

## 3. „Stellgröße nicht verfügbar“

Die konfigurierte `NOAH System Output Power`-Entität muss:

- vorhanden sein
- verfügbar sein
- numerisch sein
- als `number` beschreibbar sein
- W oder kW verwenden

Unter **Werkzeuge → Aktionen** mit `number.set_value` testen.

Ein `sensor.*_output_power` ist nur ein Messwert und keine Stellgröße.

## 4. Netzbezug und Einspeisung sind vertauscht

Erwartet wird:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Bei umgekehrter Konvention die Integration mit **Netzvorzeichen umkehren**
einrichten.

## 5. Batteriefluss im Dashboard ist falsch herum

Für Power Flow Card Plus muss gelten:

```text
consumption = Entladeleistung
production  = Ladeleistung
```

Im HACS-Dashboard:

```yaml
battery:
  entity:
    consumption: __DISCHARGING_POWER__
    production: __CHARGING_POWER__
```

Das bedeutet:

```text
Ladeleistung    -> Energie fließt in den Akku
Entladeleistung -> Energie fließt aus dem Akku
```

Beta 8 korrigiert beim bestehenden Dashboard zusätzlich die exakte alte
Beta-6-Zuordnung, falls sie noch vorhanden ist.

## 6. Dynamisches SOC-Soll ist `unavailable`

Die dynamischen SOC-Werte benötigen eine verfügbare Forecast.Solar-
Restprognose.

Prüfen:

- `Restprognose heute` ist verfügbar
- Einheit ist `Wh` oder `kWh`
- Sun-Integration liefert `sun.sun`
- Ziel-SOC, Mindest-SOC und Akkukapazität sind plausibel

Fehlt die Prognose, greift die dynamische SOC-Steuerung nicht ein.

## 7. SOC-Ladeplan zeigt „Hinter Ladeplan“

Das bedeutet:

```text
Ist-SOC < dynamisches SOC-Soll - 2 Prozentpunkte
```

Das ist zunächst nur ein Diagnosewert.

Nur wenn zusätzlich:

```text
Dynamische SOC-Steuerung aktiv = Ein
Betriebsart = Automatik
```

ist, kann der Zustand den Ausgangssollwert beeinflussen.

## 8. Dynamische SOC-Steuerung ist an, aber nichts ändert sich

Das kann korrekt sein. Die Funktion greift nur ein, wenn gleichzeitig:

- Automatik aktiv ist
- Forecast verfügbar ist
- es Tag ist
- SOC über Mindest-SOC liegt
- SOC unter Ziel-SOC liegt
- SOC mehr als 2 Prozentpunkte hinter dem Ladeplan liegt

Steht `SOC-Ladeplan` auf **Im Ladeplan** oder **Vor Ladeplan**, bleibt die
bestehende Automatik zuständig.

## 9. SOC-Nachladung wirkt zu stark

Parameter **SOC-Nachholzeit** erhöhen.

Beispiel:

```text
2,0 h -> 3,0 h
```

Dadurch wird der Rückstand auf einen längeren Zeitraum verteilt und die
berechnete dynamische Ladeleistung sinkt.

## 10. SOC-Nachladung wirkt zu schwach

Parameter **SOC-Nachholzeit** reduzieren.

Beispiel:

```text
2,0 h -> 1,0 h
```

Nicht sofort extrem kleine Werte verwenden. Zunächst die Sensoren und das
Reglerverhalten beobachten.

## 11. Reglermodus „SOC-Nachladung“ erscheint nicht

Der Modus erscheint nur bei aktivem Eingriff der neuen Funktion.

Prüfen:

```text
Optimierer-Berechnung aktiv = Ein
Dynamische SOC-Steuerung aktiv = Ein
Betriebsart = Automatik
SOC-Ladeplan = Hinter Ladeplan
```

Außerdem müssen Tag, Forecast und SOC-Grenzen die Aktivierung erlauben.

## 12. Dynamische Sensoren rechnen, obwohl der Schalter aus ist

Das ist beabsichtigt.

Beta 8 berechnet:

```text
Dynamisches SOC-Soll
SOC-Abweichung
SOC-Ladeplan
Dynamisch erforderliche Ladeleistung
```

auch bei ausgeschalteter dynamischer SOC-Steuerung.

Dadurch kann die Berechnung zunächst gefahrlos beobachtet werden.

## 13. Eigenverbrauch, Ladepriorität oder Manuell verändern sich nicht

Das ist ebenfalls beabsichtigt.

Beta 8 beeinflusst ausschließlich die Betriebsart **Automatik**.

Die explizit gewählten Betriebsarten:

```text
Eigenverbrauch
Ladepriorität
Manuell
```

behalten ihr bisheriges Verhalten.

## 14. Optimizer berechnet, steuert aber nicht

Prüfen:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Ein
```

Danach am Schalter **NOAH-Steuerung aktiv** das Attribut:

```text
control_status
```

prüfen.

### `disabled`

Aktive Steuerung ist aus.

### `optimizer_disabled`

Berechnung ist aus.

### `legacy_controller_active`

Der alte YAML-Optimizer ist noch aktiv:

```text
input_boolean.noah_optimizer_enabled = on
```

### `critical_data_missing`

Mindestens ein kritischer Messwert fehlt.

### `actuator_unavailable`

Die beschreibbare Stellgröße ist nicht verfügbar.

### `rate_limited`

Normaler Zustand direkt nach einem Stellbefehl.

### `waiting_for_retry`

Sollwert und Stellgröße weichen noch ab; der Controller wartet auf den
Wiederholungszeitpunkt.

### `in_sync`

Sollwert und Stellgröße liegen innerhalb der Hysterese.

### `command_failed`

`number.set_value` ist fehlgeschlagen. Protokoll prüfen.

### `failsafe`

Kritische Messdaten haben zu lange gefehlt.

## 15. Dashboard erscheint nicht

Im Protokoll nach:

```text
Could not create the NOAH Optimizer dashboard
```

suchen.

Mögliche Ursache ist ein bereits belegter Pfad:

```text
/noah-optimizer
```

## 16. Dashboardfehler nach Beta 8 / Beta 9

### `TemplateSyntaxError: unexpected '}'`

Wenn in der Karte **Reglerstatus** nur der Titel angezeigt wird und darunter die Fehlermeldung

`TemplateSyntaxError: unexpected '}'`

erscheint, wurde das Dashboard wahrscheinlich bereits durch Beta 8 migriert.

Beta 8 konnte beim Einfügen des dynamischen SOC-Ladeplanstatus einen
fehlerhaften Jinja-Ausdruck erzeugen.

### Lösung

1. `2.0.0-beta.9` über HACS installieren.
2. Home Assistant vollständig neu starten.
3. Dashboard erneut öffnen.

Beta 9 erhöht die Dashboard-Template-Version auf 9 und repariert die betroffene
Zeile automatisch.

Das Dashboard muss nicht gelöscht oder neu erstellt werden.

### Neue Dashboardelemente fehlen

Prüfen:

- tatsächlich `2.0.0-beta.9` installiert
- Home Assistant nach dem HACS-Update vollständig neu gestartet
- Protokoll auf `noah_optimizer`-Fehler prüfen

Stark veränderte Standardkarten können verhindern, dass einzelne Blöcke
automatisch erkannt werden. Die Integration überschreibt bewusst nicht das
gesamte benutzerdefinierte Dashboard.

## 17. Power Flow Card Plus fehlt

Fehler wie:

```text
Custom element doesn't exist: power-flow-card-plus
```

bedeuten, dass Power Flow Card Plus nicht installiert oder noch nicht im
Frontend geladen ist.

In HACS installieren und Browser/App vollständig neu laden.

## 18. ApexCharts Card fehlt

Fehler wie:

```text
Custom element doesn't exist: apexcharts-card
```

entsprechend durch Installation von ApexCharts Card beheben.

## 19. Failsafe

Fehlen kritische Daten zehn Minuten:

- persistente Benachrichtigung wird erzeugt
- bei erreichbarer Stellgröße wird `0 W` angefordert
- bei nicht erreichbarer Stellgröße bleibt die Warnung trotzdem bestehen

Nach Wiederkehr der Daten wird der Failsafe zurückgesetzt.

## 20. Legacy-YAML und HACS gleichzeitig aktiv

Das ist nicht zulässig.

Vor Aktivierung der HACS-Steuerung:

```text
input_boolean.noah_optimizer_enabled = Aus
```

setzen.

Die Beta-8-Dynamik wird nicht in die Legacy-YAML-Regelung zurückportiert.

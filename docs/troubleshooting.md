# Fehlerbehebung

Dieses Dokument behandelt zuerst die HACS-Integration und anschließend die
ältere Legacy-YAML-Version.

## 1. Integration wird nicht geladen

Unter **Einstellungen → System → Protokolle** nach:

```text
noah_optimizer
```

suchen.

Zusätzlich prüfen:

- HACS-Installation vollständig
- Home Assistant nach dem Update neu gestartet
- `manifest.json` auf der erwarteten Beta-Version
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

## 3. Stellgröße nicht verfügbar

Die konfigurierte NOAH-System-Output-Power-Entität muss:

- eine `number`-Entität sein
- einen numerischen Zustand besitzen
- in W oder kW arbeiten
- über `number.set_value` beschreibbar sein

Unter **Werkzeuge → Aktionen** testweise `number.set_value` ausführen.

Ein normaler `sensor.*_output_power` ist nur ein Messwert und keine
beschreibbare Stellgröße.

## 4. Netzbezug und Einspeisung sind vertauscht

Erwartete Konvention:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Test:

1. Einen größeren Verbraucher einschalten.
2. Die saldierte Netzleistung muss deutlich positiv werden.
3. Bei PV-Überschuss muss sie negativ werden.

Bei umgekehrter Konvention die Integration mit aktivierter Option
**Netzvorzeichen umkehren** einrichten.

## 5. Hauslast wirkt unplausibel

Ungefähr gilt:

```text
Hauslast = Netzleistung + NOAH-Ausgangsleistung
```

Beispiel:

```text
800 W Netzbezug
+ 200 W NOAH-Ausgang
= 1000 W Hauslast
```

Kurzzeitige Abweichungen können durch unterschiedliche Aktualisierungszeiten
der Quellsensoren entstehen.

## 6. Optimizer berechnet, steuert aber nicht

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

Typische Ursachen:

### `disabled`

Aktive Steuerung ist aus.

### `optimizer_disabled`

Berechnung ist aus.

### `legacy_controller_active`

Der alte YAML-Optimizer ist noch aktiv:

```text
input_boolean.noah_optimizer_enabled = on
```

Diesen zuerst ausschalten.

### `critical_data_missing`

Mindestens ein kritischer Messwert fehlt.

### `actuator_unavailable`

Die beschreibbare Stellgröße ist nicht verfügbar.

### `rate_limited`

Normaler Zustand direkt nach einem Stellbefehl. Der Controller wartet den
Mindestabstand ab.

### `waiting_for_retry`

Soll und tatsächliche Stellgröße weichen noch ab; der Controller wartet auf
den Wiederholungszeitpunkt.

### `in_sync`

Normaler Ruhezustand. Sollwert und Stellgröße liegen innerhalb der
Schalt-Hysterese.

### `command_failed`

Der Aufruf von `number.set_value` ist fehlgeschlagen. Protokoll prüfen.

### `failsafe`

Kritische Messdaten haben zu lange gefehlt.

## 7. Dashboard erscheint nicht in der Seitenleiste

Bei einer Neuinstallation muss im Config Flow:

```text
Dashboard in der Seitenleiste anzeigen
```

aktiviert sein.

Bei einem Upgrade von Beta 5 verwendet Beta 6 standardmäßig `Ein`.

Im Protokoll nach:

```text
Could not create the NOAH Optimizer dashboard
```

suchen.

Mögliche Ursache ist ein bereits belegter Pfad:

```text
/noah-optimizer
```

## 8. Dashboard ist leer oder meldet unbekannte Entitäten

Beta 6 löst die Entity-IDs über die Entity Registry auf.

Falls das Anlegen fehlschlägt, im Protokoll nach:

```text
Could not resolve dashboard entity
```

suchen.

Prüfen, ob alle Integration-Entitäten tatsächlich angelegt wurden.

## 9. Power Flow Card Plus fehlt

Fehler wie:

```text
Custom element doesn't exist: power-flow-card-plus
```

bedeuten, dass Power Flow Card Plus nicht installiert oder noch nicht im
Frontend geladen ist.

In HACS installieren und Browser/App vollständig neu laden.

## 10. ApexCharts Card fehlt

Fehler wie:

```text
Custom element doesn't exist: apexcharts-card
```

entsprechend durch Installation von ApexCharts Card in HACS beheben.

## 11. Lade- und Entladerichtung im Energiefluss

Im HACS-Dashboard gilt:

```text
battery.consumption = Entladeleistung
battery.production  = Ladeleistung
```

Für das Netz:

```text
grid.consumption = Netzbezug
grid.production  = Netzeinspeisung
```

Power Flow Card Plus zeigt mit `display_state: two_way` beide Richtungen
gleichzeitig.

## 12. Dashboardänderungen verschwinden

Beta 6 schreibt den Standardinhalt nur, wenn noch keine gespeicherte
NOAH-Dashboard-Konfiguration existiert.

Ein Neustart oder Integration-Reload darf Benutzeränderungen nicht
überschreiben.

Tritt das dennoch auf:

1. Protokoll prüfen.
2. Sicherstellen, dass nur eine Version der Custom Integration vorhanden ist.
3. Prüfen, ob der Dashboard-Speicher manuell gelöscht wurde.

## 13. Falsche Dashboard-Sprache

Die Sprache wird nur bei der erstmaligen Erzeugung des Standard-Dashboards
ausgewählt.

```text
Deutsch -> deutsche Vorlage
sonst   -> englische Vorlage
```

Ein späterer Home-Assistant-Sprachwechsel ersetzt ein bereits gespeichertes
Dashboard absichtlich nicht.

## 14. Failsafe

Fehlen kritische Daten zehn Minuten:

- persistente Benachrichtigung wird erzeugt
- bei erreichbarer Stellgröße wird `0 W` angefordert
- bei nicht erreichbarer Stellgröße bleibt die Warnung trotzdem bestehen

Nach Wiederkehr der Daten muss die Warnung wieder verschwinden.

## 15. Legacy-YAML: Entitäten fehlen

Für die alte Package-Version prüfen:

```text
/config/packages/noah_optimizer.yaml
```

und in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Danach unter **Werkzeuge → YAML** die Konfiguration prüfen und neu starten.

## 16. Legacy-YAML: Energiefluss zeigt Batterie falsch herum

Für das alte Dashboard muss Power Flow Card Plus so konfiguriert sein:

```yaml
battery:
  entity:
    consumption: sensor.noah_opt_ladeleistung
    production: sensor.noah_opt_entladeleistung
  state_of_charge: sensor.noah_opt_soc
  display_state: two_way
```

Nicht vertauschen:

```text
consumption = Laden
production  = Entladen
```

## 17. Legacy-YAML und HACS gleichzeitig aktiv

Das ist nicht zulässig.

Vor Aktivierung der HACS-Steuerung:

```text
input_boolean.noah_optimizer_enabled = Aus
```

setzen.

Die HACS-Integration enthält zusätzlich eine Software-Sperre, die normale
Stellbefehle blockiert, solange dieser Legacy-Helfer `on` ist.

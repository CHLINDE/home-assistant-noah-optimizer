# Troubleshooting

Dieses Dokument beschreibt typische Fehlerbilder und Prüfungen für den NOAH Optimizer.

## 1. Datenstatus zeigt „Messwerte fehlen“

Prüfe:

```text
sensor.noah_opt_netzleistung
sensor.noah_opt_pv_leistung
sensor.noah_opt_ausgangsleistung
sensor.noah_opt_soc
```

Mindestens eine externe Quellentität ist wahrscheinlich:

- nicht vorhanden
- falsch geschrieben
- `unknown`
- `unavailable`

Kontrolliere die in `noah_optimizer.yaml` eingesetzten Entity-IDs.

## 2. Datenstatus zeigt „Stellgröße fehlt“

Prüfe die `number`-Entität:

```text
number.dein_noah_system_output_power
```

Die Entität muss:

- mit `number.` beginnen
- vorhanden sein
- einen verstellbaren Wert anzeigen
- über `number.set_value` beschreibbar sein

Ein `sensor.*_output_power` ist nur ein Messwert und kann nicht als Stellgröße verwendet werden.

## 3. Optimierer-Sensoren existieren nicht

Prüfe:

1. Liegt die Datei unter `/config/packages/noah_optimizer.yaml`?
2. Ist die Package-Unterstützung in `configuration.yaml` aktiviert?
3. Wurde die YAML-Konfiguration erfolgreich geprüft?
4. Wurde Home Assistant vollständig neu gestartet?
5. Gibt es doppelte Dateien mit denselben `unique_id`-Werten?

Suche im gesamten `/config`-Verzeichnis nach:

```text
unique_id: noah_opt_controller_mode
```

Dieser Eintrag darf nur einmal vorkommen.

## 4. YAML-Editor zeigt Warnungen zu internen Entitäten

Vor dem ersten erfolgreichen Neustart kennt Home Assistant die neuen Entitäten noch nicht.

Warnungen wie:

```text
sensor.noah_opt_netzleistung does not exist
```

können vor dem ersten Laden des Packages auftreten.

Entscheidend ist die Prüfung unter:

**Entwicklerwerkzeuge → YAML → Konfiguration prüfen**

## 5. Netzbezug und Einspeisung sind vertauscht

Prüfe `sensor.noah_opt_netzleistung`:

```text
positiv = Netzbezug
negativ = Einspeisung
```

Ist das Ergebnis umgekehrt, aktiviere:

```text
input_boolean.noah_grid_sign_inverted
```

Test:

1. Größeren Verbraucher einschalten.
2. Netzleistung muss deutlich positiv werden.
3. Bei PV-Überschuss muss sie negativ werden.

## 6. Hauslast ist unplausibel

Die Berechnung lautet:

```text
Hauslast = Netzleistung + NOAH-Ausgangsleistung
```

Prüfe:

- Netzleistung in W
- NOAH-Ausgangsleistung in W
- korrekte Vorzeichenrichtung
- unterschiedliche Aktualisierungsintervalle

Kurzzeitige Abweichungen sind normal, da Stromzähler und Noah-MQTT nicht gleichzeitig aktualisieren.

## 7. System Output Power wird gesetzt, Output Power folgt aber nicht

Mögliche Ursachen:

### Akku ist voll

Bei vollem Akku und Solarüberschuss kann der NOAH mehr Leistung zum Wechselrichter durchreichen als die eingestellte Standardausgangsleistung.

### Verzögerte Aktualisierung

Noah-MQTT, Growatt und der Stromzähler aktualisieren nicht zwingend gleichzeitig.

### Growatt-Zeitpläne

Aktive Arbeitszeitfenster oder Zeitpläne in ShinePhone können die Standardausgangsleistung überschreiben.

### Schreibzugriff prüfen

Führe manuell aus:

```yaml
action: number.set_value
target:
  entity_id: number.dein_noah_system_output_power
data:
  value: 300
```

Prüfe zuerst die `number`-Entität und danach den tatsächlichen Output-Power-Sensor.

## 8. Akku wird laut Dashboard geladen, obwohl der SOC fällt

Prüfe die Rohsensoren:

```text
sensor.dein_noah_charging_power
sensor.dein_noah_discharge_power
```

Erwartet:

```text
Charging Power > 0  = Akkuladung
Discharge Power > 0 = Akkuentladung
```

Die Package-Zuordnung muss unverändert bleiben.

In Power Flow Card Plus wird für die Batterie verwendet:

```yaml
entity:
  consumption: sensor.noah_opt_entladeleistung
  production: sensor.noah_opt_ladeleistung
```

Diese Zuordnung ist für die Flussrichtung der Karte erforderlich.

## 9. Reglermodus zeigt „Mindest-SOC“, obwohl der Akku darüber liegt

Prüfe:

```text
sensor.noah_opt_soc
input_number.noah_min_soc
```

Wenn der SOC tatsächlich größer ist, löse eine Neuberechnung aus:

1. Optimierer ausschalten.
2. Prüfen, ob der Reglermodus auf `Aus` wechselt.
3. Optimierer wieder einschalten.

Prüfe außerdem auf doppelte Package-Dateien.

## 10. Abends steht der Regler auf „Ladepriorität“ und gibt 0 W aus

Prüfe:

```text
sensor.noah_opt_pv_leistung
state_attr('sun.sun', 'elevation')
sensor.noah_opt_reglermodus
```

Die veröffentlichte Konfiguration erkennt Nachtbetrieb bei:

```text
sun.sun = below_horizon
```

oder:

```text
Sonnenhöhe < 3°
PV-Leistung < 20 W
```

Wenn das nicht greift, prüfe, ob wirklich die aktuelle Package-Datei geladen wurde.

## 11. Akku wird nachts nicht entladen

Prüfe:

```text
NOAH Optimierer aktiv = Ein
NOAH Betriebsart = Automatik
SOC > Mindest-SOC
Reglermodus = Nachtbetrieb
NOAH maximale Ausgangsleistung nachts > 0 W
```

Prüfe außerdem:

```text
sensor.noah_opt_ausgangssollwert
number.dein_noah_system_output_power
```

## 12. Akku wird nachts zu schnell leer

Reduziere:

```text
NOAH maximale Ausgangsleistung nachts
```

Beispiel:

```text
von 800 W auf 400 W
```

Dadurch steigt zwar der Netzbezug, der Akku hält aber länger.

## 13. Akku wird abends nicht voll

Mögliche Ursachen:

- PV-Ertrag war geringer als prognostiziert
- Hausverbrauch war höher als angenommen
- Ziel-SOC ist hoch
- Prognosefaktor ist zu optimistisch
- Reserve ist zu klein
- während des Tages wurde zu viel Ausgangsleistung freigegeben

Schrittweise Anpassung:

1. Ziel-SOC kontrollieren.
2. Prognosefaktor von 0,80 auf 0,75 reduzieren.
3. Reserve von 0,25 auf 0,40 kWh erhöhen.
4. Erwartete Hauslast erhöhen.
5. Freigabemarge erhöhen.
6. Verlauf von PV, SOC, Ladeleistung und Sollwert vergleichen.

Ändere jeweils nur einen Parameter und beobachte mindestens einen vollständigen Tag.

## 14. Es wird eingespeist, obwohl der Akku nicht voll ist

Kurzzeitige Einspeisung ist bei dieser Regelung möglich.

Ursachen:

- Regelzyklus von fünf Minuten
- geglättete Netzleistung über fünf Minuten
- plötzlich abgeschaltete Verbraucher
- 50-W-Stellraster
- verzögerte Growatt- und MQTT-Werte
- Sollwert ist höher als die aktuelle Hauslast

Prüfe im Diagramm:

```text
NOAH-Ausgang
Hauslast
Netzeinspeisung
Akkuladung
Regler-Soll
Eigenverbrauch-Soll
Ladepriorität-Soll
```

Mögliche Anpassungen:

- Rest-Netzbezug erhöhen, beispielsweise 50 auf 80–100 W
- Stellgrößenraster auf 20 W verkleinern
- Hysterese moderat auf 30–40 W reduzieren

Eine vollständig sekundengenaue Nulleinspeiseregelung ist mit der cloudbasierten Stellgröße nicht zu erwarten.

## 15. Zu hoher Netzbezug trotz gefülltem Akku

Prüfe den Reglermodus.

### Nachtbetrieb

Das Nachtmaximum begrenzt die Ausgangsleistung:

```text
Sollwert = Minimum aus Eigenverbrauchs-Soll und Nachtmaximum
```

Erhöhe bei Bedarf:

```text
NOAH maximale Ausgangsleistung nachts
```

### Ladepriorität

Bei geringer Prognosedeckung reserviert der Regler Leistung für den Akku. Dies kann bewusst zu Netzbezug führen.

## 16. Prognosedeckung ist ständig niedrig

Die Berechnung umfasst:

```text
Ladebedarf
+ erwarteter Hausenergiebedarf
+ zusätzliche Reserve
```

und verwendet im Zähler nur:

```text
Restprognose × Prognosefaktor
```

Prüfe:

- Forecast-Sensor liefert kWh
- Akkukapazität ist korrekt
- erwartete Hauslast ist realistisch
- Ziel-SOC ist nicht unnötig hoch
- Reserve und Prognosefaktor sind sinnvoll

Die Prognosedeckung ist keine Erfolgswahrscheinlichkeit, sondern ein Verhältnis von verfügbarer Restprognose zu geplantem Restenergiebedarf.

## 17. Helfer springen nach Neustart auf andere Werte

Die veröffentlichte Datei enthält für die meisten Benutzerparameter keinen festen `initial:`-Wert.

Prüfe dennoch:

- ob noch eine ältere Package-Datei aktiv ist
- ob ein Helfer doppelt definiert wurde
- ob die Datei nach Änderungen neu geladen wurde
- ob Home Assistant den letzten Zustand wiederhergestellt hat

Der interne Helfer `noah_last_target_w` startet bewusst mit 0 W.

## 18. Failsafe-Benachrichtigung erscheint

Die Ausfallsicherung wurde ausgelöst, weil kritische Messwerte mindestens zehn Minuten fehlten.

Prüfe:

- MQTT-Verbindung
- Noah-MQTT
- Stromzählersensor
- Forecast ist nicht kritisch, kann aber separat fehlen
- NOAH-Gerät online
- Home-Assistant-Protokolle

Sobald die kritischen Daten wieder verfügbar sind, wird die Benachrichtigung automatisch verworfen.

## 19. Dashboard zeigt „Custom element doesn't exist“

Installiere beziehungsweise aktualisiere über HACS:

- Power Flow Card Plus
- ApexCharts Card

Danach:

- Browser vollständig neu laden
- Home-Assistant-App schließen und neu öffnen
- Ressourcen unter Dashboard-Ressourcen kontrollieren

## 20. Dashboard zeigt falsche oder fehlende Werte

Prüfe zunächst die zugrunde liegenden `sensor.noah_opt_...`-Entitäten.

Wenn diese korrekt sind, kontrolliere:

- Schreibfehler in `noah_dashboard.yaml`
- nicht ersetzte Stellgrößen-Entity
- deaktivierte Entitäten
- Browser-Cache
- HACS-Karten

## 21. Diagnose-Checkliste

Für eine Fehleranalyse sind folgende Werte besonders hilfreich:

```text
sensor.noah_opt_datenstatus
binary_sensor.noah_opt_kritische_daten_ok
sensor.noah_opt_reglermodus
sensor.noah_opt_netzleistung
sensor.noah_opt_netzleistung_5_min
sensor.noah_opt_pv_leistung
sensor.noah_opt_ausgangsleistung
sensor.noah_opt_soc
sensor.noah_opt_ladeleistung
sensor.noah_opt_entladeleistung
sensor.noah_opt_ausgangssollwert
sensor.noah_opt_eigenverbrauch_soll
sensor.noah_opt_ladeprioritat_soll
sensor.noah_opt_restprognose_heute
sensor.noah_opt_wirksame_restprognose
sensor.noah_opt_ladebedarf
sensor.noah_opt_prognosemarge
number.dein_noah_system_output_power
input_number.noah_last_target_w
input_datetime.noah_last_command
```

Zusätzlich sind die Ablaufverfolgung der Automation und die Noah-MQTT-Protokolle hilfreich.

## 22. Problembericht für GitHub

Ein vollständiger Fehlerbericht sollte enthalten:

- Home-Assistant-Version
- Noah-MQTT-Version
- Anzahl der NOAH-Module
- relevante Entity-IDs ohne Zugangsdaten
- Betriebsart
- eingestellte Parameter
- Werte aus der Diagnose-Checkliste
- Screenshot des Dashboards
- Ablaufverfolgung der letzten Automation
- relevante Protokollauszüge
- genaue Uhrzeit des Fehlers

Keine Passwörter, Tokens, MQTT-Zugangsdaten oder vollständigen Home-Assistant-Backups veröffentlichen.

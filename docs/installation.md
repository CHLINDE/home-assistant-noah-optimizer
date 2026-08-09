# Installation

Diese Anleitung beschreibt die Installation des **Home Assistant Growatt NOAH Optimizers**.

Ab Version `2.0.0-beta.7` ist die HACS-Integration der empfohlene
Installationsweg. Die ältere YAML-Package-Version wird weiter unten separat
beschrieben.

## 1. Voraussetzungen

Für den Optimizer werden benötigt:

- Home Assistant
- HACS
- ein funktionsfähiger MQTT-Broker
- Noah-MQTT für den Growatt NOAH
- Forecast.Solar
- die Home-Assistant-Sun-Integration
- ein saldierter Netzleistungssensor
- eine beschreibbare `number`-Entität für NOAH System Output Power

Für das erweiterte Dashboard werden zusätzlich benötigt:

- Power Flow Card Plus
- ApexCharts Card

Die Custom Cards sind nur für die Darstellung erforderlich. Der Optimizer
funktioniert auch ohne sie.

## 2. Benötigte Quell-Entitäten

Vor dem Einrichten müssen folgende Entitäten in Home Assistant vorhanden sein:

| Funktion | Entitätstyp | Typische Einheit |
|---|---|---|
| Saldierte Netzleistung | `sensor` | W oder kW |
| NOAH Solar Power | `sensor` | W oder kW |
| NOAH Output Power | `sensor` | W oder kW |
| NOAH SOC | `sensor` | % |
| NOAH Charging Power | `sensor` | W oder kW |
| NOAH Discharge Power | `sensor` | W oder kW |
| Forecast.Solar Restprognose heute | `sensor` | Wh oder kWh |
| NOAH System Output Power | `number` | W oder kW |

Die vorhandenen Entity-IDs können unter **Werkzeuge → Zustände** geprüft werden.

### Netzvorzeichen

Der Optimizer erwartet:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Verwendet der Netzsensor die umgekehrte Konvention, während der Einrichtung
**Netzvorzeichen umkehren** aktivieren.

## 3. Dashboardkarten installieren

Für das vollständige Dashboard in HACS zusätzlich installieren:

```text
Power Flow Card Plus
ApexCharts Card
```

Danach den Browser beziehungsweise die Home-Assistant-App vollständig neu
laden.

Fehlen diese Karten, bleibt die Optimizer-Integration funktionsfähig. Im
Dashboard erscheinen dann lediglich Fehler für die betreffenden Custom Cards.

## 4. Repository in HACS hinzufügen

Falls das Projekt noch nicht direkt in HACS gefunden wird:

1. HACS öffnen.
2. Benutzerdefinierte Repositories öffnen.
3. Repository eintragen:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

4. Typ **Integration** wählen.
5. Nach **Growatt NOAH Optimizer** suchen.

## 5. Beta 6 installieren

Version:

```text
2.0.0-beta.6
```

installieren und Home Assistant vollständig neu starten.

## 6. Integration einrichten

Öffne:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

und suche nach:

```text
Growatt NOAH Optimizer
```

Wähle anschließend die acht Quell-Entitäten aus.

Zusätzlich gibt es zwei Setup-Optionen:

### Netzvorzeichen umkehren

Aktivieren, wenn der Netzsensor positive Werte für Einspeisung und negative
Werte für Bezug liefert.

### Dashboard in der Seitenleiste anzeigen

Standard:

```text
Ein
```

Bei **Ein** wird der Eintrag **NOAH Optimizer** direkt in der Seitenleiste
registriert. Bei **Aus** wird das Dashboard trotzdem erzeugt, aber nicht in der
Seitenleiste angezeigt.

## 7. Update von Beta 5

Beim Update von `2.0.0-beta.5` auf `2.0.0-beta.6` muss die Integration nicht neu
eingerichtet werden.

Die bereits ausgewählten Quell-Entitäten und Optimizer-Parameter bleiben
erhalten.

Da Beta 5 die Dashboard-Option noch nicht kannte, gilt beim Upgrade:

```text
Dashboard in der Seitenleiste anzeigen = Ein
```

Während des Beta-Updates empfiehlt sich:

```text
NOAH-Steuerung aktiv = Aus
```

Nach erfolgreicher Prüfung kann sie wieder eingeschaltet werden.

## 8. Automatisches Dashboard

Beta 6 legt beim ersten erfolgreichen Start eine eigene Lovelace-Konfiguration
für den Panel-Pfad:

```text
/noah-optimizer
```

an.

Die Integration benutzt dabei **keine zweite Home-Assistant
DashboardsCollection**. Das Dashboard wird als von der Integration verwaltetes
Lovelace-Panel registriert.

Wichtig:

- `configuration.yaml` muss nicht geändert werden.
- Die Entity-IDs werden dynamisch über die Entity Registry ermittelt.
- Bereichspräfixe wie `terrasse_` müssen nicht bekannt sein.
- Das Dashboard wird nur initial mit dem Standardinhalt befüllt.
- Spätere Benutzeränderungen werden nicht überschrieben.
- Beim Reload wird nur die Laufzeitregistrierung entfernt und wieder angelegt;
  die gespeicherte Dashboard-Konfiguration bleibt erhalten.

### Sprache

Bei der ersten Erzeugung gilt:

```text
Home Assistant Deutsch -> dashboard_de.yaml
sonstige Sprache        -> dashboard_en.yaml
```

Ein späterer Sprachwechsel überschreibt ein bereits angepasstes Dashboard
nicht automatisch.

## 9. Erste Funktionsprüfung

Zunächst:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Aus
Betriebsart = Automatik
```

setzen.

Im Dashboard oder unter **Werkzeuge → Zustände** prüfen:

```text
Datenstatus = OK
Kritische Daten = verfügbar
Prognose = verfügbar
Stellgröße = verfügbar
```

Außerdem müssen plausibel sein:

- Netzleistung
- Netzbezug
- Netzeinspeisung
- PV-Leistung
- Ausgangsleistung
- Hauslast
- Ladezustand
- Ladeleistung
- Entladeleistung
- Restprognose
- Ausgangssollwert
- Reglermodus

## 10. Netzrichtung prüfen

Einen größeren Verbraucher einschalten.

Bei Netzbezug muss die saldierte Netzleistung positiv sein, zum Beispiel:

```text
+800 W = 800 W Netzbezug
```

Bei PV-Überschuss muss sie negativ sein:

```text
-500 W = 500 W Netzeinspeisung
```

Ist das Verhalten umgekehrt, die Integration mit aktivierter Option
**Netzvorzeichen umkehren** neu einrichten.

## 11. Grundeinstellungen

Die Standardwerte der HACS-Integration sind:

| Einstellung | Standard |
|---|---:|
| Nutzbare Akkukapazität | 2,048 kWh |
| Ziel-SOC bei Sonnenuntergang | 95 % |
| Mindest-SOC | 10 % |
| Angenommener Ladewirkungsgrad | 0,90 |
| Prognose-Sicherheitsfaktor | 0,80 |
| Zusätzliche Energiereserve | 0,25 kWh |
| Freigabemarge | 0,50 kWh |
| Erwartete mittlere Hauslast | 250 W |
| Gewünschter Rest-Netzbezug | 50 W |
| Maximale Ausgangsleistung | 800 W |
| Maximale Ausgangsleistung nachts | 400 W |
| Manuelle Ausgangsleistung | 200 W |
| Stellgrößenraster | 50 W |
| Schalt-Hysterese | 50 W |

Bei mehreren NOAH-Modulen muss die gesamte nutzbare Kapazität eingetragen
werden.

## 12. Stellgröße manuell testen

Vor dem Einschalten der aktiven Regelung unter **Werkzeuge → Aktionen** den
Dienst:

```text
number.set_value
```

mit der ausgewählten NOAH-System-Output-Power-Entität testen.

Bei einer Stellgröße in Watt zum Beispiel:

```yaml
action: number.set_value
target:
  entity_id: number.dein_noah_system_output_power
data:
  value: 300
```

Bei einer Stellgröße in kW entsprechend:

```yaml
data:
  value: 0.3
```

Danach prüfen, ob die Stellgröße den Wert angenommen hat.

## 13. Aktive Steuerung einschalten

Erst wenn Daten und Sollwert plausibel sind:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Ein
Betriebsart = Automatik
```

Der Controller kann dann die konfigurierte Stellgröße beschreiben.

Typische Diagnoseattribute am Schalter **NOAH-Steuerung aktiv**:

```text
control_status
last_command_target
last_command_at
```

Ein häufiger Normalzustand ist:

```text
in_sync
```

## 14. Schutzmechanismen

Die aktive Regelung enthält:

- Schalt-Hysterese
- Mindestabstand zwischen normalen Stellbefehlen
- Wiederholungsversuch
- 10-Minuten-Failsafe bei dauerhaft fehlenden kritischen Daten
- persistente Home-Assistant-Benachrichtigung
- Sperre gegen den Legacy-YAML-Controller

Ist beim Failsafe die Stellgröße erreichbar, wird `0 W` angefordert. Ist die
Stellgröße nicht erreichbar, wird die Warnmeldung trotzdem erzeugt.

## 15. Legacy-YAML-Optimizer

Der ältere YAML-Optimizer darf nicht gleichzeitig mit der aktiven
HACS-Steuerung denselben NOAH regeln.

Die HACS-Integration prüft den Legacy-Helfer:

```text
input_boolean.noah_optimizer_enabled
```

Steht dieser auf `on`, werden normale HACS-Stellbefehle blockiert.

### Legacy-Package installieren

Package-Unterstützung in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Dann:

```text
noah_optimizer.yaml
```

nach:

```text
/config/packages/noah_optimizer.yaml
```

kopieren und alle Platzhalter-Entity-IDs anpassen.

Anschließend unter **Werkzeuge → YAML** die Konfiguration prüfen und Home
Assistant neu starten.

Das Legacy-Dashboard befindet sich unter:

```text
dashboards/noah_dashboard.yaml
```

Für neue Installationen wird die HACS-Integration empfohlen.

## 16. Weiterführende Dokumentation

- [Konfiguration](configuration.md)
- [Fehlerbehebung](troubleshooting.md)
- [HACS Beta](hacs-beta.md)

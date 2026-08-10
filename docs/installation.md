# Installation

Diese Anleitung beschreibt die Installation und das Update des **Home
Assistant Growatt NOAH Optimizers** für Version `2.0.0-beta.9`.

Für neue Installationen wird die HACS-Integration empfohlen.

## 1. Voraussetzungen

Benötigt werden:

- Home Assistant
- HACS
- MQTT
- Noah-MQTT
- Forecast.Solar
- Sun-Integration
- saldierter Netzleistungssensor
- beschreibbare `number`-Entität für NOAH System Output Power

Für das vollständige Dashboard zusätzlich:

- Power Flow Card Plus
- ApexCharts Card

Die beiden Dashboardkarten werden nicht automatisch installiert.

## 2. Benötigte Quell-Entitäten

Vor dem Einrichten müssen vorhanden sein:

| Funktion | Entitätstyp | Einheit |
|---|---|---|
| Saldierte Netzleistung | `sensor` | W oder kW |
| NOAH Solar Power | `sensor` | W oder kW |
| NOAH Output Power | `sensor` | W oder kW |
| NOAH SOC | `sensor` | % |
| NOAH Charging Power | `sensor` | W oder kW |
| NOAH Discharge Power | `sensor` | W oder kW |
| Forecast.Solar Restprognose heute | `sensor` | Wh oder kWh |
| NOAH System Output Power | `number` | W oder kW |

Die Entity-IDs können unter **Werkzeuge → Zustände** geprüft werden.

### Netzvorzeichen

Erwartet wird:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Bei umgekehrter Konvention während der Einrichtung **Netzvorzeichen umkehren**
aktivieren.

## 3. Dashboardkarten installieren

In HACS installieren:

```text
Power Flow Card Plus
ApexCharts Card
```

Danach Browser beziehungsweise Home-Assistant-App vollständig neu laden.

Der Optimizer selbst funktioniert auch ohne diese Karten.

## 4. Repository in HACS öffnen

Am einfachsten über My Home Assistant:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

Alternativ das Repository in HACS als benutzerdefiniertes Repository hinzufügen:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

## 5. Beta 9 installieren

Zu installierende Version:

```text
2.0.0-beta.9
```

Nach der Installation Home Assistant vollständig neu starten.

Bei Verwendung eines GitHub-Pre-Releases muss HACS für dieses Repository auch
Vorabversionen berücksichtigen.

## 6. Neue Installation einrichten

Öffne:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

und suche nach:

```text
Growatt NOAH Optimizer
```

Wähle die acht Quell-Entitäten aus.

Zusätzlich stehen zur Verfügung:

### Netzvorzeichen umkehren

Aktivieren, wenn dein Netzsensor positive Werte für Einspeisung und negative
Werte für Bezug liefert.

### Dashboard in der Seitenleiste anzeigen

Standard:

```text
Ein
```

## 7. Update auf Beta 9

Vor dem Update empfiehlt sich:

```text
NOAH-Steuerung aktiv = Aus
```

Danach Beta 8 über HACS installieren und Home Assistant neu starten.

Vorhandene Quellentitäten und bisherige Optimizer-Parameter bleiben erhalten.

Neu hinzu kommen automatisch:

```text
Dynamische SOC-Steuerung aktiv
SOC-Nachholzeit
Dynamisches SOC-Soll
SOC-Abweichung
SOC-Ladeplan
Dynamisch erforderliche Ladeleistung
```

Wichtig:

```text
Dynamische SOC-Steuerung aktiv = Aus
```

ist der Standard. Das Update verändert deshalb nicht automatisch die bisherige
Ausgangsregelung.

## 8. Dashboard-Migration

Beta 8 verwendet Dashboard-Template-Version 8.

Ein vorhandenes Beta-6-/Beta-7-Dashboard wird **nicht vollständig ersetzt**.
Die Integration nimmt nur gezielte Migrationen vor:

- Beta-6-Batteriezuordnung korrigieren, wenn sie noch exakt unverändert vorliegt
- Schalter für dynamische SOC-Steuerung ergänzen
- neue SOC-Sensoren ergänzen
- SOC-Nachholzeit ergänzen
- SOC-Planungsdiagramm ergänzen
- Reglerstatus um dynamische SOC-Werte ergänzen, wenn der Standardblock erkannt wird

Eigene sonstige Dashboard-Anpassungen bleiben erhalten.

Bei einer Neuinstallation wird direkt die vollständige Beta-8-Vorlage erzeugt.

## 9. Erste Prüfung nach dem Update

Zunächst:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Aus
Dynamische SOC-Steuerung aktiv = Aus
Betriebsart = Automatik
```

Im Dashboard beziehungsweise unter **Werkzeuge → Zustände** prüfen:

```text
Datenstatus
Dynamisches SOC-Soll
SOC-Abweichung
SOC-Ladeplan
Dynamisch erforderliche Ladeleistung
```

Die neuen Werte dürfen den bisherigen Ausgangssollwert noch nicht verändern.

## 10. Dynamische SOC-Werte plausibilisieren

Beispiel:

```text
Ist-SOC:                       40 %
Dynamisches SOC-Soll:          52 %
SOC-Abweichung:               -12 %
SOC-Ladeplan:                  Hinter Ladeplan
Dynamisch erforderliche
Ladeleistung:                 280 W
```

Bei hoher verbleibender PV-Prognose darf das dynamische SOC-Soll morgens
niedrig sein. Mit abnehmender Restprognose sollte es Richtung Ziel-SOC steigen.

Fehlt Forecast.Solar, sind die dynamischen SOC-Werte nicht verfügbar und die
neue Funktion greift nicht in die Regelung ein.

## 11. Dynamische SOC-Steuerung aktivieren

Erst nach plausibler Beobachtung:

```text
Dynamische SOC-Steuerung aktiv = Ein
```

Die Funktion beeinflusst ausschließlich die Betriebsart **Automatik**.

Liegt der Akku mehr als 2 Prozentpunkte hinter dem Ladeplan, kann der interne
Reglermodus auf:

```text
SOC-Nachladung
```

wechseln und mehr PV-Leistung für die Batterieladung reservieren.

## 12. SOC-Nachholzeit einstellen

Standard:

```text
2,0 h
```

Empfohlener Startwert:

```text
2,0 h
```

Kürzer bedeutet stärkere Reaktion auf einen SOC-Rückstand. Länger bedeutet
eine sanftere Verteilung der Nachladung.

## 13. Stellgröße manuell testen

Vor Aktivierung der NOAH-Steuerung unter **Werkzeuge → Aktionen** den Dienst:

```text
number.set_value
```

mit der ausgewählten `NOAH System Output Power`-Entität testen.

Beispiel bei Watt:

```yaml
action: number.set_value
target:
  entity_id: number.dein_noah_system_output_power
data:
  value: 300
```

Danach prüfen, ob die Stellgröße den Wert annimmt.

## 14. Aktive NOAH-Steuerung einschalten

Erst wenn Daten und Sollwert plausibel sind:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Ein
Betriebsart = Automatik
```

Die dynamische SOC-Steuerung kann unabhängig davon ein- oder ausgeschaltet
bleiben.

## 15. Schutzmechanismen

Die aktive Steuerung enthält weiterhin:

- Schalt-Hysterese
- Mindestabstand zwischen normalen Stellbefehlen
- Wiederholungsversuch
- 10-Minuten-Failsafe bei dauerhaft fehlenden kritischen Daten
- persistente Home-Assistant-Benachrichtigung
- Sperre gegen den Legacy-YAML-Controller

## 16. Legacy-YAML-Optimizer

Der ältere YAML-Optimizer darf nicht gleichzeitig mit der aktiven
HACS-Steuerung denselben NOAH regeln.

Die HACS-Integration prüft:

```text
input_boolean.noah_optimizer_enabled
```

Steht dieser Helfer auf `on`, werden normale HACS-Stellbefehle blockiert.

Die Beta-8-Dynamik wird nur in der HACS-Integration implementiert; die
Legacy-YAML-Version erhält keine dynamische SOC-Regelung.

## 17. Weiterführende Dokumentation

- [Konfiguration](configuration.md)
- [Fehlerbehebung](troubleshooting.md)
- [HACS Beta](hacs-beta.md)

# Installation

Diese Anleitung beschreibt die Installation und das Update des **Home
Assistant Growatt NOAH Optimizers** für Version `2.0.0-beta.10`.

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

> **Hinweis zu Home Assistant 2026.8 und neuer:**  
> Home Assistant OS verwendet bei neuen Installationen standardmäßig Port 80
> statt Port 8123. Home Assistant Container verwendet weiterhin standardmäßig
> Port 8123. Der HACS-Link selbst enthält keinen Home-Assistant-Port.
>
> Falls My Home Assistant noch eine Adresse mit `:8123` öffnet, muss dort die
> gespeicherte Instanz-URL auf die tatsächlich verwendete
> Home-Assistant-Adresse angepasst werden.

Alternativ das Repository in HACS als benutzerdefiniertes Repository hinzufügen:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

## 5. Beta 10 installieren

Zu installierende Version:

```text
2.0.0-beta.10
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

## 7. Update auf Beta 10

Vor dem Update:

```text
NOAH-Steuerung aktiv = Aus
Dynamische SOC-Steuerung aktiv = Aus
```

Danach Beta 10 über HACS installieren und Home Assistant vollständig neu starten.

### Update von Beta 9

Beta 10 übernimmt alle vorhandenen Einstellungen und Entitäten.

Geändert wird die Berechnung des dynamischen SOC-Ladeplans:

- zeitbasierte Sollkurve von Sonnenaufgang bis Sonnenuntergang
- Mindest-SOC als Startwert
- Ziel-SOC als Endwert
- Restprognose hebt die Kurve bei Bedarf progressiv an
- eine knappe Restprognose setzt das dynamische Soll nicht mehr sofort auf 100 %

Die Dashboard-Struktur wird nicht geändert. Die Dashboard-Template-Version
bleibt bei Version 9.

### Update von Beta 8 oder älter

Beim direkten Update auf Beta 10 werden weiterhin die bisherigen Migrationen
aus Beta 8 und Beta 9 ausgeführt, soweit sie für das vorhandene Dashboard
erforderlich sind.

Dazu gehören insbesondere:

```text
Dynamische SOC-Steuerung aktiv
SOC-Nachholzeit
Dynamisches SOC-Soll
SOC-Abweichung
SOC-Ladeplan
Dynamisch erforderliche Ladeleistung
```

und die Reparatur des Beta-8-Jinja-Fehlers im Reglerstatus.

Die dynamische SOC-Steuerung ist bei einer neuen Einrichtung standardmäßig
ausgeschaltet.

## 8. Dashboard und Migration

Beta 10 verändert die Dashboard-Struktur nicht.

Es werden keine neuen Dashboardkarten und keine neuen Dashboard-Entitäten
benötigt. Deshalb bleibt:

```text
Dashboard-Template-Version = 9
```

Der vorhandene Chart **Dynamischer SOC-Ladeplan** zeigt nach dem Update
automatisch die neue zeitbasierte Sollkurve.

Ältere Dashboard-Migrationen bleiben im Code erhalten:

- Beta-6-Batteriezuordnung korrigieren, wenn sie noch exakt unverändert vorliegt
- Beta-8-Dynamic-SOC-Elemente ergänzen, falls sie fehlen
- SOC-Planungsdiagramm ergänzen, falls es fehlt
- Reglerstatus um Dynamic-SOC-Werte erweitern
- fehlerhaften Beta-8-Jinja-Ausdruck reparieren

Eigene Dashboard-Anpassungen bleiben erhalten.

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

Die Werte werden bereits mit der Beta-10-Logik berechnet, beeinflussen den
Ausgangssollwert aber noch nicht, solange die dynamische SOC-Steuerung
ausgeschaltet ist.

## 10. Dynamische SOC-Werte plausibilisieren

Während des Tages sollte das dynamische SOC-Soll jetzt eine nachvollziehbare
Kurve bilden.

Bei Mindest-SOC `10 %` und Ziel-SOC `100 %` liegt das reine Zeit-Soll ungefähr
bei:

```text
Sonnenaufgang    10 %
25 % des Tages   32,5 %
50 % des Tages   55 %
75 % des Tages   77,5 %
Sonnenuntergang 100 %
```

Eine knappe Restprognose darf diese Kurve nach oben ziehen. Sie sollte das Soll
morgens aber nicht mehr allein deshalb sofort auf `100 %` setzen.

Beispiel:

```text
Ist-SOC:                       70 %
Dynamisches SOC-Soll:          66 %
SOC-Abweichung:                +4 %
SOC-Ladeplan:                  Vor Ladeplan
Dynamisch erforderliche
Ladeleistung:                   0 W
```

Bei stärkerem Prognosedruck kann das dynamische Soll zum gleichen Zeitpunkt
höher liegen.

Nach Sonnenuntergang fällt das dynamische Soll wieder auf den Mindest-SOC.
Das ist beabsichtigt, weil die Nachtregelung den Speicher bis zum Mindest-SOC
nutzen darf.

Fehlt Forecast.Solar, sind die dynamischen SOC-Werte nicht verfügbar und die
dynamische SOC-Steuerung greift nicht in die Regelung ein.

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

Die Betriebsarten **Manuell**, **Eigenverbrauch** und **Ladepriorität** werden
durch die dynamische SOC-Steuerung nicht verändert.

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

Das wirksame Nachholfenster wird zusätzlich durch die verbleibende Zeit bis
Sonnenuntergang begrenzt.

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

Die dynamische SOC-Regelung ab Beta 8 wird nur in der HACS-Integration
implementiert; die Legacy-YAML-Version erhält keine dynamische SOC-Regelung.

## 17. Weiterführende Dokumentation

- [Konfiguration](configuration.md)
- [Fehlerbehebung](troubleshooting.md)
- [HACS Beta](hacs-beta.md)
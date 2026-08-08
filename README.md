# Home Assistant Growatt NOAH Optimizer

Prognosebasierte Steuerung der Ausgangsleistung eines Growatt NOAH 2000
über Home Assistant und Noah-MQTT.

> **Status:** Beta. Die aktive Steuerung kann die NOAH-Ausgangsleistung
> verändern und sollte während der Testphase überwacht werden.

## Ziele

- Netzbezug reduzieren
- unnötige PV-Einspeisung bei noch aufnahmefähigem Speicher reduzieren
- Akku bis zum Abend auf einen konfigurierbaren Ziel-SOC laden
- Nachtentladung bis zu einem Mindest-SOC ermöglichen
- Forecast.Solar in die Ladeplanung einbeziehen
- Regelzustand, Prognose und Energiefluss in einem Dashboard darstellen

## HACS-Integration

Eine HACS-kompatible Custom Integration ist als Beta verfügbar.

Aktuelle Beta:

```text
2.0.0-beta.6
```

Ab Beta 5 kann die Integration den berechneten Sollwert optional aktiv an
`NOAH System Output Power` übertragen.

Ab Beta 6 wird zusätzlich ein eigenes Lovelace-Dashboard erzeugt.

## Voraussetzungen

- Home Assistant
- HACS
- MQTT
- Noah-MQTT
- Forecast.Solar
- Sun-Integration
- saldierter Netzleistungssensor
- beschreibbare `number`-Entität für NOAH System Output Power

Für das erweiterte Dashboard zusätzlich:

- Power Flow Card Plus
- ApexCharts Card

Die beiden Custom Cards werden nicht automatisch installiert. Der Optimizer
selbst funktioniert auch ohne sie.

## Installation über HACS

Falls das Repository noch nicht in der regulären HACS-Suche verfügbar ist,
als benutzerdefiniertes Repository hinzufügen:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

Danach **Growatt NOAH Optimizer** installieren und Home Assistant neu starten.

Die vollständige Anleitung steht unter:

- [Installation](docs/installation.md)
- [Konfiguration](docs/configuration.md)
- [Fehlerbehebung](docs/troubleshooting.md)
- [HACS Beta](docs/hacs-beta.md)

## Benötigte Quell-Entitäten

Beim Einrichten werden ausgewählt:

- saldierte Netzleistung
- NOAH Solar Power
- NOAH Output Power
- NOAH SOC
- NOAH Charging Power
- NOAH Discharge Power
- Forecast.Solar Restprognose heute
- NOAH System Output Power

Unterstützte Einheiten:

```text
Leistung: W oder kW
Energie:  Wh oder kWh
SOC:      %
```

Die erwartete Netzkonvention lautet:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Bei umgekehrter Konvention kann während der Einrichtung
**Netzvorzeichen umkehren** aktiviert werden.

## Aktive Steuerung

Die Integration besitzt zwei getrennte Schalter:

```text
Optimierer-Berechnung aktiv
NOAH-Steuerung aktiv
```

Die aktive NOAH-Steuerung ist standardmäßig ausgeschaltet.

Der Controller enthält unter anderem:

- Schalt-Hysterese
- Mindestabstand zwischen normalen Stellbefehlen
- Wiederholungsversuch bei nicht übernommenem Sollwert
- Failsafe bei längerem Verlust kritischer Daten
- persistente Home-Assistant-Benachrichtigung
- Sperre gegen den alten YAML-Controller

Der alte YAML-Optimizer und die HACS-Steuerung dürfen niemals gleichzeitig
denselben NOAH aktiv regeln.

## Dashboard ab Beta 6

Beta 6 erzeugt beim ersten Start ein eigenes Lovelace-Dashboard mit dem
Seitenleisteneintrag:

```text
NOAH Optimizer
```

Bei einer Neuinstallation kann im Einrichtungsdialog gewählt werden, ob der
Eintrag in der Seitenleiste erscheinen soll. Standard ist **Ein**.

Bei einem Update von Beta 5 auf Beta 6 existiert diese Einstellung noch nicht;
in diesem Fall wird ebenfalls **Ein** verwendet.

Die Integration löst ihre eigenen Entity-IDs über die Home-Assistant
Entity Registry auf. Bereichspräfixe oder vom Benutzer geänderte Entity-IDs
müssen deshalb nicht in einer Dashboard-Datei fest eingetragen werden.

Die Standardsprache des Dashboards richtet sich bei der erstmaligen Erzeugung
nach der Home-Assistant-Sprache:

- Deutsch → `dashboard_de.yaml`
- alle anderen Sprachen → `dashboard_en.yaml`

Spätere Benutzeränderungen am Dashboard werden nicht überschrieben.

### Dashboard-Inhalt

- aktueller Energiefluss
- Netzbezug und Netzeinspeisung getrennt
- Laden und Entladen des NOAH getrennt
- Akkustand und Prognosedeckung
- Reglermodus und Controllerstatus
- letzter Stellwert und letzter Stellbefehl
- Energieplanung bis Sonnenuntergang
- Leistung heute
- Reglerverhalten
- Planung im Detail
- Kalibrierparameter
- Diagnose

## Legacy-YAML-Optimizer

Die ältere Package-Variante bleibt im Repository enthalten.

Dateien:

```text
noah_optimizer.yaml
dashboards/noah_dashboard.yaml
```

Für neue Installationen wird die HACS-Integration empfohlen.

Die Legacy-YAML-Regelung muss ausgeschaltet sein, bevor die aktive
HACS-Steuerung eingeschaltet wird.

## Sicherheit

Dieses Projekt ist ein Community-Projekt und keine offizielle Growatt-
Integration.

Die aktive Steuerung sollte erst eingeschaltet werden, nachdem:

- alle Quellwerte plausibel geprüft wurden
- das Netzvorzeichen stimmt
- Forecast.Solar plausible Werte liefert
- NOAH System Output Power manuell beschreibbar ist
- der berechnete Ausgangssollwert plausibel ist

## Lizenz

Siehe [LICENSE](LICENSE) und [THIRD_PARTY.md](THIRD_PARTY.md).

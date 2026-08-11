# Installation

Diese Anleitung beschreibt die Installation und das Update des **Home
Assistant Growatt NOAH Optimizers** für Version `2.0.0-beta.11`.

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

## 5. Beta 11 installieren

Zu installierende Version:

```text
2.0.0-beta.11
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

## 7. Update auf Beta 11

Vor dem Update:

```text
NOAH-Steuerung aktiv = Aus
Dynamische SOC-Steuerung aktiv = Aus
Vorausschauende SOC-Freigabe aktiv = Aus
```

Bei einem Update von Beta 10 existiert der letzte Schalter noch nicht. Er wird
mit Beta 11 neu angelegt und ist standardmäßig ausgeschaltet.

Danach Beta 11 über HACS installieren und Home Assistant vollständig neu starten.

### Update von Beta 10

Beta 11 übernimmt alle vorhandenen Einstellungen und Entitäten.

Neu hinzu kommen:

```text
Vorausschauende SOC-Freigabe aktiv
Prognosebasierter Mindest-SOC
SOC-Freigabegrenze
Freigebare Akkuenergie
SOC-Freigabe-Soll
```

Außerdem steht der neue Reglermodus zur Verfügung:

```text
SOC-Freigabe
```

Die Funktion ist nach dem Update **nicht automatisch aktiv**.

### Update von Beta 9 oder älter

Beim direkten Update auf Beta 11 bleiben die bisherigen Dashboard-Migrationen
erhalten. Die Integration ergänzt fehlende Beta-8-Dynamic-SOC-Elemente,
repariert gegebenenfalls den Beta-8-Jinja-Fehler und führt anschließend die
Beta-11-Erweiterung aus.

## 8. Dashboard und Migration

Beta 11 ergänzt neue Dashboard-Entitäten und einen neuen Schalter. Deshalb
wird die Dashboard-Template-Version erhöht auf:

```text
Dashboard-Template-Version = 10
```

Bei einem bestehenden Dashboard werden gezielt ergänzt:

- Vorausschauende SOC-Freigabe aktiv
- Prognosebasierter Mindest-SOC
- SOC-Freigabegrenze
- Freigebare Akkuenergie
- SOC-Freigabe-Soll
- Reglermodus `SOC-Freigabe` in der Statuskarte

Ältere Migrationen bleiben ebenfalls aktiv:

- Beta-6-Batteriezuordnung korrigieren, wenn sie noch exakt unverändert vorliegt
- Beta-8-Dynamic-SOC-Elemente ergänzen, falls sie fehlen
- SOC-Planungsdiagramm ergänzen, falls es fehlt
- fehlerhaften Beta-8-Jinja-Ausdruck reparieren

Das Dashboard wird **nicht vollständig ersetzt**. Eigene Anpassungen bleiben
bestehen, soweit die bekannten Standardkarten eindeutig erkannt werden.

Bei einer Neuinstallation wird direkt die vollständige Beta-11-Vorlage mit
Dashboard-Template-Version 10 erzeugt.

## 9. Erste Prüfung nach dem Update

Zunächst:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Aus
Dynamische SOC-Steuerung aktiv = Aus
Vorausschauende SOC-Freigabe aktiv = Aus
Betriebsart = Automatik
```

Im Dashboard beziehungsweise unter **Werkzeuge → Zustände** prüfen:

```text
Datenstatus
Dynamisches SOC-Soll
SOC-Abweichung
SOC-Ladeplan
Dynamisch erforderliche Ladeleistung
Prognosebasierter Mindest-SOC
SOC-Freigabegrenze
Freigebare Akkuenergie
SOC-Freigabe-Soll
```

Alle neuen Diagnosewerte werden auch bei ausgeschalteter SOC-Freigabe
berechnet. Es wird noch kein Stellbefehl an den NOAH gesendet.

## 10. Dynamischen SOC-Ladeplan prüfen

Die Beta-10-Ladeplankurve bleibt unverändert.

Bei Mindest-SOC `10 %` und Ziel-SOC `100 %` liegt das reine Zeit-Soll ungefähr
bei:

```text
Sonnenaufgang    10 %
25 % des Tages   32,5 %
50 % des Tages   55 %
75 % des Tages   77,5 %
Sonnenuntergang 100 %
```

Eine knappe Restprognose darf diese Kurve progressiv nach oben ziehen, soll sie
aber morgens nicht allein deshalb sofort auf `100 %` setzen.

## 11. SOC-Freigabewerte plausibilisieren

Die neuen Werte beantworten drei verschiedene Fragen:

```text
Prognosebasierter Mindest-SOC
= Welchen SOC muss der Akku nach aktueller Prognose mindestens schon haben,
  damit der Ziel-SOC bis Sonnenuntergang noch erreichbar ist?

SOC-Freigabegrenze
= Bis zu welchem SOC darf die neue Freigabe maximal entladen?

Freigebare Akkuenergie
= Wie viel Batterieenergie liegt aktuell oberhalb dieser Grenze?
```

Die Freigabegrenze wird aus dem größeren Wert von dynamischem SOC-Soll und
prognosebasiertem Mindest-SOC plus 2 Prozentpunkten Sicherheitsreserve gebildet.

Beispiel:

```text
Ist-SOC:                         92 %
Dynamisches SOC-Soll:            70 %
Prognosebasierter Mindest-SOC:   76 %
SOC-Freigabegrenze:              78 %
```

Dann dürfen rechnerisch maximal `14` SOC-Prozentpunkte als Vorsprung genutzt
werden.

Ist dagegen:

```text
Prognosebasierter Mindest-SOC:   96 %
SOC-Freigabegrenze:              98 %
Ist-SOC:                         98 %
```

vorhanden, ist keine Akkuenergie freigebbar. Die aktuelle Prognose lässt dann
keine sichere zusätzliche Entladung zu.

Wichtig: Diese Grenze ist **prognosebasiert**. Sie verhindert eine absichtliche
Entladung unter den aktuell berechneten Bedarf, kann aber keine absolute
Garantie geben, wenn PV-Ertrag oder Hausverbrauch später deutlich von der
Prognose abweichen.

## 12. Dynamische SOC-Steuerung aktivieren

Erst nach plausibler Beobachtung:

```text
Dynamische SOC-Steuerung aktiv = Ein
Vorausschauende SOC-Freigabe aktiv = Aus
NOAH-Steuerung aktiv = Aus
```

Dadurch kann bereits geprüft werden, ob der berechnete Reglermodus bei einem
SOC-Rückstand auf:

```text
SOC-Nachladung
```

wechselt und wie sich der berechnete Ausgangssollwert ändert. Wegen der noch
ausgeschalteten NOAH-Steuerung wird der Sollwert nicht geschrieben.

## 13. Vorausschauende SOC-Freigabe testen

Anschließend:

```text
Dynamische SOC-Steuerung aktiv = Ein
Vorausschauende SOC-Freigabe aktiv = Ein
NOAH-Steuerung aktiv = Aus
Betriebsart = Automatik
```

Der Reglermodus **SOC-Freigabe** kann jetzt erscheinen, wenn:

- Forecast.Solar verfügbar ist
- es Tag ist
- der Ist-SOC über der SOC-Freigabegrenze liegt
- freigebare Akkuenergie vorhanden ist
- aktuell positiver Netzbezug vorliegt

Der berechnete **SOC-Freigabe-Sollwert** entspricht näherungsweise:

```text
aktuelle NOAH-Ausgangsleistung + aktueller Netzbezug
```

begrenzt durch die maximale Ausgangsleistung.

Der endgültige Ausgangssollwert wird weiterhin auf das konfigurierte
Stellgrößenraster gerundet. Ziel ist ein möglichst kleiner Netzbezug; eine
absichtliche Batterieeinspeisung ins Netz wird nicht angefordert. Kleine
kurzzeitige Abweichungen um 0 W können durch Messverzögerung, Lastsprünge und
das Stellgrößenraster entstehen.

## 14. SOC-Nachholzeit einstellen

Standard:

```text
2,0 h
```

Ein kleinerer Wert reagiert stärker auf einen SOC-Rückstand. Ein größerer Wert
verteilt das Nachladen über einen längeren Zeitraum.

Die Nachholzeit wirkt auf **SOC-Nachladung**, nicht direkt auf die neue
SOC-Freigabe.

## 15. Stellgröße manuell testen

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

## 16. Aktive NOAH-Steuerung einschalten

Erst wenn Ladeplan und SOC-Freigabewerte plausibel sind:

```text
Optimierer-Berechnung aktiv = Ein
Dynamische SOC-Steuerung aktiv = Ein
Vorausschauende SOC-Freigabe aktiv = Ein
NOAH-Steuerung aktiv = Ein
Betriebsart = Automatik
```

Wenn die SOC-Freigabe noch nicht aktiv eingesetzt werden soll, kann ihr eigener
Schalter auf **Aus** bleiben.

## 17. Schutzmechanismen

Die aktive Steuerung enthält weiterhin:

- Schalt-Hysterese
- Stellgrößenraster
- Mindestabstand zwischen normalen Stellbefehlen
- Wiederholungsversuch
- 10-Minuten-Failsafe bei dauerhaft fehlenden kritischen Daten
- persistente Home-Assistant-Benachrichtigung
- Sperre gegen den Legacy-YAML-Controller

Zusätzlich schützt Beta 11 die SOC-Freigabe durch:

- dynamisches SOC-Soll
- prognosebasierten Mindest-SOC
- 2 Prozentpunkte SOC-Sicherheitsreserve
- Freigabe nur bei positivem Netzbezug
- Freigabe nur am Tag
- sofortige Sollwertreduzierung, wenn ein zuvor gesetzter SOC-Freigabe-Sollwert aus Sicherheitsgründen sinken muss

## 18. Legacy-YAML-Optimizer

Der ältere YAML-Optimizer darf nicht gleichzeitig mit der aktiven
HACS-Steuerung denselben NOAH regeln.

Die HACS-Integration prüft:

```text
input_boolean.noah_optimizer_enabled
```

Steht dieser Helfer auf `on`, werden normale HACS-Stellbefehle blockiert.

Die dynamische SOC-Regelung und die vorausschauende SOC-Freigabe werden nicht
in die Legacy-YAML-Regelung zurückportiert.

## 19. Weiterführende Dokumentation

- [Konfiguration](configuration.md)
- [Fehlerbehebung](troubleshooting.md)
- [HACS Beta](hacs-beta.md)

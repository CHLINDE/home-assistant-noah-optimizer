# Installation

Diese Anleitung beschreibt die Installation des **Home Assistant Growatt NOAH Optimizers** mit der mitgelieferten Package-Datei und dem Dashboard.

## 1. Voraussetzungen

Erforderlich sind:

- Home Assistant mit Zugriff auf `/config`
- ein funktionsfähiger MQTT-Broker
- eine laufende Noah-MQTT-Anbindung für den Growatt NOAH
- Forecast.Solar in Home Assistant
- ein saldierter Netzleistungssensor in Watt
- die Möglichkeit, `System Output Power` des NOAH über eine `number`-Entität zu setzen

Für das mitgelieferte Dashboard werden zusätzlich benötigt:

- Power Flow Card Plus
- ApexCharts Card

Die beiden benutzerdefinierten Karten können über HACS installiert werden.

## 2. Erforderliche Home-Assistant-Komponenten

Vor der Installation des Optimierers müssen die folgenden Komponenten eingerichtet sein:

| Komponente | Zweck | Installation / Dokumentation |
|---|---|---|
| [MQTT](https://www.home-assistant.io/integrations/mqtt/) | Überträgt Messwerte und Stellgrößen zwischen Noah-MQTT und Home Assistant. | Als Home-Assistant-Integration einrichten. Bei Home Assistant OS kann beispielsweise der Mosquitto Broker als Add-on verwendet werden. |
| [Mosquitto Broker](https://github.com/home-assistant/addons/tree/master/mosquitto) | Optionaler MQTT-Broker für Home Assistant OS. | Über **Einstellungen → Add-ons → Add-on-Store** installieren. Ein externer MQTT-Broker kann ebenfalls verwendet werden. |
| [Noah-MQTT](https://github.com/mtrossbach/noah-mqtt) | Liest die Growatt-NOAH-Daten aus und stellt Sensoren sowie die Stellgröße `System Output Power` über MQTT Discovery bereit. | Noah-MQTT entsprechend der Projektanleitung installieren und mit dem MQTT-Broker verbinden. |
| [Forecast.Solar](https://www.home-assistant.io/integrations/forecast_solar/) | Liefert die PV-Ertragsprognose und die verbleibende Energieproduktion des aktuellen Tages. | Über **Einstellungen → Geräte & Dienste → Integration hinzufügen** einrichten. |
| [Sun](https://www.home-assistant.io/integrations/sun/) | Liefert Sonnenstand, Sonnenhöhe und Sonnenuntergang für Tages- und Nachtbetrieb. | Ist in Home Assistant normalerweise standardmäßig vorhanden. |
| [HACS](https://www.hacs.xyz/) | Wird für die Installation der benutzerdefinierten Dashboardkarten benötigt. | Nach der offiziellen HACS-Anleitung installieren und anschließend als Integration hinzufügen. |
| [Power Flow Card Plus](https://github.com/flixlix/power-flow-card-plus) | Stellt den aktuellen Energiefluss zwischen PV, Netz, Haus und Akku dar. | In HACS unter **Frontend** beziehungsweise **Dashboard** suchen und installieren. |
| [ApexCharts Card](https://github.com/RomRider/apexcharts-card) | Stellt Leistungs-, SOC- und Prognoseverläufe im Dashboard dar. | In HACS unter **Frontend** beziehungsweise **Dashboard** suchen und installieren. |

### Mindestanforderungen für die Regelung

Für die eigentliche Regelung werden benötigt:

```text
MQTT-Broker
MQTT-Integration
Noah-MQTT
Forecast.Solar
Sun-Integration
saldierter Netzleistungssensor
```

HACS, Power Flow Card Plus und ApexCharts Card sind nur für das mitgelieferte Dashboard erforderlich. Der Optimierer selbst funktioniert auch ohne diese drei Komponenten.

### Komponenten vor der Installation prüfen

Unter **Einstellungen → Geräte & Dienste** sollten mindestens folgende Integrationen ohne Fehler angezeigt werden:

```text
MQTT
Forecast.Solar
Sun
```

Unter **Einstellungen → Geräte & Dienste → MQTT → Geräte** sollte außerdem das NOAH-Gerät mit seinen Sensoren und der verstellbaren Entität **System Output Power** vorhanden sein.

## 3. Benötigte Entitäten ermitteln

Vor der Installation müssen folgende Entitäten in Home Assistant vorhanden sein:

| Funktion | Erwarteter Entitätstyp | Einheit |
|---|---|---:|
| Saldierte Netzleistung | `sensor` | W |
| NOAH Solar Power | `sensor` | W |
| NOAH Output Power | `sensor` | W |
| NOAH SOC | `sensor` | % |
| NOAH Charging Power | `sensor` | W |
| NOAH Discharge Power | `sensor` | W |
| Forecast.Solar Restprognose heute | `sensor` | kWh |
| NOAH System Output Power | `number` | W |

Die Entity-IDs findest du unter:

**Entwicklerwerkzeuge → Zustände**

Die Netzleistung muss folgende Vorzeichenkonvention verwenden:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Ist die Richtung umgekehrt, kann sie später über den Helfer **NOAH Netzvorzeichen umkehren** korrigiert werden.

## 4. Package-Unterstützung aktivieren

Öffne `/config/configuration.yaml`.

Wenn noch kein `homeassistant:`-Abschnitt vorhanden ist, ergänze:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Wenn bereits ein `homeassistant:`-Abschnitt existiert, ergänze nur die Zeile `packages:` darin:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Lege anschließend den Ordner an:

```text
/config/packages
```

## 5. Optimierer-Datei kopieren

Kopiere die veröffentlichte Datei:

```text
noah_optimizer.yaml
```

nach:

```text
/config/packages/noah_optimizer.yaml
```

## 6. Entity-Platzhalter ersetzen

Öffne `/config/packages/noah_optimizer.yaml` und ersetze alle Platzhalter:

```yaml
sensor.dein_netzleistungssensor
sensor.dein_noah_solar_power
sensor.dein_noah_output_power
sensor.dein_noah_soc
sensor.dein_noah_charging_power
sensor.dein_noah_discharge_power
sensor.deine_forecast_solar_restprognose
number.dein_noah_system_output_power
```

Beispiel:

```yaml
sensor.dein_noah_soc
```

wird zu:

```yaml
sensor.DEINE_GERAETE_ID_soc
```

Achte darauf, jede Entity-ID an allen Stellen vollständig zu ersetzen.

## 7. YAML-Konfiguration prüfen

Öffne:

**Entwicklerwerkzeuge → YAML → Konfiguration prüfen**

Behebe alle gemeldeten Fehler, bevor Home Assistant neu gestartet wird.

Warnungen des Editors zu den neu erzeugten `sensor.noah_opt_...`-Entitäten können vor dem ersten Neustart auftreten, weil diese Entitäten zu diesem Zeitpunkt noch nicht existieren.

## 8. Home Assistant neu starten

Starte Home Assistant vollständig neu.

Danach sollten unter **Entwicklerwerkzeuge → Zustände** unter anderem folgende Entitäten existieren:

```text
sensor.noah_opt_netzleistung
sensor.noah_opt_pv_leistung
sensor.noah_opt_ausgangsleistung
sensor.noah_opt_soc
sensor.noah_opt_ladeleistung
sensor.noah_opt_entladeleistung
sensor.noah_opt_hauslast
sensor.noah_opt_ausgangssollwert
sensor.noah_opt_reglermodus
sensor.noah_opt_datenstatus
binary_sensor.noah_opt_kritische_daten_ok
```

Erwartet werden:

```text
sensor.noah_opt_datenstatus = OK
binary_sensor.noah_opt_kritische_daten_ok = on
```

## 9. Grundeinstellungen setzen

Nach dem ersten Neustart müssen die Helfer kontrolliert und sinnvoll eingestellt werden.

Empfohlene Startwerte:

| Einstellung | Startwert |
|---|---:|
| Nutzbare Akkukapazität | 2,048 kWh je NOAH-Modul |
| Ziel-SOC bei Sonnenuntergang | 95 % |
| Mindest-SOC | 10 % |
| Ladewirkungsgrad | 0,90 |
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

Bei mehreren NOAH-Modulen muss die gesamte nutzbare Akkukapazität eingetragen werden.

Beispiel für zwei Module:

```text
2 × 2,048 kWh = 4,096 kWh
```

## 10. Messwerte prüfen

### Netzrichtung

Bei einem größeren Verbraucher muss `sensor.noah_opt_netzleistung` positiv werden.

Bei PV-Überschuss muss der Wert negativ werden.

Ist das umgekehrt, aktiviere:

```text
input_boolean.noah_grid_sign_inverted
```

### Leistungsbilanz

Ungefähr muss gelten:

```text
Hauslast = Netzleistung + NOAH-Ausgangsleistung
```

Beispiel:

```text
300 W Netzbezug + 200 W NOAH-Ausgang = 500 W Hauslast
```

Kleine Abweichungen durch unterschiedliche Aktualisierungszeitpunkte sind normal.

## 11. Schreibzugriff testen

Der Optimierer bleibt zunächst ausgeschaltet.

Öffne:

**Entwicklerwerkzeuge → Aktionen**

Führe testweise aus:

```yaml
action: number.set_value
target:
  entity_id: number.dein_noah_system_output_power
data:
  value: 300
```

Ersetze die Entity-ID durch deine tatsächliche Stellgröße.

Prüfe anschließend:

```text
number.dein_noah_system_output_power = 300
```

Die gemessene NOAH-Ausgangsleistung kann verzögert folgen. Bei vollem Akku und vorhandener Solarleistung kann der tatsächliche Ausgang vorübergehend über dem Sollwert liegen.

## 12. Automations-Test

Stelle ein:

```text
NOAH Betriebsart = Manuell
NOAH manuelle Ausgangsleistung = 300 W
NOAH Optimierer aktiv = Ein
```

Der Regler läuft nach der mitgelieferten Konfiguration alle fünf Minuten.

Kontrolliere anschließend:

```text
sensor.noah_opt_reglermodus = Manuell
sensor.noah_opt_ausgangssollwert = 300 W
input_number.noah_last_target_w = 300 W
number.dein_noah_system_output_power = 300 W
```

Teste danach beispielsweise 500 W.

Wenn beide Werte übernommen werden, schalte den Optimierer wieder aus und stelle die Betriebsart auf **Automatik**.

## 13. Dashboard installieren

Installiere über HACS:

- Power Flow Card Plus
- ApexCharts Card

Lade den Browser danach vollständig neu.

## 14. Dashboard importieren

Öffne die Datei:

```text
dashboards/noah_dashboard.yaml
```

Ersetze darin:

```yaml
number.dein_noah_system_output_power
```

durch deine tatsächliche Stellgrößen-Entität.

Dann:

1. **Einstellungen → Dashboards**
2. Neues Dashboard anlegen
3. Dashboard öffnen
4. **Dashboard bearbeiten**
5. Drei-Punkte-Menü öffnen
6. **Rohkonfigurationseditor**
7. Inhalt von `noah_dashboard.yaml` einfügen
8. Speichern

Falls `Custom element doesn't exist` erscheint, fehlen die HACS-Karten oder der Browser-Cache wurde noch nicht aktualisiert.

## 15. Automatik aktivieren

Vor der Freigabe müssen folgende Werte plausibel sein:

```text
Datenstatus = OK
kritische Daten OK = on
Netzvorzeichen korrekt
SOC plausibel
PV-Leistung plausibel
Ausgangsleistung plausibel
Restprognose plausibel
berechneter Ausgangssollwert plausibel
```

Danach:

```text
NOAH Betriebsart = Automatik
NOAH Optimierer aktiv = Ein
```

Beobachte mindestens die ersten zwei Regelzyklen.

## Sicherheitshinweis

Das Projekt steuert aktiv die Ausgangsleistung des Speichers. Die Noah-MQTT-Anbindung und die verwendete Growatt-Schnittstelle sind keine offizielle lokale Growatt-Steuerung. Die Nutzung erfolgt auf eigene Verantwortung.

Der Optimierer sollte erst aktiviert werden, nachdem Messwerte, Vorzeichen und Schreibzugriff manuell geprüft wurden.

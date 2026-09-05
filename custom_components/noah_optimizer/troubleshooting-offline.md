# NOAH-Offline-Erkennung – Fehlerbehebung

## Home Assistant meldet „NOAH Optimizer: NOAH offline“

Prüfe zuerst direkt am Growatt NOAH:

1. Ist das Gerät eingeschaltet?
2. Ist die IoT-/WLAN-Anzeige aktiv?
3. Falls nötig, die **IoT-Taste** bzw. WLAN-Kopplung des NOAH prüfen.
4. In ShinePhone kontrollieren, ob der NOAH wieder als `Online` angezeigt wird.
5. In Home Assistant beim Noah-MQTT-Gerät den Binary-Sensor
   **Connectivity** prüfen.

Während des echten Offline-Zustands blockiert der Optimizer bewusst alle
Stellbefehle.

## Datenstatus zeigt „Stellgröße nicht verfügbar“, Connectivity ist aber `on`

Unter `2.1.0-beta.10` kann dies durch die fehlerhafte 3-Minuten-Prüfung von
`Connectivity.last_reported` verursacht werden.

Home Assistant MQTT-Entitäten schreiben bei erneut empfangenen identischen
Payloads nicht zwingend einen neuen Entity-State. Deshalb konnte
`last_reported` altern, obwohl Noah-MQTT weiterhin aktuelle Daten erhielt.

Lösung:

```text
Auf 2.1.0-beta.11 oder neuer aktualisieren.
```

Beta 11 verwendet für die Online-/Offline-Entscheidung keinen
`last_reported`-Timeout mehr.

## Datenstatus zeigt „Stellgröße nicht verfügbar“ und Connectivity ist `off`

Das ist beabsichtigt. Die Noah-MQTT-Leistungswerte können weiterhin als
zuletzt bekannte/gecachte Werte vorhanden sein. Solange Connectivity `off`,
`unknown` oder `unavailable` meldet, werden sie nicht als aktuelle NOAH-Daten
verwendet.

## Connectivity bleibt `on`, obwohl Noah-MQTT selbst keine Daten mehr erhält

Beta 11 setzt einen vorhandenen Connectivity-Sensor mit Zustand `on` nicht
allein aufgrund eines alten Home-Assistant-Zeitstempels auf offline.

Grund: `last_reported` ist bei MQTT-Entitäten kein verlässlicher Indikator
dafür, wann die letzte identische MQTT-Nachricht eingegangen ist.

Wenn Noah-MQTT selbst hängt oder beendet wurde, Noah-MQTT beziehungsweise den
MQTT-Broker separat überwachen.

## Keine Connectivity-Entität vorhanden

Dann arbeitet die Integration aus Kompatibilitätsgründen mit der bisherigen
Regelung weiter und schreibt eine Warnung in das Home-Assistant-Protokoll.

Aktualisiere Noah-MQTT auf eine Version, die den Connectivity-Binary-Sensor
bereitstellt.

## PV-Energie steigt während Offline nicht weiter

Das ist beabsichtigt. Solange der NOAH tatsächlich offline ist, werden
Noah-MQTT-Quellwerte nicht erneut in die Optimizer-Berechnung und das
PV-Learning übernommen. Dadurch kann ein gecachter letzter PV-Leistungswert
nicht als reale weitere Produktion integriert werden.

Nach der Wiederverbindung wird die Messlücke vom PV-Learning bewertet. Eine
lange Tageslücke verwirft den Lerntag gemäß der bestehenden Lernlogik.

## NOAH ist wieder online

Ab Beta 11 reicht `Connectivity = on` zur Wiederfreigabe der Offline-Sperre.

Die in Beta 10 verwendete zusätzliche Prüfung über
`System Output Power.last_reported` wurde entfernt, weil auch ein
unveränderter MQTT-Number-Wert nicht zwingend zu einem neuen Entity-State in
Home Assistant führt.

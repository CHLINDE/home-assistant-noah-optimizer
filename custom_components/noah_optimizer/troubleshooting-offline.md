# NOAH-Offline-Erkennung – Fehlerbehebung

## Home Assistant meldet „NOAH Optimizer: NOAH offline“

Prüfe zuerst direkt am Growatt NOAH:

1. Ist das Gerät eingeschaltet?
2. Ist die IoT-/WLAN-Anzeige aktiv?
3. Falls nötig, die **IoT-Taste** bzw. WLAN-Kopplung des NOAH prüfen.
4. In ShinePhone kontrollieren, ob der NOAH wieder als `Online` angezeigt wird.
5. In Home Assistant beim Noah-MQTT-Gerät den Binary-Sensor
   **Connectivity** prüfen.

Während des Offline-Zustands blockiert der Optimizer bewusst alle
Stellbefehle.

## Datenstatus zeigt „Stellgröße nicht verfügbar“

Das ist bei einem erkannten NOAH-Offline-Zustand beabsichtigt. Die
Noah-MQTT-Leistungswerte können weiterhin als zuletzt bekannte/gecachte Werte
vorhanden sein. Sie werden dann nicht mehr als Beleg für eine funktionierende
NOAH-Verbindung verwendet.

## Connectivity bleibt `on`, obwohl keine Daten mehr kommen

Beta 10 prüft zusätzlich den Zeitpunkt der letzten Statusmeldung. Wird ein
`on`-Zustand länger als drei Minuten nicht neu gemeldet, wird der NOAH
vorsorglich als offline behandelt.

Prüfe in diesem Fall auch Noah-MQTT selbst.

## Keine Connectivity-Entität vorhanden

Dann arbeitet Beta 10 aus Kompatibilitätsgründen mit der bisherigen Regelung
weiter und schreibt eine Warnung in das Home-Assistant-Protokoll.

Aktualisiere Noah-MQTT auf eine Version, die den Connectivity-Binary-Sensor
bereitstellt.

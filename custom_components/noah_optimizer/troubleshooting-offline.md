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

## PV-Energie steigt während Offline nicht weiter

Das ist ab Beta 10 beabsichtigt. Solange der NOAH offline ist, werden
Noah-MQTT-Quellwerte nicht erneut in die Optimizer-Berechnung und das
PV-Learning übernommen. Dadurch kann ein gecachter letzter PV-Leistungswert
nicht als reale weitere Produktion integriert werden.

Nach der Wiederverbindung wird die Messlücke vom PV-Learning bewertet. Eine
lange Tageslücke verwirft den Lerntag gemäß der bestehenden Lernlogik.

## NOAH ist wieder online, die Warnung bleibt aber kurz bestehen

Das kann nach `2.1.0-beta.10` beabsichtigt sein.

`Connectivity` und **System Output Power** werden von Noah-MQTT über
unterschiedliche MQTT-State-Topics veröffentlicht. Nach einem erkannten
Offline-Zustand wartet der Optimizer daher zusätzlich auf eine frische Meldung
von **System Output Power**, bevor die aktive Regelung wieder freigegeben wird.

Bei der Noah-MQTT-Standardkonfiguration werden Parameterdaten regelmäßig
abgefragt; die Wiederfreigabe kann deshalb etwas später erfolgen als die reine
Connectivity-Anzeige.

Bleibt die Warnung dauerhaft bestehen:

1. Prüfen, ob **System Output Power** in Home Assistant wieder aktualisiert wird.
2. Noah-MQTT-Protokoll auf Fehler beim Parameterabruf prüfen.
3. Erst danach Noah-MQTT beziehungsweise die Integration neu laden.


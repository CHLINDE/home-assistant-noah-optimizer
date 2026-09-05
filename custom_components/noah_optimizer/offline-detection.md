# NOAH-Offline-Erkennung

Ab `2.1.0-beta.10` überwacht der NOAH Optimizer den von Noah-MQTT
bereitgestellten **Connectivity**-Binary-Sensor des konfigurierten NOAH.

`2.1.0-beta.11` korrigiert dabei die Auswertung der Home-Assistant-Zeitstempel:
`last_reported` wird nicht mehr als MQTT-Nachrichten-Freshness verwendet.

Die Zuordnung erfolgt automatisch über dasselbe Home-Assistant-Gerät wie die
konfigurierte Entität **NOAH System Output Power**. Eine zusätzliche Auswahl
im Config Flow ist nicht erforderlich.

## Offline-Bedingungen

Der NOAH wird als nicht erreichbar behandelt, wenn:

- `Connectivity` den Zustand `off` meldet,
- der Zustand `unknown` oder `unavailable` ist oder
- eine zuvor erkannte Connectivity-Entität verschwindet.

Ein vorhandener Connectivity-Sensor mit Zustand `on` gilt als online.

### Warum keine 3-Minuten-Zeitstempelprüfung mehr verwendet wird

Beta 10 verwendete `State.last_reported`, um einen unverändert auf `on`
stehenden Connectivity-Sensor nach drei Minuten als veraltet zu behandeln.

Das ist für MQTT-Entitäten nicht zuverlässig: Home Assistant muss bei einem
erneut empfangenen identischen MQTT-Payload keinen neuen Entity-State
schreiben. Ein alter `last_reported`-Zeitstempel bedeutet deshalb nicht
automatisch, dass Noah-MQTT keine aktuellen MQTT-Daten mehr erhält.

Dasselbe gilt für einen unveränderten numerischen Wert von
**System Output Power**. Deshalb verwendet Beta 11 auch dort keine
`last_reported`-Wiederfreigabeprüfung mehr.

## Verhalten bei Offline

Während der NOAH offline ist:

- werden **keine Stellbefehle** gesendet,
- wird auch kein 0-W-Failsafe-Befehl gesendet,
- wird ein laufender Failsafe-Zähler zurückgesetzt,
- wird `Datenstatus` auf **Stellgröße nicht verfügbar** gesetzt,
- wird `Controllerstatus` auf **Stellgröße nicht verfügbar** gesetzt,
- erscheint einmalig die persistente Home-Assistant-Benachrichtigung
  **NOAH Optimizer: NOAH offline**.

Damit können gecachte Noah-MQTT-Werte nicht zu
`Datenstatus: OK / Controller: Synchron` führen, während der Connectivity-
Sensor tatsächlich einen Offline-Zustand meldet.

## Wiederverbindung

Sobald der Noah-MQTT-Connectivity-Sensor wieder `on` meldet:

- wird die Offline-Sperre aufgehoben,
- wird die Offline-Benachrichtigung entfernt,
- werden die aktuellen Quellwerte wieder verarbeitet und
- die bestehende Regellogik darf wieder Stellbefehle senden.

Eine zusätzliche Prüfung von `System Output Power.last_reported` findet ab
Beta 11 nicht mehr statt.

## Kompatibilität

Falls bei einer älteren Noah-MQTT-Version noch keine Connectivity-Entität
existiert, wird die aktive Regelung nicht unerwartet abgeschaltet. Stattdessen
wird einmalig eine Warnung in das Home-Assistant-Protokoll geschrieben.

Für die Offline-Erkennung wird eine aktuelle Noah-MQTT-Version empfohlen.

## Gecachte Messwerte und PV-Learning

Während der NOAH tatsächlich offline ist, wird der Coordinator bewusst
**nicht** erneut aus den Noah-MQTT-Quellentitäten aktualisiert. Noah-MQTT kann
die zuletzt bekannten Werte für PV-Leistung und SOC weiterhin anzeigen, obwohl
das physische Gerät nicht erreichbar ist.

Das ist besonders für das PV-Learning wichtig: Die PV-Energie wird aus der
Leistung über die vergangene Zeit integriert. Würde ein gecachter letzter
PV-Leistungswert während der Offline-Zeit wiederholt verarbeitet, entstünde
fiktive PV-Produktion.

Nach Wiederherstellung der Verbindung wird die ausgelassene Zeit von der
bestehenden Lernlogik als normale Messlücke behandelt. Eine längere Tageslücke
verwirft den Lerntag dadurch korrekt, anstatt den Lernfaktor mit falscher
PV-Energie zu verfälschen.

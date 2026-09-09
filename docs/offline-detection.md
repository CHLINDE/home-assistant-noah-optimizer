# NOAH-Offline-Erkennung

Ab `2.1.0-beta.10` überwacht der NOAH Optimizer den von Noah-MQTT
bereitgestellten **Connectivity**-Binary-Sensor des konfigurierten NOAH.

`2.1.0-beta.11` korrigierte die fehlerhafte Verwendung von
`last_reported` als MQTT-Freshness-Signal. `2.1.0-beta.12` unterscheidet
zusätzlich zwischen einem sicherheitsrelevanten Offline-Zustand und zwei
Situationen, in denen keine persistente Warnung nötig ist: der kurzen
Initialisierungsphase nach einem Home-Assistant-Neustart sowie der erwarteten
Nachtabschaltung am Mindest-SOC.

Die Zuordnung des Connectivity-Sensors erfolgt automatisch über dasselbe
Home-Assistant-Gerät wie die konfigurierte Entität **NOAH System Output Power**.
Eine zusätzliche Auswahl im Config Flow ist nicht erforderlich.

## Offline-Bedingungen

Der NOAH wird für die aktive Regelung als nicht erreichbar behandelt, wenn:

- `Connectivity` den Zustand `off` meldet,
- der Zustand `unknown` oder `unavailable` ist,
- der Connectivity-State fehlt oder
- eine zuvor erkannte Connectivity-Entität verschwindet.

Ein vorhandener Connectivity-Sensor mit Zustand `on` gilt als online.

Unabhängig davon, ob eine Benachrichtigung angezeigt wird, gilt bei jedem
nicht sicheren Connectivity-Zustand:

- **keine normalen Stellbefehle**,
- **kein 0-W-Failsafe-Befehl**,
- keine erneute Verarbeitung gecachter Noah-MQTT-Quellwerte,
- kein PV-Learning aus gecachter PV-Leistung.

## Startup-Grace-Period

Direkt nach einem Home-Assistant-Neustart können MQTT-Entitäten kurzzeitig
`unknown`, `unavailable` oder noch ohne State sein, bevor Noah-MQTT den ersten
aktuellen Status veröffentlicht.

Ab Beta 12 blockiert der Optimizer die aktive Regelung in dieser Phase sofort,
erzeugt für diese vorläufigen Zustände aber während der ersten **90 Sekunden**
noch keine Offline-Benachrichtigung.

Wichtig:

- `Connectivity = off` ist von dieser Startup-Grace-Period ausgenommen und wird
  grundsätzlich sofort als echter Offline-Zustand behandelt.
- Die Stellbefehls-Sperre ist auch während der Grace-Period bereits aktiv.
- Wird der Sensor innerhalb der 90 Sekunden `on`, bleibt die Benachrichtigung
  vollständig aus.
- Bleibt `unknown`, `unavailable` oder ein fehlender State länger bestehen,
  erscheint anschließend die normale Offline-Benachrichtigung.

## Erwartete Nachtabschaltung am Mindest-SOC

Der Growatt NOAH kann sich nachts nach Erreichen der Entladegrenze vollständig
abschalten. Für den Optimizer ist das bei erreichtem Mindest-SOC kein Fehler.

Beta 12 unterdrückt deshalb die persistente Offline-Benachrichtigung, wenn:

- der NOAH nicht erreichbar ist,
- der zuletzt verfügbare konfigurierte Batterie-SOC höchstens dem eingestellten
  Mindest-SOC zuzüglich einer kleinen Rundungstoleranz entspricht und
- `sun.sun` Nacht beziehungsweise frühe Dämmerung meldet
  (Sonnenhöhe unter 3°).

Die Offline-Sperre bleibt trotzdem vollständig aktiv. Der Optimizer schreibt in
diesem Zustand keinerlei Stellwerte.

Sobald die Sonne höher steht, wird ein weiterhin nicht erreichbarer NOAH wieder
als unerwarteter Offline-Zustand behandelt und die Warnung erscheint. Dadurch
bleibt ein Gerät, das morgens trotz ausreichender Tageszeit nicht wiederkehrt,
erkennbar.

## Warum keine `last_reported`-Zeitstempelprüfung verwendet wird

Beta 10 verwendete `State.last_reported`, um einen unverändert auf `on`
stehenden Connectivity-Sensor nach drei Minuten als veraltet zu behandeln.

Das ist für MQTT-Entitäten nicht zuverlässig: Home Assistant muss bei einem
erneut empfangenen identischen MQTT-Payload keinen neuen Entity-State schreiben.
Ein alter `last_reported`-Zeitstempel bedeutet deshalb nicht automatisch, dass
Noah-MQTT keine aktuellen MQTT-Daten mehr erhält.

Dasselbe gilt für einen unveränderten numerischen Wert von
**System Output Power**. Deshalb wird auch dort keine `last_reported`-
Wiederfreigabeprüfung verwendet.

## Wiederverbindung

Sobald der Noah-MQTT-Connectivity-Sensor wieder `on` meldet:

- wird die Offline-Sperre aufgehoben,
- wird eine vorhandene Offline-Benachrichtigung entfernt,
- werden die aktuellen Quellwerte wieder verarbeitet und
- die bestehende Regellogik darf wieder Stellbefehle senden.

## Einschränkung des Noah-MQTT-Connectivity-Sensors

Der Optimizer kann nur den Zustand auswerten, den Home Assistant von Noah-MQTT
erhält. Falls Noah-MQTT selbst weiterhin `Connectivity = on` stehen lässt,
obwohl der physische NOAH bereits ausgeschaltet ist, kann der Optimizer daraus
keinen Offline-Zustand ableiten.

Dieses Verhalten sollte bevorzugt in Noah-MQTT selbst über eine belastbare
Availability-/Expiry-Logik behoben werden, statt im Optimizer einen zweiten
MQTT-Watchdog nachzubauen.

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

# NOAH-Offline-Erkennung

Ab `2.1.0-beta.10` überwacht der NOAH Optimizer den von Noah-MQTT
bereitgestellten **Connectivity**-Binary-Sensor des konfigurierten NOAH.

Die Zuordnung erfolgt automatisch über dasselbe Home-Assistant-Gerät wie die
konfigurierte Entität **NOAH System Output Power**. Eine zusätzliche Auswahl
im Config Flow ist nicht erforderlich.

## Offline-Bedingungen

Der NOAH wird als nicht erreichbar behandelt, wenn:

- `Connectivity` den Zustand `off` meldet,
- der Zustand `unknown` oder `unavailable` ist,
- eine zuvor erkannte Connectivity-Entität verschwindet oder
- ein weiterhin als `on` angezeigter Connectivity-Zustand länger als drei
  Minuten nicht neu gemeldet wurde.

Die letzte Bedingung schützt zusätzlich vor veralteten/gecachten Daten, wenn
Noah-MQTT selbst keine aktuellen Statusmeldungen mehr liefert.

## Verhalten bei Offline

Während der NOAH offline ist:

- werden **keine Stellbefehle** gesendet,
- wird auch kein 0-W-Failsafe-Befehl gesendet,
- wird ein laufender Failsafe-Zähler zurückgesetzt,
- wird `Datenstatus` auf **Stellgröße nicht verfügbar** gesetzt,
- wird `Controllerstatus` auf **Stellgröße nicht verfügbar** gesetzt,
- erscheint einmalig die persistente Home-Assistant-Benachrichtigung
  **NOAH Optimizer: NOAH offline**.

Damit können gecachte Noah-MQTT-Werte nicht mehr zu
`Datenstatus: OK / Controller: Synchron` führen, obwohl der NOAH selbst
offline ist.

## Wiederverbindung

Ein frischer `online`-Status allein reicht nach einem erkannten Offline-Zustand
noch nicht zum Wiederanlauf der aktiven Regelung.

Noah-MQTT veröffentlicht `Connectivity` und die normalen Gerätemesswerte über
den Geräte-Status-Topic. **System Output Power** wird dagegen über einen
separaten Parameter-Status-Topic gemeldet. Deshalb kann dessen Home-Assistant-
Zustand nach einer Wiederverbindung noch der alte gecachte Stellwert sein.

Nach einem Offline-Zustand wartet der Optimizer deshalb zusätzlich auf eine
neue Meldung von **System Output Power**, die mindestens so aktuell ist wie die
erste wiederhergestellte Connectivity-Meldung.

Erst danach:

- wird die Offline-Benachrichtigung automatisch entfernt,
- werden die aktuellen Werte erneut eingelesen und
- die unveränderte bestehende Regellogik darf wieder Stellbefehle senden.

Damit kann `Controller: Synchron` nach einer Wiederverbindung nicht allein auf
einem alten gecachten Stellwert beruhen.

## Kompatibilität

Falls bei einer älteren Noah-MQTT-Version noch keine Connectivity-Entität
existiert, wird die aktive Regelung nicht unerwartet abgeschaltet. Stattdessen
wird einmalig eine Warnung in das Home-Assistant-Protokoll geschrieben.

Für die vollständige Offline-Erkennung wird eine aktuelle Noah-MQTT-Version
empfohlen.

## Gecachte Messwerte und PV-Learning

Während der NOAH offline ist, wird der Coordinator bewusst **nicht** erneut
aus den Noah-MQTT-Quellentitäten aktualisiert. Noah-MQTT kann die zuletzt
bekannten Werte für PV-Leistung und SOC weiterhin anzeigen, obwohl das
physische Gerät nicht erreichbar ist.

Das ist besonders für das PV-Learning wichtig: Die PV-Energie wird aus der
Leistung über die vergangene Zeit integriert. Würde ein gecachter letzter
PV-Leistungswert während der Offline-Zeit wiederholt verarbeitet, entstünde
fiktive PV-Produktion.

Nach Wiederherstellung der Verbindung wird die ausgelassene Zeit von der
bestehenden Lernlogik als normale Messlücke behandelt. Eine längere
Tageslücke verwirft den Lerntag dadurch korrekt, anstatt den Lernfaktor mit
falscher PV-Energie zu verfälschen.


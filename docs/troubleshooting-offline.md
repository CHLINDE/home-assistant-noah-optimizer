# NOAH-Offline-Erkennung – Fehlerbehebung

## Home Assistant meldet „NOAH Optimizer: NOAH offline“

Prüfe zuerst direkt am Growatt NOAH:

1. Ist das Gerät eingeschaltet?
2. Ist die IoT-/WLAN-Anzeige aktiv?
3. Falls nötig, die **IoT-Taste** beziehungsweise WLAN-Kopplung des NOAH prüfen.
4. In ShinePhone kontrollieren, ob der NOAH wieder als `Online` angezeigt wird.
5. In Home Assistant beim Noah-MQTT-Gerät den Binary-Sensor
   **Connectivity** prüfen.

Während eines nicht sicheren Connectivity-Zustands blockiert der Optimizer
bewusst alle Stellbefehle, auch wenn die sichtbare Benachrichtigung in einer der
unten beschriebenen erwarteten Situationen unterdrückt wird.

## Nach Home-Assistant-Neustart erscheint kurzzeitig keine Offline-Warnung

Das ist ab `2.1.0-beta.12` beabsichtigt.

Nach einem Neustart können MQTT-Entitäten zunächst `unknown`, `unavailable`
oder ohne State sein. Der Optimizer blockiert die aktive Regelung in dieser
Phase sofort, wartet für die persistente Warnung aber bis zu **90 Sekunden** auf
den ersten stabilen Noah-MQTT-Status.

`Connectivity = off` wird grundsätzlich sofort als echter Offline-Zustand
behandelt, sofern nicht gleichzeitig die erwartete Nachtabschaltung am
Mindest-SOC greift.

## NOAH schaltet sich nachts bei Mindest-SOC ab

Das kann ein normaler Betriebszustand sein. Wenn der zuletzt bekannte Batterie-
SOC am eingestellten Mindest-SOC liegt und der NOAH während Nacht beziehungsweise
früher Dämmerung nicht erreichbar wird, zeigt Beta 12 **keine persistente
Offline-Benachrichtigung** mehr an.

Die Sicherheitssperre bleibt aktiv:

```text
keine normalen Stellbefehle
kein 0-W-Failsafe-Befehl
keine Verarbeitung gecachter Noah-MQTT-Werte
```

Steht die Sonne anschließend höher als etwa 3° und der NOAH bleibt weiterhin
nicht erreichbar, wird die Situation wieder als unerwartet behandelt und die
Warnung erscheint.

## Historischer SOC-Ladeplan zeigt nachts noch den letzten Sollwert des Vorabends

Bis Beta 12 konnte das dynamische SOC-Soll bei einer erwarteten Nachtabschaltung
am Mindest-SOC auf dem letzten Wert des Vorabends stehen bleiben. Grund war die
absichtlich gesperrte Übernahme gecachter NOAH-Messwerte.

Ab `2.1.0-beta.13` wird während dieser erwarteten Abschaltung stattdessen der
konfigurierte Mindest-SOC als dynamisches Soll veröffentlicht.

## Datenstatus zeigt „Stellgröße nicht verfügbar“, Connectivity ist aber `on`

Unter `2.1.0-beta.10` konnte dies durch die fehlerhafte 3-Minuten-Prüfung von
`Connectivity.last_reported` verursacht werden. Ab Beta 11 wird dieser
Zeitstempel nicht mehr als MQTT-Freshness-Indikator verwendet.

Lösung bei einer alten Installation:

```text
Auf 2.1.0-beta.12 oder neuer aktualisieren.
```

## Datenstatus zeigt „Stellgröße nicht verfügbar“ und Connectivity ist `off`

Das ist beabsichtigt. Die Noah-MQTT-Leistungswerte können weiterhin als zuletzt
bekannte beziehungsweise gecachte Werte vorhanden sein. Solange Connectivity
`off`, `unknown` oder `unavailable` meldet, werden sie nicht als aktuelle
NOAH-Daten verwendet.

## Connectivity bleibt `on`, obwohl der NOAH physisch aus ist

Das ist eine Einschränkung des von Noah-MQTT gelieferten Connectivity-Zustands.
Der Optimizer behandelt `Connectivity = on` bewusst als online, weil
Home-Assistant-Zeitstempel bei unveränderten MQTT-Werten keine zuverlässige
Freshness-Information liefern.

Wenn ShinePhone den NOAH bereits als offline zeigt, Noah-MQTT/Home-Assistant
aber weiterhin `Connectivity = on`, sollte die Availability-/Expiry-Logik in
Noah-MQTT geprüft beziehungsweise dort als Issue gemeldet werden.

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

`Connectivity = on` hebt die Offline-Sperre wieder auf. Eine vorhandene
Offline-Benachrichtigung wird automatisch entfernt und die aktuellen Quellwerte
werden wieder verarbeitet.

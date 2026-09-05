# Fehlerbehebung

Dieses Dokument bezieht sich auf die HACS-Integration **Growatt NOAH
Optimizer**, insbesondere `2.1.0-beta.11`.

## 1. Integration wird nicht geladen

Unter **Einstellungen → System → Protokolle** nach:

```text
noah_optimizer
```

suchen.

Prüfen:

- Home Assistant neu gestartet
- `manifest.json` auf `2.1.0-beta.11`
- Quell-Entitäten vorhanden
- keine Python-Fehler

## 2. Datenstatus ist nicht OK

Unter **Werkzeuge → Zustände** prüfen.

Kritisch:

- Netzleistung
- Solar Power
- Output Power
- SOC

Nicht dauerhaft `unknown` oder `unavailable`.

## 3. Stellgröße nicht verfügbar

System Output Power muss eine beschreibbare `number`-Entität sein.

Unter **Werkzeuge → Aktionen** mit `number.set_value` testen.

Ab Beta 10 kann derselbe Status auch absichtlich gesetzt werden, wenn der NOAH
über Noah-MQTT als offline erkannt wurde. In diesem Fall erscheint zusätzlich
die persistente Benachrichtigung **NOAH Optimizer: NOAH offline**.

## 4. Netzvorzeichen falsch

Erwartet:

```text
positiv = Netzbezug
negativ = Einspeisung
```

## 5. Batteriefluss falsch

```text
consumption = Entladeleistung
production  = Ladeleistung
```

## 6. Dynamisches SOC-Soll unavailable

Prüfen:

- Restprognose
- Einheit
- `sun.sun`
- Ziel-SOC
- Mindest-SOC
- Akkukapazität

## 7. Ladeplanbasis Tageslicht-Fallback

Kann korrekt sein. Native Kurve nur bei sicher auflösbarer Forecast.Solar-
Quelle.

## 8. PV-Learning nicht bereit

Mindestens drei gültige Lerntage.

Mögliche ungültige Tage:

- große Messlücken
- fehlende Prognosereferenz
- unvollständiger Lerntag
- unplausible Messwerte
- längerer NOAH-Offline-Zeitraum während des Tages

## 9. Lernfaktor wirkt nicht

Prüfen:

```text
PV-Learning bereit = Ein
Gelernte PV-Korrektur verwenden = Ein
```

## 10. Hinter Ladeplan

```text
Ist-SOC < dynamisches SOC-Soll - 2 %-Punkte
```

Ein aktiver Eingriff erfolgt nur bei dynamischer SOC-Steuerung in Automatik.

## 11. Nachts Vor Ladeplan

Ab Beta 14 nicht vorgesehen.

Erwartet:

```text
Nachtbetrieb
```

## 12. SOC-Nachladung zu stark

SOC-Nachholzeit erhöhen.

## 13. SOC-Nachladung zu schwach

Prüfen:

- Hinter Ladeplan
- dynamische Ladeleistung > 0
- ausreichend PV
- Ausgangsgrenzen

## 14. SOC-Halten erscheint nicht

Benötigt erfüllten Plan in Automatik mit dynamischer SOC-Steuerung.

## 15. Unnötige Ladepriorität trotz erfülltem Plan

Ab 2.1.0-beta.2 sollte `soc_hold` dies verhindern.

Version, Ist-SOC, dynamisches Soll und Reglermodus prüfen.

## 16. SOC-Freigabe erscheint nicht

Prüfen:

```text
Automatik
Dynamische SOC-Steuerung = Ein
Vorausschauende SOC-Freigabe = Ein
Tag
Forecast verfügbar
Ist-SOC > Freigabegrenze
Netzbezug > 0
```

## 17. Prognosebasierter Mindest-SOC sehr hoch

Für die Freigabe:

```text
PV-Energie für Wiederaufladung
= wirksame Restprognose - zusätzliche Energiereserve
```

Der erwartete Hausenergiebedarf wird hier nicht abgezogen.

## 18. PV-Umlenkung erscheint nicht

Benötigt:

- Automatik
- dynamische SOC-Steuerung
- Tag
- Forecast
- Ist-SOC mindestens am Soll
- Akkuladeleistung > 0
- Netzbezug > 0
- keine priorisierte SOC-Nachladung

## 19. Akku wird nicht zusätzlich entladen

PV-Umlenkung soll keine zusätzliche Akkuentladung erzeugen.

Dafür ist SOC-Freigabe zuständig.

## 20. Optimizer berechnet, steuert aber nicht

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Ein
```

## 21. controller_status disabled

Aktive Steuerung aus.

## 22. optimizer_disabled

Berechnung aus.

## 23. legacy_controller_active

Legacy-YAML noch aktiv.

## 24. critical_data_missing

Kritischer Messwert fehlt.

## 25. actuator_unavailable

Stellgröße nicht verfügbar oder Beta 10 hat den NOAH als offline erkannt.

Bei erkanntem NOAH-Offline-Zustand wird keine Stellgröße beschrieben.

## 26. rate_limited

Befehl erforderlich, aber Mindestabstand noch nicht erreicht.

## 27. waiting_for_retry

Anzeige:

```text
Warte auf Stellwertübernahme
```

Sollwert wurde geschrieben, aber noch nicht bestätigt.

## 28. in_sync

Sollwert und Stellgröße innerhalb Hysterese.

Ein offline erkannter NOAH darf in Beta 10 nicht mehr auf `in_sync` /
**Synchron** stehen.

## 29. command_failed

`number.set_value` fehlgeschlagen.

## 30. failsafe

Kritische Daten fehlten zu lange.

Der 0-W-Failsafe-Befehl wird bei erkanntem NOAH-Offline-Zustand bewusst nicht
gesendet.

## 31. Dashboard erscheint nicht

Nach:

```text
Could not create the NOAH Optimizer dashboard
```

suchen.

## 32. Power Flow Card Plus fehlt

HACS installieren und Frontend neu laden.

## 33. ApexCharts Card fehlt

HACS installieren und Frontend neu laden.

## 34. Historische SOC-Karte Configuration error

Prüfen:

- Beta 10
- Neustart
- Lovelace-Ressource
- Browser/App neu laden
- Cache `?v=8`

## 35. Historische Daten fehlen

Recorder-Konfiguration prüfen.

## 36. Vergangener Tag weicht von heutiger Berechnung ab

Beabsichtigt. Historie zeigt tatsächliche damalige Zustände.

## 37. Farben nach Beta 7 weiterhin falsch

Genau dieser Upgrade-Fall wird durch `2.1.0-beta.8` behoben.

Ursache: alte explizite `color`-Werte im gespeicherten Dashboard.

Lösung:

1. Beta 8 installieren.
2. Home Assistant neu starten.
3. Dashboard öffnen.

Template-Version:

```text
18
```

## 38. Reglerverhalten falsche Farben

Erwartet:

```text
Regler-Soll                  #2196F3
Ist-Ausgang                  #009B21
Eigenverbrauch-Soll          #FF6A00
Ladepriorität-Soll           #FFD800
Nötige Ladeleistung          #00FFFF
Dynamische Nachladeleistung  #B200FF
```

## 39. Reglerverhalten bleibt nach Beta 8 falsch

Das kann bei einem bereits gespeicherten älteren **5-Serien-Chart** auftreten.
Beta 8 erkannte `Reglerverhalten` nur, wenn auch die später ergänzte Serie
**Dynamische Nachladeleistung** vorhanden war.

Beta 9 behebt diesen Fall und erhöht die Dashboard-Template-Version auf 19.
Dadurch wird die Migration auch dann erneut ausgeführt, wenn Template 18 schon
gespeichert war.

Erwartete Farben der fünf Kernserien:

```text
Regler-Soll                  #2196F3
Ist-Ausgang                  #009B21
Eigenverbrauch-Soll          #FF6A00
Ladepriorität-Soll           #FFD800
Nötige Ladeleistung          #00FFFF
```

Ist die sechste Serie vorhanden:

```text
Dynamische Nachladeleistung  #B200FF
```

## 40. Historischer SOC falsche Farben

Erwartet:

```text
Ist-SOC                      #2196F3
Dynamisches SOC-Soll         #009B21
Ziel-SOC                     #FF6A00
Gespeicherter Plan           #FFD800
```

## 41. Eigenes ApexCharts wird nicht umgefärbt

Beabsichtigt.

Template v19 ändert nur eindeutig erkannte Standardcharts.

## 42. Eigenes ApexCharts wurde unerwartet geändert

Mit aktuellem Beta-9-Fix darf die alte breite v17-Farbmigration nicht mehr
vorgeschaltet sein.

Prüfen:

- aktuelle `dashboard_migration_v18.py`
- Version `2.1.0-beta.11`
- Neustart

## 43. Migration läuft immer wieder

Gespeicherte Template-Version prüfen.

Bei stark verändertem Dashboard kann eine sichere Erkennung bewusst
ausbleiben.

## 44. Historischer Beta-8-Jinja-Fehler

```text
TemplateSyntaxError: unexpected '}'
```

wird durch die ältere Template-9-Migration repariert.

## 45. Frontend zeigt alte JS-Version

Cache:

```text
?v=8
```

Browser/App vollständig neu laden.

## 46. Plan-Snapshots fehlen

Snapshots werden dedupliziert und nur bei relevanten Planänderungen gespeichert.

## 47. Failsafe

Bei dauerhaft fehlenden Daten:

- Warnung
- wenn möglich 0 W
- Rücksetzen nach Datenrückkehr

Bei NOAH offline wird nicht versucht, 0 W zu schreiben.

## 48. Legacy-YAML und HACS gleichzeitig

Nicht zulässig.

## 49. SOC-Freigabe reagiert zu träge

```text
Controller-Auswertung = 15 s
Erhöhungen            = 30 s
Normal                = 120 s
```

## 50. Kurzzeitige Einspeisung

Möglich durch:

- Messverzögerung
- MQTT-Verzögerung
- Stellgrößenraster
- Lastsprünge
- NOAH-Übernahmezeit

## 51. Abend-SOC wird nicht erreicht

Die Prognose ist keine Garantie. Reale PV und Last können abweichen.

## 52. Welche Version?

HACS und `manifest.json` prüfen:

```text
2.1.0-beta.11
```

## 53. Was ändert Beta 9 an der Regelung?

Nichts. Beta 9 korrigiert die verbleibende Reglerverhalten-Farbmigration.
Optimizer- und Controllerlogik bleiben unverändert.

## Beta-10-Fehler: „Stellgröße nicht verfügbar“ trotz Connectivity = Verbunden

Wenn der NOAH normal arbeitet und Noah-MQTT `Connectivity = Verbunden` / `on`
meldet, der Optimizer aber nach einigen Minuten trotzdem auf
**Stellgröße nicht verfügbar** wechselt, betrifft die Installation den in
`2.1.0-beta.11` behobenen Zeitstempelfehler.

Beta 10 verwendete `last_reported` als MQTT-Freshness-Indikator. Bei einem
unveränderten MQTT-Zustand beziehungsweise Number-Wert muss Home Assistant aber
keinen neuen Entity-State schreiben. Dadurch konnte der Zeitstempel altern,
obwohl weiterhin aktuelle MQTT-Daten vorlagen.

Lösung:

```text
2.1.0-beta.11 oder neuer installieren
Home Assistant vollständig neu starten
```

Beta 11 verwendet für die Offline-Entscheidung ausschließlich den tatsächlichen
Connectivity-Zustand.

## 54. Home Assistant meldet „NOAH Optimizer: NOAH offline“

Prüfen:

1. Direkt am NOAH die IoT-/WLAN-Anzeige prüfen.
2. In ShinePhone kontrollieren, ob der NOAH als Online angezeigt wird.
3. Beim Noah-MQTT-Gerät unter Home Assistant den Binary-Sensor
   **Connectivity** prüfen.
4. Falls die IoT-Anzeige am NOAH aus ist, die IoT-Verbindung bzw. IoT-Taste
   prüfen.
5. Noah-MQTT-Protokoll auf API-/MQTT-Fehler prüfen.

Während dieser Meldung blockiert der Optimizer sämtliche Stellbefehle.

## 55. Connectivity ist `on`, aber der Optimizer meldet offline

Unter `2.1.0-beta.10` kann dies durch die fehlerhafte
`last_reported`-Zeitstempelprüfung verursacht werden. Ein unveränderter
MQTT-Connectivity-Zustand muss in Home Assistant nicht bei jedem identischen
Payload erneut geschrieben werden.

Ab `2.1.0-beta.11` gilt `Connectivity = on` als online und wird nicht mehr
allein aufgrund eines alten `last_reported`-Zeitstempels als offline
behandelt.

Wenn dieses Verhalten noch auftritt:

1. Prüfen, ob tatsächlich `2.1.0-beta.11` oder neuer installiert ist.
2. Home Assistant vollständig neu starten.
3. Den Rohzustand des Noah-MQTT-Connectivity-Sensors unter
   **Werkzeuge → Zustände** prüfen.

## 56. Connectivity-Sensor fehlt

Der Optimizer sucht automatisch auf demselben Home-Assistant-Gerät wie
**NOAH System Output Power** nach einem Binary-Sensor der Geräteklasse
`connectivity` bzw. der Noah-MQTT-Unique-ID mit Suffix `_connectivity`.

Wenn noch nie ein solcher Sensor gefunden wurde, bleibt Beta 10 aus
Kompatibilitätsgründen im bisherigen Verhalten und schreibt eine Warnung ins
Protokoll. Noah-MQTT aktualisieren bzw. MQTT-Discovery prüfen.

## 57. PV-Energie steigt scheinbar weiter, obwohl NOAH offline ist

Das darf mit der korrigierten Beta-10-Implementierung nicht passieren.

Der ursprüngliche Feature-Stand hat den Coordinator auch während Offline alle
15 Sekunden aktualisiert. Bei einem von Noah-MQTT gecachten PV-Wert konnte das
PV-Learning dadurch fiktive Energie integrieren.

Die korrigierte Implementierung prüft Connectivity vor jeder
Quellwertübernahme und pausiert Coordinator/PV-Learning während Offline.

Nach Wiederverbindung wird die Messlücke normal bewertet. Eine lange
Tageslücke verwirft den Lerntag.

## Feste Dashboard-Farbpalette

Die von der Integration erzeugten Standarddiagramme verwenden eine feste
Farbpalette:

```text
Blau     #2196F3
Grün     #009B21
Orange   #FF6A00
Gelb     #FFD800
Cyan     #00FFFF
Violett  #B200FF
```

### Reglerverhalten

```text
Regler-Soll                  #2196F3  Blau
Ist-Ausgang                  #009B21  Grün
Eigenverbrauch-Soll          #FF6A00  Orange
Ladepriorität-Soll           #FFD800  Gelb
Nötige Ladeleistung          #00FFFF  Cyan
Dynamische Nachladeleistung  #B200FF  Violett
```

### Historischer SOC-Ladeplan

```text
Ist-SOC                      #2196F3  Blau
Dynamisches SOC-Soll         #009B21  Grün
Ziel-SOC                     #FF6A00  Orange
Gespeicherter Ladeplan       #FFD800  Gelb
```

### Dashboard-Migration in 2.1.0-beta.8

Beta 8 erhöht die Dashboard-Template-Version von `17` auf `18`.

Die vorherigen Farbänderungen hatten die Dashboardvorlagen bereits korrigiert.
In einem schon gespeicherten Lovelace-Dashboard konnten jedoch explizite alte
`color`-Werte erhalten bleiben. Dadurch waren nach einem Update weiterhin
falsche Farben sichtbar.

Template v18 korrigiert deshalb vorhandene Farben nur auf eindeutig erkannten
NOAH-Standard-ApexCharts. Für die Erkennung werden der bekannte deutsche oder
englische Kartentitel und die erwartete Entity-Kombination geprüft. Bei der
PV-Prognose werden zusätzlich die bekannten Data-Generatoren ausgewertet.

Eigene oder zusätzlich angelegte ApexCharts werden nicht pauschal verändert.

Die historische SOC-Karte verwendet bereits die aktuelle
Blau/Grün/Orange/Gelb-Palette. Ihr Frontend-Cache wird mit Beta 8 auf `v8`
angehoben.

Die Änderung betrifft ausschließlich Dashboarddarstellung und
Dashboardmigration. Optimizer-Berechnung und aktive NOAH-Regelung bleiben
unverändert.

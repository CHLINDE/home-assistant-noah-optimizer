# Fehlerbehebung

Dieses Dokument bezieht sich auf die HACS-Integration **Growatt NOAH
Optimizer**, insbesondere `2.1.0-beta.8`.

## 1. Integration wird nicht geladen

Unter **Einstellungen → System → Protokolle** nach:

```text
noah_optimizer
```

suchen.

Prüfen:

- Home Assistant neu gestartet
- `manifest.json` auf `2.1.0-beta.8`
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

Stellgröße nicht verfügbar.

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

## 29. command_failed

`number.set_value` fehlgeschlagen.

## 30. failsafe

Kritische Daten fehlten zu lange.

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

- Beta 8
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

## 39. Historischer SOC falsche Farben

Erwartet:

```text
Ist-SOC                      #2196F3
Dynamisches SOC-Soll         #009B21
Ziel-SOC                     #FF6A00
Gespeicherter Plan           #FFD800
```

## 40. Eigenes ApexCharts wird nicht umgefärbt

Beabsichtigt.

Template v18 ändert nur eindeutig erkannte Standardcharts.

## 41. Eigenes ApexCharts wurde unerwartet geändert

Mit aktuellem Beta-8-Fix darf die alte breite v17-Farbmigration nicht mehr
vorgeschaltet sein.

Prüfen:

- aktuelle `dashboard_migration_v18.py`
- Version `2.1.0-beta.8`
- Neustart

## 42. Migration läuft immer wieder

Gespeicherte Template-Version prüfen.

Bei stark verändertem Dashboard kann eine sichere Erkennung bewusst
ausbleiben.

## 43. Historischer Beta-8-Jinja-Fehler

```text
TemplateSyntaxError: unexpected '}'
```

wird durch die ältere Template-9-Migration repariert.

## 44. Frontend zeigt alte JS-Version

Cache:

```text
?v=8
```

Browser/App vollständig neu laden.

## 45. Plan-Snapshots fehlen

Snapshots werden dedupliziert und nur bei relevanten Planänderungen gespeichert.

## 46. Failsafe

Bei dauerhaft fehlenden Daten:

- Warnung
- wenn möglich 0 W
- Rücksetzen nach Datenrückkehr

## 47. Legacy-YAML und HACS gleichzeitig

Nicht zulässig.

## 48. SOC-Freigabe reagiert zu träge

```text
Controller-Auswertung = 15 s
Erhöhungen            = 30 s
Normal                = 120 s
```

## 49. Kurzzeitige Einspeisung

Möglich durch:

- Messverzögerung
- MQTT-Verzögerung
- Stellgrößenraster
- Lastsprünge
- NOAH-Übernahmezeit

## 50. Abend-SOC wird nicht erreicht

Die Prognose ist keine Garantie. Reale PV und Last können abweichen.

## 51. Welche Version?

HACS und `manifest.json` prüfen:

```text
2.1.0-beta.8
```

## 52. Was ändert Beta 8 an der Regelung?

Nichts. Beta 8 korrigiert Dashboard-Farbmigration und Frontend-Cache.

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

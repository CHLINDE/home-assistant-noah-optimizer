# Fehlerbehebung

## 1. Integration lädt nicht

Prüfen:

- HACS-Version installiert
- Home Assistant neu gestartet
- Protokoll nach `noah_optimizer` durchsuchen

## 2. Quellwert ist nicht verfügbar

Unter **Werkzeuge → Zustände** die konfigurierte Entity prüfen.

Unterstützte Leistungseinheiten:

```text
W
kW
```

Unterstützte Energieeinheiten:

```text
Wh
kWh
```

## 3. Netzleistung hat falsches Vorzeichen

Erwartet:

```text
positiv = Netzbezug
negativ = Einspeisung
```

Falls umgekehrt, Setup-Option **Netzvorzeichen umkehren** verwenden.

## 4. Forecast.Solar-Kurve fehlt

Prüfen:

- Restprognose-Entity stammt direkt von Forecast.Solar
- Forecast.Solar ist geladen
- Sensor ist verfügbar

Bei Template-/Fremdsensoren ist der Tageslicht-Fallback beabsichtigt.

## 5. PV-Learning bleibt nicht bereit

Mindestens drei gültige Lerntage sind erforderlich.

Ungültig können unter anderem sein:

- zu später Start
- unzureichende Tagesabdeckung
- große Messlücke
- fehlende Prognosereferenz

## 6. Gelernter Faktor verändert nichts

Prüfen:

```text
Gelernte PV-Korrektur verwenden = Ein
PV-Learning bereit = Ein
```

Solange einer der Punkte nicht erfüllt ist, bleibt der Basissicherheitsfaktor
maßgeblich.

## 7. SOC-Ladeplan zeigt nachts Vor Ladeplan

Ab Beta 14 muss der Status nachts:

```text
Nachtbetrieb
```

lauten.

Prüfen:

- aktuelle Version installiert
- Home Assistant neu gestartet
- `sun.sun` verfügbar

## 8. Dynamische SOC-Steuerung greift nicht ein

SOC-Nachladung benötigt unter anderem:

- Automatik
- Forecast verfügbar
- Tag
- SOC über Mindest-SOC
- SOC unter Ziel-SOC
- mehr als 2 Prozentpunkte Rückstand

## 9. SOC-Nachladung wirkt zu stark

SOC-Nachholzeit erhöhen.

Beispiel:

```text
2,0 h -> 3,0 h
```

## 10. SOC-Nachladung wirkt zu schwach

SOC-Nachholzeit reduzieren und prüfen:

- `SOC-Ladeplan = Hinter Ladeplan`
- dynamisch erforderliche Ladeleistung > 0
- ausreichend PV vorhanden

## 11. SOC-Ladeplan halten erscheint nicht

Benötigt:

- Automatik
- dynamische SOC-Steuerung aktiv
- Plan erfüllt
- keine höher priorisierte SOC-Nachladung
- keine aktive SOC-Freigabe/PV-Umlenkung mit höherer Priorität

## 12. PV-Umlenkung erscheint nicht

Benötigt:

- Automatik
- dynamische SOC-Steuerung
- Ist-SOC mindestens am dynamischen Soll
- Akkuladeleistung > 0
- Netzbezug > 0

Der sichere zusätzliche Sollwert ist begrenzt auf:

```text
min(Netzbezug, Akkuladeleistung)
```

## 13. Akku wird trotz Netzbezug nicht entladen

Für absichtliche Batterieentladung ist nicht PV-Umlenkung, sondern die
vorausschauende SOC-Freigabe zuständig.

Prüfen:

- SOC-Freigabe aktiv
- dynamische SOC-Steuerung aktiv
- Freigabegrenze < Ist-SOC
- freigebare Akkuenergie > 0
- positiver Netzbezug

## 14. Optimizer berechnet, steuert aber nicht

Prüfen:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Ein
```

Controllerstatus beachten.

## 15. Typische Controllerstatus

### disabled

Aktive Steuerung aus.

### optimizer_disabled

Berechnung aus.

### legacy_controller_active

Legacy-YAML-Optimizer blockiert HACS-Schreibzugriff.

### critical_data_missing

Kritischer Messwert fehlt.

### actuator_unavailable

Stellgröße nicht verfügbar.

### rate_limited

Ein tatsächlich erforderlicher Stellbefehl wartet auf den zulässigen
Mindestabstand.

### waiting_for_retry

Ein Sollwert wurde geschrieben, aber noch nicht innerhalb der Hysterese von der
Stellgröße bestätigt.

### in_sync

Sollwert und Stellgröße liegen innerhalb der Hysterese.

### command_failed

`number.set_value` fehlgeschlagen.

### failsafe

Kritische Daten fehlten zu lange.

## 16. Dashboard erscheint nicht

Protokoll nach:

```text
Could not create the NOAH Optimizer dashboard
```

durchsuchen.

Auch prüfen, ob `/noah-optimizer` bereits anderweitig verwendet wird.

## 17. Custom element fehlt

Für externe Dashboardkarten müssen installiert sein:

```text
Power Flow Card Plus
ApexCharts Card
```

Danach Frontend neu laden.

## 18. Historische SOC-Karte zeigt Configuration error

Prüfen:

- Integration aktuell
- Home Assistant neu gestartet
- Lovelace-Ressource für `noah-soc-history-card.js` vorhanden
- Browser/App neu geladen

Beta 8 verwendet den Cache-Parameter:

```text
?v=8
```

## 19. Farben bleiben nach Beta 7 falsch

Das ist der Fehler, den `2.1.0-beta.8` behebt.

Ursache:

Frühere Migrationen konnten vorhandene `color`-Einträge pauschal erhalten.
Deshalb blieb bei einem bereits gespeicherten Dashboard die alte Farbe stehen,
obwohl die neue Vorlage korrekt war.

Lösung:

1. `2.1.0-beta.8` installieren.
2. Home Assistant vollständig neu starten.
3. Dashboard neu öffnen.

Die Dashboard-Template-Version muss danach auf 18 migriert worden sein.

## 20. Reglerverhalten hat weiterhin falsche Farben

Erwartet:

```text
Regler-Soll                  #2196F3
Ist-Ausgang                  #009B21
Eigenverbrauch-Soll          #FF6A00
Ladepriorität-Soll           #FFD800
Nötige Ladeleistung          #00FFFF
Dynamische Nachladeleistung  #B200FF
```

Wenn das Diagramm stark manuell verändert wurde, kann die sichere Erkennung
absichtlich ausbleiben. Die Migration verlangt sowohl den Standardtitel als
auch die erwartete Entity-Kombination.

## 21. Eigene ApexCharts wurden nicht umgefärbt

Das ist beabsichtigt.

Template v18 korrigiert ausschließlich eindeutig erkannte NOAH-Standardcharts.

## 22. Historische SOC-Farben

Erwartet:

```text
Ist-SOC             #2196F3
Dynamisches Soll    #009B21
Ziel-SOC            #FF6A00
Gespeicherter Plan  #FFD800
```

Wenn eine alte Darstellung sichtbar bleibt:

- Browser hart neu laden
- Home-Assistant-App vollständig schließen/öffnen
- prüfen, ob Ressource `?v=8` geladen wird

## 23. Migration läuft nach jedem Neustart erneut

Bei mindestens einem erkannten Standardchart wird Template v18 auch dann
persistiert, wenn die Farben bereits korrekt waren.

Falls ein extrem stark angepasstes Dashboard keinen Standardchart mehr sicher
erkennen lässt, wird bewusst nichts pauschal überschrieben.

## 24. Beta-8/Beta-9 Jinja-Fehler aus der 2.0-Reihe

Ältere Installationen können den historischen Fehler:

```text
TemplateSyntaxError: unexpected '}'
```

enthalten.

Die bestehenden älteren Migrationen bleiben weiterhin aktiv und reparieren
diesen bekannten Zustand.

## 25. Failsafe

Bei dauerhaft fehlenden kritischen Daten:

- Warnung wird erzeugt
- wenn möglich 0 W angefordert
- nach Wiederkehr der Daten wird der Zustand zurückgesetzt

## 26. Legacy-YAML und HACS gleichzeitig aktiv

Nicht zulässig.

Vor aktiver HACS-Steuerung:

```text
input_boolean.noah_optimizer_enabled = Aus
```

setzen.

## 27. SOC-Freigabe reagiert zu träge

Während SOC-Freigabe wird der Controller häufiger bewertet als im normalen
Regelpfad.

Typisch:

```text
Controller-Auswertung: 15 s
Erhöhung:              30 s Mindestabstand
Normal:               120 s Mindestabstand
```

Reduzierungen dürfen aus Sicherheitsgründen schneller erfolgen.

## 28. Kurzzeitige Einspeisung bei SOC-Freigabe

Kleine Abweichungen können durch:

- Messverzögerung
- MQTT-Verzögerung
- Lastsprünge
- Stellgrößenraster
- NOAH-Übernahmezeit

entstehen.

## 29. Forecast-/Plan-Historie fehlt

Snapshots werden nur bei inhaltlich geänderten Plänen geschrieben und
dedupliziert.

Retention:

```text
31 Tage
max. 48 Planstände pro Tag
```

## 30. Vergangener Tag sieht anders als heutige Neuberechnung aus

Beabsichtigt.

Die historische Karte verwendet Recorder-Zustände, die tatsächlich am
gewählten Tag aufgezeichnet wurden. Ein vergangener Tag wird nicht mit heutigen
Parametern neu berechnet.

## 31. Welche Version ist tatsächlich installiert?

In HACS und in:

```text
custom_components/noah_optimizer/manifest.json
```

prüfen.

Für diesen Fix muss stehen:

```text
2.1.0-beta.8
```

## 32. Was ändert Beta 8 an der Regelung?

Nichts.

Beta 8 korrigiert Dashboard-Migration, Darstellung und Frontend-Cache. Die
Optimizer- und aktive Controllerlogik bleibt unverändert.

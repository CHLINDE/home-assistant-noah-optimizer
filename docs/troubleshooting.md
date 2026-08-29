# Fehlerbehebung

Dieses Dokument bezieht sich auf den stabilen Release `2.0.0` und den aktuellen
Pre-Release `2.1.0-beta.8`.

## 1. Integration wird nicht geladen

Unter **Einstellungen → System → Protokolle** nach `noah_optimizer` suchen.

Prüfen:

- HACS-Installation vollständig
- Home Assistant nach dem Update neu gestartet
- `manifest.json` meldet `2.1.0-beta.8`
- alle Quell-Entitäten vorhanden
- keine Python-Fehler im Protokoll

## 2. Datenstatus ist nicht OK

Unter **Werkzeuge → Zustände** die ausgewählten Quell-Entitäten prüfen.
`unknown` und `unavailable` dürfen bei kritischen Quellen nicht dauerhaft
anliegen.

## 3. „Stellgröße nicht verfügbar“

Die konfigurierte `NOAH System Output Power`-Entität muss vorhanden,
verfügbar, numerisch und als `number` beschreibbar sein.

Unter **Werkzeuge → Aktionen** mit `number.set_value` prüfen.

## 4. Netzbezug und Einspeisung sind vertauscht

Erwartet:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Bei umgekehrter Quelle **Netzvorzeichen umkehren** aktivieren.

## 5. Batteriefluss im Dashboard ist falsch herum

Für Power Flow Card Plus muss gelten:

```text
consumption = Entladeleistung
production  = Ladeleistung
```

## 6. Dynamisches SOC-Soll ist `unavailable`

Prüfen:

- Restprognose heute verfügbar
- Forecast.Solar-Quelle korrekt
- `sun.sun` verfügbar
- Ziel-SOC, Mindest-SOC und Akkukapazität plausibel

## 7. SOC-Ladeplan zeigt nachts „Vor Ladeplan“

Seit dem stabilen 2.0.0-Regelstand verwendet der SOC-Ladeplan nachts den eigenen
Enum-Zustand `night`, lokalisiert als **Nachtbetrieb**.

Falls weiterhin ein Tagesstatus erscheint:

- Home Assistant vollständig neu starten
- Rohzustand des SOC-Ladeplan-Sensors unter **Werkzeuge → Zustände** prüfen
- Integrationsversion prüfen

## 8. Dynamische SOC-Steuerung ist an, aber nichts ändert sich

Die Funktion greift nur unter passenden Bedingungen ein. Unter anderem müssen
Automatik, Forecast und Tagesbetrieb aktiv sein und der jeweilige Ladeplanstatus
einen Eingriff erfordern.

## 9. SOC-Nachladung wirkt zu stark oder zu schwach

Über die **SOC-Nachholzeit** kann der Zeitraum verändert werden, über den der
SOC-Rückstand aufgeholt werden soll.

Größerer Wert → geringere erforderliche Nachladeleistung.

Kleinerer Wert → höhere erforderliche Nachladeleistung.

## 10. Controllerstatus

Wichtige Rohzustände:

```text
disabled
optimizer_disabled
legacy_controller_active
critical_data_missing
actuator_unavailable
target_unavailable
rate_limited
waiting_for_retry
in_sync
command_sent
command_failed
failsafe
```

`waiting_for_retry` bedeutet, dass ein Sollwert bereits gesendet wurde, die
Stellgröße ihn aber noch nicht innerhalb der Hysterese zurückmeldet. Die Anzeige
lautet **Warte auf Stellwertübernahme**.

## 11. Dashboard erscheint nicht

Im Protokoll nach:

```text
Could not create the NOAH Optimizer dashboard
```

suchen. Ein möglicher Grund ist ein bereits belegter Pfad `/noah-optimizer`.

## 12. Power Flow Card Plus oder ApexCharts fehlt

Fehler wie:

```text
Custom element doesn't exist: power-flow-card-plus
Custom element doesn't exist: apexcharts-card
```

bedeuten, dass die jeweilige HACS-Frontendkarte nicht installiert oder noch
nicht neu geladen wurde.

## 13. Historische SOC-Karte wird nicht aktualisiert

Beta 8 registriert die Ressource mit:

```text
/noah_optimizer/noah-soc-history-card.js?v=8
```

Nach dem Update Home Assistant und die Browser-/App-Ansicht vollständig neu
laden. In Lovelace-Storage-Mode aktualisiert die Integration die Ressource auf
`v=8` automatisch.

## 14. Farben sind nach dem Update weiterhin falsch

Der aktuelle `2.1.0-beta.8`-Stand verwendet Dashboard-Template-Version 18 und
feste Serienfarben.

Prüfen:

1. Tatsächlich `2.1.0-beta.8` installiert.
2. Home Assistant vollständig neu gestartet.
3. NOAH-Dashboard anschließend neu geöffnet.
4. Die gespeicherte Dashboard-Migration auf Template-Version 18 wurde ausgeführt.
5. Die betroffene Karte ist eine erkannte generierte NOAH-Standardkarte.

Template-Version 18 richtet Farben in eindeutig erkannten generierten
NOAH-Standarddiagrammen einmalig neu aus. Zusätzliche oder benutzerdefinierte
ApexCharts-Karten werden nicht verändert.

### Erwartete Farben – Reglerverhalten

```text
Regler-Soll                   #2196F3
Ist-Ausgang                   #009B21
Eigenverbrauch-Soll           #FF6A00
Ladepriorität-Soll            #FFD800
Erforderliche Ladeleistung    #00FFFF
Dynamische Nachladeleistung   #B200FF
```

### Erwartete Farben – Historischer SOC-Ladeplan

```text
Ist-SOC                       #2196F3
Dynamisches Soll              #009B21
Ziel-SOC                      #FF6A00
Gespeicherter Plan            #FFD800
```

Wenn eine benutzerdefinierte Karte absichtlich einen anderen Titel trägt, wird
sie von der Beta-8-Migration nicht angefasst.

## 15. Dashboard wurde schon von Beta 7 auf Version 17 migriert

Das ist genau der Fall, den Beta 8 behebt. Die neue Version erhöht die
Template-Version auf 18. Dadurch wird die korrigierte Migration noch einmal
ausgeführt, obwohl Beta 7 bereits Version 17 gespeichert hatte.

## 16. Failsafe

Fehlen kritische Daten lange genug:

- persistente Benachrichtigung wird erzeugt
- bei erreichbarer Stellgröße wird `0 W` angefordert
- Warnung bleibt auch bei nicht erreichbarer Stellgröße sichtbar
- nach Wiederkehr der Daten wird der Failsafe zurückgesetzt

## 17. Legacy-YAML und HACS gleichzeitig aktiv

Nicht zulässig. Vor aktiver HACS-Steuerung sicherstellen, dass der alte
YAML-Optimizer nicht gleichzeitig Stellbefehle sendet.

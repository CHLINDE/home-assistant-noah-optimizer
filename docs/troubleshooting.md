# Fehlerbehebung

Dieses Dokument bezieht sich primär auf die HACS-Integration ab
`2.0.0-beta.13`.

## 1. Integration wird nicht geladen

Unter **Einstellungen → System → Protokolle** nach:

```text
noah_optimizer
```

suchen.

Zusätzlich prüfen:

- HACS-Installation vollständig
- Home Assistant nach dem Update neu gestartet
- `manifest.json` auf `2.0.0-beta.13`
- alle Quell-Entitäten vorhanden
- keine Python-Fehler im Protokoll

## 2. Datenstatus ist nicht OK

Unter **Werkzeuge → Zustände** die ausgewählten Quell-Entitäten prüfen.

Kritisch sind insbesondere:

- saldierte Netzleistung
- NOAH Solar Power
- NOAH Output Power
- NOAH SOC

Die Zustände dürfen nicht dauerhaft:

```text
unknown
unavailable
```

sein.

## 3. „Stellgröße nicht verfügbar“

Die konfigurierte `NOAH System Output Power`-Entität muss:

- vorhanden sein
- verfügbar sein
- numerisch sein
- als `number` beschreibbar sein
- W oder kW verwenden

Unter **Werkzeuge → Aktionen** mit `number.set_value` testen.

Ein `sensor.*_output_power` ist nur ein Messwert und keine Stellgröße.

## 4. Netzbezug und Einspeisung sind vertauscht

Erwartet wird:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Bei umgekehrter Konvention die Integration mit **Netzvorzeichen umkehren**
einrichten.

## 5. Batteriefluss im Dashboard ist falsch herum

Für Power Flow Card Plus muss gelten:

```text
consumption = Entladeleistung
production  = Ladeleistung
```

Im HACS-Dashboard:

```yaml
battery:
  entity:
    consumption: __DISCHARGING_POWER__
    production: __CHARGING_POWER__
```

Das bedeutet:

```text
Ladeleistung    -> Energie fließt in den Akku
Entladeleistung -> Energie fließt aus dem Akku
```

Beta 8 korrigiert beim bestehenden Dashboard zusätzlich die exakte alte
Beta-6-Zuordnung, falls sie noch vorhanden ist.

## 6. Dynamisches SOC-Soll ist `unavailable`

Die dynamischen SOC-Werte benötigen eine verfügbare Forecast.Solar-
Restprognose.

Prüfen:

- `Restprognose heute` ist verfügbar
- Einheit ist `Wh` oder `kWh`
- Sun-Integration liefert `sun.sun`
- Ziel-SOC, Mindest-SOC und Akkukapazität sind plausibel

Fehlt die Prognose, greift die dynamische SOC-Steuerung nicht ein.

## 7. SOC-Ladeplan zeigt „Hinter Ladeplan“

Das bedeutet:

```text
Ist-SOC < dynamisches SOC-Soll - 2 Prozentpunkte
```

Ab Beta 10 wird das dynamische SOC-Soll aus einer zeitbasierten Tageskurve und
einem zusätzlichen Prognosedruck berechnet.

Der Status ist daher jetzt tatsächlich eine Aussage darüber, ob der Akku vor,
im oder hinter dem aktuellen Tages-Ladeplan liegt.

Nur wenn zusätzlich:

```text
Dynamische SOC-Steuerung aktiv = Ein
Betriebsart = Automatik
```

gilt, kann der Zustand den Ausgangssollwert beeinflussen.

### Dynamisches Soll bleibt tagsüber ständig bei 100 %

Das sollte in Beta 10 nicht mehr allein durch eine schlechte Restprognose
verursacht werden.

Prüfen:

- tatsächlich `2.0.0-beta.13` installiert
- Home Assistant nach dem Update vollständig neu gestartet
- `sun.sun` ist verfügbar
- `sun.sun` steht tagsüber auf `above_horizon`
- Mindest-SOC ist kleiner als Ziel-SOC
- Forecast.Solar liefert eine gültige Restprognose

Nahe Sonnenuntergang ist ein dynamisches Soll am Ziel-SOC dagegen normal.

### Dynamisches Soll bleibt tagsüber ständig beim Mindest-SOC

Prüfen:

- `sun.sun` ist verfügbar
- Home Assistant besitzt korrekte Standort- und Zeitzoneneinstellungen
- die Sun-Integration ist geladen

Außerhalb der Tageslichtzeit ist der Mindest-SOC als dynamisches Soll
beabsichtigt.

## 8. Dynamische SOC-Steuerung ist an, aber nichts ändert sich

Das kann korrekt sein. Die Funktion greift nur ein, wenn gleichzeitig:

- Automatik aktiv ist
- Forecast verfügbar ist
- es Tag ist
- SOC über Mindest-SOC liegt
- SOC unter Ziel-SOC liegt
- SOC mehr als 2 Prozentpunkte hinter dem Ladeplan liegt

Steht `SOC-Ladeplan` auf **Im Ladeplan** oder **Vor Ladeplan**, bleibt die
bestehende Automatik zuständig.

## 9. SOC-Nachladung wirkt zu stark

Ab Beta 12 zielt die Nachladung auf das dynamische SOC-Soll am **Ende** des
Nachholfensters. Die angezeigte dynamisch erforderliche Ladeleistung kann
deshalb höher sein als bei älteren Versionen, weil zusätzlich der während der
Nachholzeit weiter steigende Ladeplan berücksichtigt wird.

Wenn die Nachladung trotzdem zu aggressiv ist, Parameter **SOC-Nachholzeit**
erhöhen.

Beispiel:

```text
2,0 h -> 3,0 h
```

Dadurch wird der Rückstand auf einen längeren Zeitraum verteilt und die
berechnete dynamische Ladeleistung sinkt.

## 10. SOC-Nachladung wirkt zu schwach

Ab Beta 12 sollte ein deutlicher SOC-Rückstand nicht mehr allein deshalb
bestehen bleiben, weil die Nachladung nur auf das aktuelle, gleichzeitig
weiter ansteigende Soll zielt.

Prüfen:

- tatsächlich mindestens `2.0.0-beta.12` mit der aktuellen Berechnung installiert
- `SOC-Ladeplan = Hinter Ladeplan`
- `Dynamisch erforderliche Ladeleistung` ist größer als `0 W`
- genügend aktuelle PV-Leistung ist vorhanden, um die berechnete Ladeleistung tatsächlich bereitzustellen
- maximale NOAH-Ausgangsleistung und Hausverbrauch lassen ausreichend PV für die Akkuladung übrig

Ist die Nachladung bei ausreichender PV weiterhin zu schwach, Parameter
**SOC-Nachholzeit** reduzieren.

Beispiel:

```text
2,0 h -> 1,0 h
```

Nicht sofort extrem kleine Werte verwenden. Zunächst die Sensoren und das
Reglerverhalten beobachten.

## 11. Reglermodus „SOC-Nachladung“ erscheint nicht

Der Modus erscheint nur bei aktivem Eingriff der neuen Funktion.

Prüfen:

```text
Optimierer-Berechnung aktiv = Ein
Dynamische SOC-Steuerung aktiv = Ein
Betriebsart = Automatik
SOC-Ladeplan = Hinter Ladeplan
```

Außerdem müssen Tag, Forecast und SOC-Grenzen die Aktivierung erlauben.

## 12. Dynamische Sensoren rechnen, obwohl der Schalter aus ist

Das ist beabsichtigt.

Die Integration berechnet:

```text
Dynamisches SOC-Soll
SOC-Abweichung
SOC-Ladeplan
Dynamisch erforderliche Ladeleistung
```

auch bei ausgeschalteter dynamischer SOC-Steuerung.

Dadurch kann die Berechnung zunächst gefahrlos beobachtet werden.

## 13. Eigenverbrauch, Ladepriorität oder Manuell verändern sich nicht

Das ist ebenfalls beabsichtigt.

Die dynamische SOC-Regelung beeinflusst ausschließlich die Betriebsart **Automatik**.

Die explizit gewählten Betriebsarten:

```text
Eigenverbrauch
Ladepriorität
Manuell
```

behalten ihr bisheriges Verhalten.

## 14. Optimizer berechnet, steuert aber nicht

Prüfen:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Ein
```

Danach am Schalter **NOAH-Steuerung aktiv** das Attribut:

```text
control_status
```

prüfen.

### `disabled`

Aktive Steuerung ist aus.

### `optimizer_disabled`

Berechnung ist aus.

### `legacy_controller_active`

Der alte YAML-Optimizer ist noch aktiv:

```text
input_boolean.noah_optimizer_enabled = on
```

### `critical_data_missing`

Mindestens ein kritischer Messwert fehlt.

### `actuator_unavailable`

Die beschreibbare Stellgröße ist nicht verfügbar.

### `rate_limited`

Ein neuer Stellbefehl ist tatsächlich erforderlich, wartet aber noch auf den
für den aktuellen Reglermodus geltenden Mindestabstand. Ab Beta 13 beträgt
dieser bei `SOC-Freigabe` 30 Sekunden und bei normalen Regelzuständen weiterhin
zwei Minuten.

### `waiting_for_retry`

Sollwert und Stellgröße weichen noch ab; der Controller wartet auf den
Wiederholungszeitpunkt.

### `in_sync`

Sollwert und Stellgröße liegen innerhalb der Hysterese.

### `command_failed`

`number.set_value` ist fehlgeschlagen. Protokoll prüfen.

### `failsafe`

Kritische Messdaten haben zu lange gefehlt.

## 15. Dashboard erscheint nicht

Im Protokoll nach:

```text
Could not create the NOAH Optimizer dashboard
```

suchen.

Mögliche Ursache ist ein bereits belegter Pfad:

```text
/noah-optimizer
```

## 16. Dashboardfehler nach Beta 8 / Beta 9

### `TemplateSyntaxError: unexpected '}'`

Wenn in der Karte **Reglerstatus** nur der Titel angezeigt wird und darunter die Fehlermeldung

`TemplateSyntaxError: unexpected '}'`

erscheint, wurde das Dashboard wahrscheinlich bereits durch Beta 8 migriert.

Beta 8 konnte beim Einfügen des dynamischen SOC-Ladeplanstatus einen
fehlerhaften Jinja-Ausdruck erzeugen.

### Lösung

1. `2.0.0-beta.9` oder neuer über HACS installieren.
2. Home Assistant vollständig neu starten.
3. Dashboard erneut öffnen.

Beta 9 erhöht die Dashboard-Template-Version auf 9 und repariert die betroffene
Zeile automatisch.

Das Dashboard muss nicht gelöscht oder neu erstellt werden.

### Neue Dashboardelemente fehlen

Prüfen:

- tatsächlich `2.0.0-beta.13` installiert
- Home Assistant nach dem HACS-Update vollständig neu gestartet
- Protokoll auf `noah_optimizer`-Fehler prüfen

Stark veränderte Standardkarten können verhindern, dass einzelne Blöcke
automatisch erkannt werden. Die Integration überschreibt bewusst nicht das
gesamte benutzerdefinierte Dashboard.

## 17. Power Flow Card Plus fehlt

Fehler wie:

```text
Custom element doesn't exist: power-flow-card-plus
```

bedeuten, dass Power Flow Card Plus nicht installiert oder noch nicht im
Frontend geladen ist.

In HACS installieren und Browser/App vollständig neu laden.

## 18. ApexCharts Card fehlt

Fehler wie:

```text
Custom element doesn't exist: apexcharts-card
```

entsprechend durch Installation von ApexCharts Card beheben.

## 19. Failsafe

Fehlen kritische Daten zehn Minuten:

- persistente Benachrichtigung wird erzeugt
- bei erreichbarer Stellgröße wird `0 W` angefordert
- bei nicht erreichbarer Stellgröße bleibt die Warnung trotzdem bestehen

Nach Wiederkehr der Daten wird der Failsafe zurückgesetzt.

## 20. Legacy-YAML und HACS gleichzeitig aktiv

Das ist nicht zulässig.

Vor Aktivierung der HACS-Steuerung:

```text
input_boolean.noah_optimizer_enabled = Aus
```

setzen.

Die dynamische SOC-Regelung wird nicht in die Legacy-YAML-Regelung zurückportiert.

## 21. SOC-Freigabe wird nicht aktiv

Der neue Reglermodus lautet:

```text
SOC-Freigabe
```

Er kann nur erscheinen, wenn gleichzeitig:

```text
Optimierer-Berechnung aktiv = Ein
Dynamische SOC-Steuerung aktiv = Ein
Vorausschauende SOC-Freigabe aktiv = Ein
Betriebsart = Automatik
```

Zusätzlich müssen folgende Bedingungen erfüllt sein:

- Forecast.Solar ist verfügbar
- es ist Tag
- der Ist-SOC liegt über der SOC-Freigabegrenze
- freigebare Akkuenergie ist größer als `0 kWh`
- der Netzsensor zeigt positiven Netzbezug

Steht der Akku nur **Vor Ladeplan**, reicht das allein nicht. Die
SOC-Freigabegrenze kann wegen der Restprognose höher als das dynamische SOC-Soll
liegen.

## 22. SOC-Freigabegrenze ist unerwartet hoch

Die Grenze lautet:

```text
SOC-Freigabegrenze
= max(Dynamisches SOC-Soll, Prognosebasierter Mindest-SOC)
  + 2 %-Punkte
```

Ab Beta 12 wird der **prognosebasierte Mindest-SOC für
die SOC-Freigabe** nicht mehr aus derselben konservativen Rechnung wie der
dynamische Ladeplan abgeleitet.

Für die Freigabe gilt:

```text
PV-Energie für Wiederaufladung
= wirksame Restprognose
  - zusätzliche Energiereserve
```

Der erwartete Hausenergiebedarf wird dabei nicht abgezogen.

Wenn der prognosebasierte Mindest-SOC trotzdem nahe `100 %` liegt, prüfen:

- wirksame Restprognose
- zusätzliche Energiereserve
- Prognose-Sicherheitsfaktor
- Ziel-SOC
- Akkukapazität
- Ladewirkungsgrad

Ist:

```text
Wirksame Restprognose <= zusätzliche Energiereserve
```

vorhanden, ist ein prognosebasierter Mindest-SOC bis zum Ziel-SOC korrekt. Es
steht dann nach der Sicherheitsreserve keine prognostizierte Energie mehr zur
Verfügung, um einen jetzt freigegebenen Akkuanteil später wieder aufzuladen.

Wichtig: Der **erwartete Hausenergiebedarf gehört nicht mehr zu dieser
Fehlerprüfung**. Er beeinflusst weiterhin den dynamischen Ladeplan, aber nicht
die separate Wiederauflade-Reserve der SOC-Freigabe.

## 23. Akku wird trotz Netzbezug nicht entladen

Prüfen:

- `Vorausschauende SOC-Freigabe aktiv = Ein`
- `Dynamische SOC-Steuerung aktiv = Ein`
- `Betriebsart = Automatik`
- `SOC-Freigabegrenze < Ist-SOC`
- `Freigebare Akkuenergie > 0 kWh`
- Netzleistung ist tatsächlich positiv

Ist die aktive NOAH-Steuerung ausgeschaltet, werden Reglermodus und
Ausgangssollwert zwar berechnet, aber nicht an die Stellgröße geschrieben.
Das ist der empfohlene Testbetrieb.

## 24. SOC-Freigabe reagiert zu träge auf Netzbezug

Ab Beta 13 wird der aktive Controller alle `15 s` ausgewertet. Während
`SOC-Freigabe` darf ein erforderlicher höherer Stellwert im Abstand von `30 s`
geschrieben werden. Normale Betriebsarten behalten den bisherigen
2-Minuten-Mindestabstand.

Typisches Diagnosebild vor Beta 13:

```text
Reglermodus:          SOC-Freigabe
Sollwert:             deutlich höher
Letzter Stellwert:    deutlich niedriger
Netzbezug:            weiterhin positiv
```

Ab Beta 13 sollte ein solcher Unterschied wesentlich schneller nachgeführt
werden. Kurzzeitig kann weiterhin Netzbezug bestehen, weil Messwertaktualisierung,
15-Sekunden-Auswertung, 30-Sekunden-Mindestabstand, Stellgrößenraster und die
NOAH-Leistungsübernahme zusammenwirken.

Prüfen:

- `Reglermodus = SOC-Freigabe`
- `SOC-Freigabe-Soll` beziehungsweise Ausgangssollwert liegt über dem letzten Stellwert
- `Controller = Wartezeit nach Stellbefehl` darf höchstens bis zum nächsten zulässigen Freigabe-Stellbefehl bestehen bleiben
- `NOAH System Output Power` übernimmt den geschriebenen Wert
- Stellgrößenraster und maximale Ausgangsleistung begrenzen den Sollwert nicht unerwartet

Sicherheitsrelevante **Reduzierungen** nach einem SOC-Freigabe-Befehl bleiben
weiterhin ohne diese Wartezeit möglich.

## 25. Bei SOC-Freigabe entsteht kurz Netzeinspeisung

Die Funktion fordert keine absichtliche Batterieeinspeisung an. Das
SOC-Freigabe-Soll orientiert sich am aktuell gemessenen positiven Netzbezug.

Kurzzeitige kleine Einspeisung kann trotzdem entstehen durch:

- Stellgrößenraster
- Mess- und MQTT-Verzögerungen
- schnelle Änderungen der Hauslast
- Verzögerung bei der NOAH-Leistungsübernahme

Soll der Ausgang nach einem SOC-Freigabe-Stellbefehl reduziert werden, umgeht
diese Reduzierung bewusst die normale 2-Minuten-Wartezeit und die
Schalt-Hysterese. Dadurch soll eine sinkende Hauslast möglichst schnell zu
einem niedrigeren Sollwert führen.

Wenn stärkere oder dauerhafte Einspeisung auftritt:

1. **Vorausschauende SOC-Freigabe aktiv** ausschalten.
2. Prüfen, ob Ausgangssollwert und NOAH-Stellgröße auf einen niedrigeren Wert
   zurückgehen.
3. Anschließend bei Bedarf **NOAH-Steuerung aktiv** ausschalten.

Das Ausschalten von **NOAH-Steuerung aktiv** verhindert weitere Stellbefehle,
setzt einen zuvor geschriebenen NOAH-Sollwert jedoch nicht automatisch auf
`0 W`.

Falls die Stellgröße nicht wie erwartet zurückgeht, kann `NOAH System Output
Power` unter **Werkzeuge → Aktionen** mit `number.set_value` manuell auf einen
sicheren Wert gesetzt werden.

Anschließend Netzleistung, Ausgangssollwert, SOC-Freigabe-Soll und tatsächliche
NOAH-Ausgangsleistung vergleichen.

## 26. Abend-SOC wird trotz SOC-Freigabe nicht erreicht

Die SOC-Freigabe schützt den aufgrund der **aktuellen** Restprognose
berechneten Wiederaufladebedarf. Sie ist keine absolute Garantie.

Für die Freigabe wird angenommen, dass die verbleibende PV-Energie bei Bedarf
zum Wiederaufladen des Akkus priorisiert werden darf. Der spätere
Hausverbrauch kann deshalb zeitweise Netzbezug verursachen.

Mögliche Ursachen für ein später zu niedriges Abend-SOC:

- tatsächlicher PV-Ertrag niedriger als Forecast.Solar
- Prognose-Sicherheitsfaktor zu optimistisch
- zusätzliche Energiereserve zu klein
- unerwartete Verluste oder Leistungsbegrenzungen
- PV-Leistung kommt zeitlich so spät oder kurz, dass der Akku sie nicht
  vollständig aufnehmen kann

Ein höherer tatsächlicher Hausverbrauch ist für die **Freigabe-Reserve** nicht
direkt abgezogen. Er kann jedoch dazu führen, dass später mehr Netzbezug nötig
ist, während PV zum Wiederaufladen des Akkus reserviert wird.

In diesem Fall die vorausschauende SOC-Freigabe zunächst deaktivieren und
Prognose-Sicherheitsfaktor beziehungsweise Energiereserve konservativer
einstellen. Die dynamische **SOC-Nachladung** sollte aktiviert bleiben, damit
ein später erkannter SOC-Rückstand wieder aufgeholt werden kann.

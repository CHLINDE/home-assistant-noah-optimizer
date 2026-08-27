# Fehlerbehebung

Dieses Dokument bezieht sich primär auf die stabile HACS-Integration
`2.0.0`.

## 1. Integration wird nicht geladen

Unter **Einstellungen → System → Protokolle** nach:

```text
noah_optimizer
```

suchen.

Zusätzlich prüfen:

- HACS-Installation vollständig
- Home Assistant nach dem Update neu gestartet
- `manifest.json` auf `2.0.0` (stabil) oder `2.1.0-beta.4` (aktueller Pre-Release)
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

Ab `2.1.0-beta.3` wird das dynamische SOC-Soll bei einer nativen
Forecast.Solar-Quelle aus deren vollständiger zeitaufgelöster Leistungskurve
abgeleitet. Nur wenn diese Kurve nicht verfügbar ist, wird noch der zeitbasierte
Beta-10-Tageslichtalgorithmus verwendet.

Der Status ist eine Aussage darüber, ob der Akku vor, im oder hinter dem aktuell
aus der Prognose berechneten Tages-Ladeplan liegt.

Nur wenn zusätzlich:

```text
Dynamische SOC-Steuerung aktiv = Ein
Betriebsart = Automatik
```

gilt, kann der Zustand den Ausgangssollwert beeinflussen.

### Dynamisches Soll wirkt zeitlich unplausibel

Ab Beta 3 sollte das Soll bei nativer Forecast.Solar-Quelle dem zeitlichen
PV-Profil folgen. Eine Süd-Anlage darf deshalb morgens lange nahe am Mindest-SOC
bleiben, wenn Forecast.Solar zu dieser Zeit kaum Leistung prognostiziert.

Prüfen:

- tatsächlich `2.1.0-beta.4` installiert
- Home Assistant nach dem Update vollständig neu gestartet
- `sun.sun` ist verfügbar
- `sun.sun` steht tagsüber auf `above_horizon`
- Mindest-SOC ist kleiner als Ziel-SOC
- Forecast.Solar liefert eine gültige Restprognose
- **Ladeplanbasis** zeigt `Forecast.Solar-Kurve` und nicht `Tageslicht-Fallback`
- **PV-Prognose aktualisiert** enthält einen plausiblen Zeitstempel
- die Karte **PV-Prognose** enthält Forecast.Solar-Leistungspunkte

Nahe Sonnenuntergang ist ein dynamisches Soll am Ziel-SOC dagegen normal.

### Dynamisches Soll bleibt tagsüber ständig beim Mindest-SOC

Prüfen:

- `sun.sun` ist verfügbar
- Home Assistant besitzt korrekte Standort- und Zeitzoneneinstellungen
- die Sun-Integration ist geladen

Außerhalb der Tageslichtzeit ist der Mindest-SOC als dynamisches Soll
beabsichtigt.

### SOC-Ladeplan zeigt nachts „Vor Ladeplan“

Ab Beta 14 ist das nicht mehr vorgesehen. Während die Nachtbedingung aktiv ist,
muss der Enum-Sensor **SOC-Ladeplan** unabhängig von der rechnerischen
SOC-Abweichung anzeigen:

```text
Nachtbetrieb
```

Die numerische SOC-Abweichung kann nachts weiterhin deutlich positiv sein,
weil das dynamische SOC-Soll auf den Mindest-SOC zurückfällt. Diese Abweichung
ist nur noch ein Diagnosewert und wird nachts nicht als `Vor Ladeplan`
klassifiziert.

Falls weiterhin `Vor Ladeplan` erscheint, prüfen:

- beim aktuellen Pre-Release tatsächlich `2.1.0-beta.4` installiert
- Home Assistant nach dem Update vollständig neu gestartet
- `sun.sun` verfügbar
- Dashboard-Template-Version 15 wurde übernommen
- bei stark angepasster Reglerstatus-Karte den Rohzustand des Sensors unter
  **Werkzeuge → Zustände** prüfen

## 8. Dynamische SOC-Steuerung ist an, aber nichts ändert sich

Das kann korrekt sein. Für die dynamische SOC-Steuerung müssen zunächst
gleichzeitig gelten:

- Automatik aktiv ist
- Forecast verfügbar ist
- es Tag ist
- SOC über Mindest-SOC liegt
- SOC unter Ziel-SOC liegt

Danach hängt der Eingriff von der Lage zum Ladeplan ab:

- **Hinter Ladeplan** (mehr als 2 Prozentpunkte Rückstand) → **SOC-Nachladung**
- **Im Ladeplan** oder **Vor Ladeplan** → **SOC-Ladeplan halten**

Im Modus **SOC-Ladeplan halten** begrenzt `2.1.0-beta.3` den Sollwert auf die
aktuell verfügbare PV-Leistung und den Eigenverbrauchs-Sollwert, ohne
absichtliche Akkuentladung anzufordern.

Sinkt die verfügbare PV-Leistung, darf eine erforderliche Sollwertreduzierung
sofort ausgeführt werden und wartet nicht auf den normalen Mindestabstand von
zwei Minuten. Sollwerterhöhungen im SOC-Halten bleiben weiterhin auf den
normalen Mindestabstand begrenzt.

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
für den aktuellen Reglermodus geltenden Mindestabstand. Ab Beta 14 beträgt
dieser bei `SOC-Freigabe` und `PV-Umlenkung` 30 Sekunden und bei normalen
Regelzuständen weiterhin zwei Minuten.

### `waiting_for_retry`

Die Anzeige lautet ab Beta 14 **Warte auf Stellwertübernahme** beziehungsweise
**Waiting for setpoint confirmation**. Der gewünschte Sollwert wurde bereits
gesendet, die beschreibbare Stellgröße meldet ihn aber noch nicht innerhalb der
Hysterese zurück. Das ist nicht automatisch ein Schreibfehler. Erst nach dem
Retry-Intervall wird derselbe Sollwert bei weiterhin bestehender Abweichung
erneut gesendet.

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

- tatsächlich `2.0.0` installiert
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

## 23. Netzbezug trotz ausreichender PV-Leistung und gleichzeitiger Akkuladung

Typisches Bild:

```text
Ist-SOC >= dynamisches SOC-Soll
Netzbezug > 0 W
Akkuladeleistung > 0 W
Reglermodus vor Beta 14: Ladepriorität
```

Vor Beta 14 konnte die negative Prognosemarge die Ladepriorität aktiv halten,
obwohl der Akku bereits am oder über dem dynamischen SOC-Soll lag. Dadurch
konnte der Speicher gleichzeitig geladen und Hausleistung aus dem Netz bezogen
werden.

Beta 14 führt dafür **PV-Umlenkung** ein. Sie berechnet:

```text
PV-Umlenkungsleistung = min(Netzbezug, Akkuladeleistung)
PV-Umlenkungs-Soll = aktuelle NOAH-Ausgangsleistung + PV-Umlenkungsleistung
```

Die Funktion reduziert damit zuerst nur die vorhandene Akkuladung und fordert
keine absichtliche Akkuentladung an. Voraussetzung ist unter anderem:

- `Betriebsart = Automatik`
- `Dynamische SOC-Steuerung aktiv = Ein`
- Tagbetrieb
- Forecast verfügbar
- `Ist-SOC >= dynamisches SOC-Soll`
- Akkuladeleistung größer als `0 W`
- positiver Netzbezug
- keine aktive SOC-Nachladung

Der Schalter **Vorausschauende SOC-Freigabe aktiv** ist für die PV-Umlenkung
nicht erforderlich. Eine zusätzliche Akkuentladung bleibt weiterhin Aufgabe
der separaten SOC-Freigabe.

Wenn die Bedingungen erfüllt sind, sollte der Reglermodus **PV-Umlenkung**
anzeigen. Das Ausgangssoll wird in diesem Modus auf das Stellgrößenraster
abgerundet und kann deshalb etwas unter dem rechnerischen Rohwert liegen. Die
Abrundung verhindert, dass das Raster den sicheren Umlenkungswert überschreitet.
Ist die sicher umlenkbare Leistung kleiner als der nächste mögliche
Raster-Schritt, kann die PV-Umlenkung deshalb bewusst aussetzen.

## 24. Akku wird trotz Netzbezug nicht entladen

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

## 25. SOC-Freigabe reagiert zu träge auf Netzbezug

Ab Beta 14 wird der aktive Controller weiterhin alle `15 s` ausgewertet.
Während `SOC-Freigabe` und `PV-Umlenkung` darf ein erforderlicher höherer
Stellwert im Abstand von `30 s` geschrieben werden. Normale Betriebsarten
behalten den bisherigen 2-Minuten-Mindestabstand.

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

## 26. Bei SOC-Freigabe entsteht kurz Netzeinspeisung

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

## 27. Abend-SOC wird trotz SOC-Freigabe nicht erreicht

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

## 28. PV-Learning wird nicht bereit

Der Binary Sensor **PV-Learning bereit** wird erst nach mindestens drei
gültigen, vollständig abgeschlossenen Lerntagen aktiv.

Prüfen:

- **NOAH Solar Power** liefert tagsüber plausible Werte.
- **Forecast.Solar Restprognose heute** liefert Werte in Wh oder kWh.
- **PV-Prognosereferenz heute** wird früh am Tag gesetzt.
- **PV-Energie heute** steigt während der PV-Erzeugung an.
- Home Assistant beziehungsweise die Integration lief bereits früh genug am
  Lerntag. Ein erster deutlich zu spät gestarteter Teil-Tag wird verworfen.
- Die Beobachtung erreichte mindestens 85 % des Tageslichtfensters. Ein Ausfall
  bis weit vor den Abend kann deshalb keinen unvollständigen Tagesertrag lernen.
- Es gab während der Tagesbeobachtung keine Messlücke über zehn Minuten. Eine
  solche Lücke verwirft den gesamten Lerntag; die fehlende PV-Produktion wird
  nicht als Nullertrag angelernt.
- Mindestens zwei Stunden gültige Tagesbeobachtung lagen vor.

**PV-Lerntage** wird erst beim Abschluss eines gültigen Tages erhöht, also
typischerweise beim ersten Coordinator-Update des Folgetags.

Nach **PV-Lerndaten zurücksetzen** beginnt die Lernhistorie wieder bei null.

## 29. Gelernte PV-Korrektur hat keine Wirkung

Prüfen:

```text
PV-Learning bereit = Ein
Gelernte PV-Korrektur verwenden = Ein
```

Ist einer der beiden Zustände nicht erfüllt, verwendet der Optimizer weiterhin
nur den konfigurierten Prognose-Sicherheitsfaktor.

Zum Vergleich die Sensoren prüfen:

```text
PV-Lernfaktor
Wirksamer Prognosefaktor
Wirksame Restprognose
```

Bei aktivem und bereitem Learning muss gelten:

```text
Wirksamer Prognosefaktor
= Prognose-Sicherheitsfaktor × PV-Lernfaktor
```

Der Lern-Schalter ändert keine Betriebsart und umgeht keine vorhandenen
Sicherheitsmechanismen der aktiven NOAH-Steuerung.

## 30. PV-Lernfaktor wirkt unplausibel

Der Faktor basiert auf dem Median der letzten maximal sieben gültigen Tage.
Ein einzelner schlechter Tag sollte den Median deshalb nur begrenzt
beeinflussen. Für das Learning wird jeder Tageswert zusätzlich auf
`0,50 ... 1,50` begrenzt.

Bei dauerhaft unplausiblen Werten prüfen:

- ob **NOAH Solar Power** wirklich die gesamte zu Forecast.Solar passende
  PV-Leistung beschreibt
- ob Forecast.Solar dieselbe PV-Anlage beziehungsweise Modulausrichtung
  prognostiziert
- ob es häufige Neustarts oder längere Datenlücken während der PV-Zeit gibt

Sind die Quellen inzwischen korrigiert worden, **PV-Lerndaten zurücksetzen**
und eine neue Lernhistorie aufbauen.


## 31. Ladeplanbasis zeigt „Tageslicht-Fallback“

`2.1.0-beta.3` kann die vollständige Prognosekurve nur automatisch übernehmen,
wenn die beim NOAH Optimizer konfigurierte **Forecast.Solar Restprognose heute**
direkt zu einer Home-Assistant-Config-Entry der Integration `forecast_solar`
gehört.

Prüfen:

- die ausgewählte Restprognose ist ein originaler Forecast.Solar-Sensor und kein Template-Sensor
- Forecast.Solar ist vollständig geladen und liefert im Energiedashboard eine Prognose
- Home Assistant wurde nach dem Update vollständig neu gestartet
- **PV-Prognose aktualisiert** ist verfügbar
- **PV-Prognosekurve** ist verfügbar und enthält im Attribut `raw_power` Punkte

Der Fallback ist kein Fehlerzustand. Er hält die ältere Beta-10-Berechnung für
kompatible Fremdprognosen weiterhin funktionsfähig.

## 32. PV-Prognosekurve weicht stark von der realen PV-Leistung ab

Die Karte zeigt bewusst sowohl die Vorhersage als auch die reale PV-Leistung.
Der Ladeplan wird **nicht** nachträglich anhand des Ist-SOC oder der realen
PV-Leistung passend gerechnet. Dadurch bleibt ein Prognosefehler sichtbar.

Prüfen:

- Ausrichtung, Neigung und Anlagenleistung in Forecast.Solar
- Zeitpunkt **PV-Prognose aktualisiert**
- Prognose-Sicherheitsfaktor
- PV-Lernfaktor und ob **Gelernte PV-Korrektur verwenden** aktiv ist

Ändert Forecast.Solar seine Prognose bei der nächsten Aktualisierung, wird der
Ladeplan aus der neuen Forecast-Kurve neu berechnet.

## 33. Ladepriorität obwohl der Ist-SOC bereits im dynamischen Ladeplan liegt

Typisches Bild vor `2.1.0-beta.2`:

```text
Dynamische SOC-Steuerung aktiv = Ein
Ist-SOC >= dynamisches SOC-Soll - Toleranz
Prognosemarge < 0 kWh
Reglermodus = Ladepriorität
```

Die klassische Prognosemarge betrachtet den noch fehlenden Energiebedarf bis
zum endgültigen Ziel-SOC. Der dynamische SOC-Ladeplan berücksichtigt Forecast,
Hauslast und Sicherheitsreserve jedoch bereits in seinem zeitabhängigen Soll.
Dadurch konnte dieselbe knappe Prognose ein zweites Mal bewertet werden und
Ladepriorität anzeigen, obwohl der Speicher den aktuellen Ladeplan bereits
erfüllt hatte.

Ab `2.1.0-beta.2` verwendet die Automatik in diesem Zustand den internen Modus
**SOC-Ladeplan halten**. Er fordert höchstens die kleinere Leistung aus
aktueller PV-Leistung und Eigenverbrauchs-Soll an und wird auf das
Stellgrößenraster abgerundet. Damit entsteht durch diesen Modus keine
absichtliche Akkuentladung.

Soll Akkuenergie oberhalb der sicheren Freigabegrenze gezielt für den
Hausverbrauch genutzt werden, muss weiterhin **Vorausschauende SOC-Freigabe
aktiv** eingeschaltet sein. SOC-Nachladung und PV-Umlenkung behalten ihre
vorhandenen Prioritäten.


## 34. Historischer SOC-Ladeplan zeigt keine Daten

Ab `2.1.0-beta.4` verwendet die Karte **Historischer SOC-Ladeplan** Home
Assistants History/Recorder für Ist-SOC, dynamisches Soll und Ziel-SOC.

Prüfen:

- tatsächlich `2.1.0-beta.4` installiert und Home Assistant neu gestartet
- Dashboard-Template-Version 15 wurde übernommen
- die Integrationen `frontend` und `history` sind geladen
- Recorder enthält für den gewählten Tag Zustände der drei SOC-Entitäten
- der gewählte Tag liegt innerhalb der Aufbewahrungszeit des Recorders
- Browser beziehungsweise Home-Assistant-App nach dem Update vollständig neu geladen

Bei Tagen, die älter als die Recorder-Aufbewahrungszeit sind, können die
Verlaufslinien nicht mehr rekonstruiert werden.

## 35. Für einen vergangenen Tag ist kein Planstand auswählbar

Forecast-/Plan-Snapshots werden erst ab `2.1.0-beta.4` gesammelt. Es gibt daher
keine rückwirkenden Snapshots für Tage vor der Installation dieser Version.

Die Integration hält die Snapshot-Historie rollierend für 31 Tage und maximal
48 unterschiedliche Planstände je Tag. Ein neuer Snapshot wird nur gespeichert,
wenn sich die Forecast-/SOC-Plan-Daten oder ein planungsrelevanter Parameter
tatsächlich ändern. Identische Pläne erzeugen keinen zusätzlichen Eintrag.

Prüfen:

- **Ladeplanbasis** steht auf `Forecast.Solar-Kurve`
- **PV-Prognosekurve** ist verfügbar
- **PV-Prognose aktualisiert** enthält einen plausiblen Zeitstempel
- der ausgewählte Tag liegt nicht mehr als 31 Tage zurück

Die Planstand-Auswahl ist eine Diagnosefunktion. Fehlende Snapshots beeinflussen
die aktive NOAH-Regelung nicht.

## Historischer SOC-Ladeplan zeigt „Konfigurationsfehler“

Ab `2.1.0-beta.4` wird die gebündelte Karte `noah-soc-history-card.js`
in Home Assistants Storage-Ressourcenmodus als echte Lovelace-Modulressource
registriert. Dadurch wird die Karte vor dem Aufbau des Dashboards geladen.

Nach einem Update von einem früheren Beta-4-Stand sollte das Frontend einmal
neu geladen werden. Falls die Karte weiterhin als `Konfigurationsfehler`
erscheint:

1. Home Assistant neu starten.
2. Browserseite vollständig neu laden (`Strg+F5`).
3. Unter **Einstellungen → Dashboards → Ressourcen** prüfen, ob eine Ressource
   mit `/noah_optimizer/noah-soc-history-card.js?v=5` vorhanden ist.

Im YAML-Ressourcenmodus verwendet die Integration weiterhin die
Frontend-Injektion als Kompatibilitäts-Fallback.

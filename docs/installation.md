# Installation

Diese Anleitung beschreibt die Installation und das Update des **Home
Assistant Growatt NOAH Optimizers** für den Pre-Release `2.1.0-beta.3`.

Für neue Installationen wird die HACS-Integration empfohlen.

## 1. Voraussetzungen

Benötigt werden:

- Home Assistant
- HACS
- MQTT
- Noah-MQTT
- Forecast.Solar
- Sun-Integration
- saldierter Netzleistungssensor
- beschreibbare `number`-Entität für NOAH System Output Power

Für das vollständige Dashboard zusätzlich:

- Power Flow Card Plus
- ApexCharts Card

Die beiden Dashboardkarten werden nicht automatisch installiert.

## 2. Benötigte Quell-Entitäten

Vor dem Einrichten müssen vorhanden sein:

| Funktion | Entitätstyp | Einheit |
|---|---|---|
| Saldierte Netzleistung | `sensor` | W oder kW |
| NOAH Solar Power | `sensor` | W oder kW |
| NOAH Output Power | `sensor` | W oder kW |
| NOAH SOC | `sensor` | % |
| NOAH Charging Power | `sensor` | W oder kW |
| NOAH Discharge Power | `sensor` | W oder kW |
| Forecast.Solar Restprognose heute | `sensor` | Wh oder kWh |

> **Beta 3:** Für den zeitaufgelösten Ladeplan muss diese Entität direkt von der
> Home-Assistant-Integration **Forecast.Solar** stammen. Bei Template- oder
> Fremdsensoren bleibt die bisherige Tageslichtberechnung automatisch als
> Fallback aktiv.
| NOAH System Output Power | `number` | W oder kW |

Die Entity-IDs können unter **Werkzeuge → Zustände** geprüft werden.

### Netzvorzeichen

Erwartet wird:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Bei umgekehrter Konvention während der Einrichtung **Netzvorzeichen umkehren**
aktivieren.

## 3. Dashboardkarten installieren

In HACS installieren:

```text
Power Flow Card Plus
ApexCharts Card
```

Danach Browser beziehungsweise Home-Assistant-App vollständig neu laden.

Der Optimizer selbst funktioniert auch ohne diese Karten.

## 4. Repository in HACS öffnen

Am einfachsten über My Home Assistant:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

> **Hinweis zu Home Assistant 2026.8 und neuer:**  
> Home Assistant OS verwendet bei neuen Installationen standardmäßig Port 80
> statt Port 8123. Home Assistant Container verwendet weiterhin standardmäßig
> Port 8123. Der HACS-Link selbst enthält keinen Home-Assistant-Port.
>
> Falls My Home Assistant noch eine Adresse mit `:8123` öffnet, muss dort die
> gespeicherte Instanz-URL auf die tatsächlich verwendete
> Home-Assistant-Adresse angepasst werden.

Alternativ das Repository in HACS als benutzerdefiniertes Repository hinzufügen:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

## 5. Version 2.1.0-beta.3 installieren

Zu installierende Version:

```text
2.1.0-beta.3
```

In HACS müssen für dieses Repository Vorabversionen angezeigt beziehungsweise
berücksichtigt werden. Danach `2.1.0-beta.3` auswählen und installieren.

Nach der Installation Home Assistant vollständig neu starten.

Wer PV-Learning noch nicht testen möchte, kann beim stabilen Release `2.0.0`
bleiben.

## 6. Neue Installation einrichten

Öffne:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

und suche nach:

```text
Growatt NOAH Optimizer
```

Wähle die acht Quell-Entitäten aus.

Zusätzlich stehen zur Verfügung:

### Netzvorzeichen umkehren

Aktivieren, wenn dein Netzsensor positive Werte für Einspeisung und negative
Werte für Bezug liefert.

### Dashboard in der Seitenleiste anzeigen

Standard:

```text
Ein
```

## 7. Update auf 2.1.0-beta.3

Vor dem Update:

```text
NOAH-Steuerung aktiv = Aus
Dynamische SOC-Steuerung aktiv = Aus
Vorausschauende SOC-Freigabe aktiv = Aus
```

Nach dem Update ist zusätzlich der neue Schalter **Gelernte PV-Korrektur
verwenden** standardmäßig aus.

`2.1.0-beta.3` übernimmt PV-Learning und **SOC-Ladeplan halten** aus Beta 1/2
und ergänzt den zeitaufgelösten Forecast.Solar-Ladeplan. Wenn die ausgewählte
Restprognose direkt aus der Home-Assistant-Integration Forecast.Solar stammt,
verwendet der Optimizer deren bereits geladene vollständige Leistungskurve.
Zusätzliche Forecast.Solar-API-Aufrufe werden nicht ausgeführt.

Der dynamische SOC-Ladeplan folgt damit der erwarteten PV-Erzeugung statt dem
reinen Tageslichtfortschritt. Als Diagnose kommen **PV-Prognose aktualisiert**,
**Wirksame Tagesprognose**, **Prognostizierter End-SOC** und **Ladeplanbasis**
hinzu. Das Dashboard erhält eine eigene PV-Prognosekurve.

Danach Version `2.1.0-beta.3` über HACS installieren und Home Assistant
vollständig neu starten.

### Update von 2.0.0

`2.1.0-beta.3` übernimmt alle Einstellungen des stabilen Releases `2.0.0`.
Enthalten sind das PV-Learning aus Beta 1 sowie der korrigierte dynamische
Automatikmodus. Neu gegenüber `2.0.0` sind unter anderem:

- passives, persistentes PV-Learning
- sechs PV-Learning-Diagnosesensoren
- Binary Sensor **PV-Learning bereit**
- Schalter **Gelernte PV-Korrektur verwenden**
- Schaltfläche **PV-Lerndaten zurücksetzen**
- interner Reglermodus **SOC-Ladeplan halten** für einen bereits erfüllten dynamischen Ladeplan
- zeitaufgelöste Forecast.Solar-Leistungskurve ohne zusätzliche API-Aufrufe
- Forecast-geformter dynamischer SOC-Ladeplan mit Tageslicht-Fallback
- neue Forecast-Diagnosewerte und PV-Prognosekarte
- Dashboard-Template-Version 14

Das Learning startet nach dem Neustart automatisch mit der Datensammlung. Die
gelernte PV-Korrektur ist jedoch standardmäßig ausgeschaltet und kann
frühestens nach drei gültigen Lerntagen auf die Forecast-Berechnung wirken.
Der neue Modus **SOC-Ladeplan halten** kann dagegen bereits bei aktivierter
dynamischer SOC-Steuerung das Regelverhalten gegenüber `2.0.0` verändern.

Empfohlen ist, zunächst **PV-Energie heute**, **PV-Prognosereferenz heute**,
**PV-Lerntage** und **PV-Lernfaktor** zu beobachten. Erst nach plausiblen
Werten sollte die gelernte Korrektur eingeschaltet werden.

### Update von 2.0.0-beta.14

Der stabile Zwischenstand `2.0.0` entspricht funktional `2.0.0-beta.14`.
`2.1.0-beta.3` baut auf genau diesem Regelstand auf, enthält das PV-Learning
aus Beta 1 und ergänzt außerdem den oben beschriebenen Modus
**SOC-Ladeplan halten**.

Damit gelten gegenüber Beta 14 zusätzlich die Änderungen aus
**Update von 2.0.0**: neue PV-Learning-Entitäten, der Opt-in-Schalter, die
Reset-Schaltfläche, den SOC-Halten-Modus, die zeitaufgelöste Forecast-Kurve und Dashboard-Template-Version 14.
Die gelernte PV-Korrektur verändert die Forecast-Berechnung weiterhin erst
nach ausdrücklicher Aktivierung; der SOC-Halten-Modus ist davon unabhängig und
gehört zur dynamischen SOC-Steuerung.

### Update von Beta 13

Version `2.0.0` übernimmt alle Einstellungen aus Beta 13. Neu hinzu kommt der
Enum-Sensor **Controllerstatus**. Der vorhandene Enum-Sensor **SOC-Ladeplan**
erhält zusätzlich den Zustand:

```text
night = Nachtbetrieb
```

Die Tageszustände `Vor Ladeplan`, `Im Ladeplan` und `Hinter Ladeplan` bleiben
unverändert. Sobald Nachtbetrieb gilt, wird stattdessen `Nachtbetrieb`
angezeigt.

Zusätzlich kommt der Reglermodus **PV-Umlenkung** hinzu. Er wird verwendet,
wenn der Akku mindestens am dynamischen Soll liegt, gleichzeitig lädt und
Netzbezug besteht. Dabei wird nur bis zur aktuell vorhandenen Akkuladeleistung
zum Haus umgelenkt; eine absichtliche Akkuentladung ist dafür nicht nötig.
Der endgültige PV-Umlenkungs-Sollwert wird dabei auf das konfigurierte
Stellgrößenraster abgerundet. Ist damit kein sicherer höherer Rasterwert
möglich, bleibt die PV-Umlenkung für diesen Zyklus inaktiv.

Die Dashboard-Template-Version steigt von 10 auf 11. Die Migration ergänzt den
Nachtstatus und `PV-Umlenkung` und stellt die Controllerstatus-Anzeige auf den
neuen Enum-Sensor mit zentralen Übersetzungen um. Übrige Benutzeranpassungen
werden nicht ersetzt.


### Update von Beta 12

Version `2.0.0` übernimmt alle vorhandenen Einstellungen aus Beta 12 und enthält
zusätzlich die Änderungen aus Beta 13 und Beta 14. Neu hinzu kommt der
Enum-Sensor **Controllerstatus**; neue Schalter werden nicht angelegt.

Beta 13 beschleunigt die aktive Controller-Nachführung:

```text
Controller-Auswertung:                 15 s
Normale Stellbefehle:                 120 s Mindestabstand
Sollwerterhöhung bei SOC-Freigabe:     30 s Mindestabstand
Sollwertreduzierung nach Freigabe:   sofort möglich
```

Beta 14 ergänzt am vorhandenen Enum-Sensor **SOC-Ladeplan** den Zustand
`night = Nachtbetrieb`, den Reglermodus **PV-Umlenkung** und den neuen
Enum-Sensor **Controllerstatus**. Die Reglerstatus-Karte wird auf
Dashboard-Template-Version 11 migriert.

### Update von Beta 11

Version `2.0.0` übernimmt alle vorhandenen Einstellungen und Entitäten aus Beta 11
und enthält zusätzlich die Berechnungsänderungen aus Beta 12, die schnellere
SOC-Freigabe-Nachführung aus Beta 13 und den Nachtstatus aus Beta 14.

Neu hinzu kommt in Beta 14 der Enum-Sensor **Controllerstatus**. Neue Schalter
werden nicht angelegt.

Beta 12 korrigiert zwei Berechnungen der dynamischen SOC-Regelung:

- den prognosebasierten Mindest-SOC der vorausschauenden SOC-Freigabe
- die dynamisch erforderliche Ladeleistung bei einem SOC-Rückstand

Es werden dafür keine neuen Entitäten, Schalter oder Dashboardelemente
benötigt.

In Beta 11 wurde für Ladeplan und SOC-Freigabe dieselbe konservative
Prognose-Anforderung verwendet:

```text
wirksame Restprognose
- erwarteter Hausenergiebedarf
- zusätzliche Energiereserve
```

Dadurch konnte die SOC-Freigabegrenze trotz vollem Akku auf `100 %` steigen,
wenn die normale Prognosemarge wegen des erwarteten Hausverbrauchs negativ war.

Ab Beta 12 verwendet die SOC-Freigabe eine eigene Wiederauflade-Reserve:

```text
PV-Energie für Wiederaufladung
= wirksame Restprognose
  - zusätzliche Energiereserve
```

Der erwartete Hausenergiebedarf wird bei dieser separaten Reserve bewusst nicht
abgezogen.

Die dynamische SOC-Sollkurve selbst bleibt unverändert und berücksichtigt den
erwarteten Hausenergiebedarf weiterhin. Die SOC-Nachladung verwendet ab Beta
12 jedoch das vorausberechnete Soll am Ende der Nachholzeit. Dadurch wird die
Nachladeleistung so dimensioniert, dass ein Akku, der hinter dem Ladeplan liegt,
nicht nur das aktuelle Soll erreicht, während dieses gleichzeitig weiter
ansteigt.

### Update von Beta 10 oder älter

Beim direkten Update auf `2.0.0` bleiben alle bisherigen Migrationen erhalten.

Falls die Beta-11-Elemente noch fehlen, werden weiterhin ergänzt:

```text
Vorausschauende SOC-Freigabe aktiv
Prognosebasierter Mindest-SOC
PV-Prognose aktualisiert
Wirksame Tagesprognose
Prognostizierter End-SOC
Ladeplanbasis
SOC-Freigabegrenze
Freigebare Akkuenergie
SOC-Freigabe-Soll
Controllerstatus
```

Im Nachtbetrieb muss `SOC-Ladeplan` ab Beta 14 `Nachtbetrieb` anzeigen und nicht
mehr `Vor Ladeplan`, nur weil der Ist-SOC über dem Mindest-SOC liegt.

Für die PV-Umlenkung eignet sich ein Test mit Ist-SOC mindestens am dynamischen
Soll, positiver Akkuladeleistung und gleichzeitig positivem Netzbezug. Der
Reglermodus soll dann `PV-Umlenkung` anzeigen und den Ausgang höchstens um
`min(Netzbezug, Akkuladeleistung)` erhöhen.

Zusätzlich steht der Reglermodus:

```text
SOC-Freigabe
```

zur Verfügung.

Die Funktion ist bei einer neuen Einrichtung standardmäßig ausgeschaltet.

## 8. Dashboard und Migration

Version `2.0.0` enthält die mit Beta 14 eingeführte gezielte Migration der
vorhandenen Reglerstatus-Karte. Ergänzt werden der
neue Nachtstatus, der Reglermodus **PV-Umlenkung** und die Anzeige des neuen
Enum-Sensors **Controllerstatus**. Deshalb steigt die interne Version auf:

```text
Dashboard-Template-Version = 11
```

Bei einem Update von Beta 13 wird die vorhandene Reglerstatus-Karte gezielt um
`Nachtbetrieb` beziehungsweise `Night operation` und `PV-Umlenkung` /
`PV diversion` ergänzt. Die bisherige lokale Jinja-Tabelle für Controllerstatus
wird durch `state_translated()` auf dem neuen Enum-Sensor ersetzt.

Bei älteren Installationen bleiben die bisherigen Migrationen aktiv:

- Beta-6-Batteriezuordnung korrigieren, wenn sie noch exakt unverändert vorliegt
- Beta-8-Dynamic-SOC-Elemente ergänzen, falls sie fehlen
- SOC-Planungsdiagramm ergänzen, falls es fehlt
- fehlerhaften Beta-8-Jinja-Ausdruck reparieren
- Beta-11-SOC-Freigabeschalter und Diagnosesensoren ergänzen

Das Dashboard wird **nicht vollständig ersetzt**. Eigene Anpassungen bleiben
bestehen, soweit die bekannten Standardkarten eindeutig erkannt werden.

Bei einer Neuinstallation wird direkt die vollständige aktuelle
Dashboard-Vorlage mit Template-Version 14 erzeugt.

Für `2.1.0-beta.1` steigt die Dashboard-Template-Version von 11 auf 12. Die
Migration ergänzt die PV-Learning-Diagnosewerte, den neuen Anwendungsschalter
und die Reset-Schaltfläche, ohne das übrige Dashboard pauschal zu ersetzen.

Für `2.1.0-beta.2` steigt die Dashboard-Template-Version von 12 auf 13. Die
gezielte Migration ergänzt in der vorhandenen Reglerstatus-Karte den Modus
**SOC-Ladeplan halten**. Eigene Anpassungen am übrigen Dashboard werden nicht
pauschal ersetzt.

Für `2.1.0-beta.3` steigt die Dashboard-Template-Version von 13 auf 14. Die
Migration ergänzt die Karte **PV-Prognose** sowie Forecast-Aktualisierungszeit,
wirksame Tagesprognose, prognostizierten End-SOC und Ladeplanbasis in den
Planungsdetails.

## 9. Erste Prüfung nach dem Update

Zunächst:

```text
Optimierer-Berechnung aktiv = Ein
NOAH-Steuerung aktiv = Aus
Dynamische SOC-Steuerung aktiv = Aus
Vorausschauende SOC-Freigabe aktiv = Aus
Betriebsart = Automatik
```

Im Dashboard beziehungsweise unter **Werkzeuge → Zustände** prüfen:

```text
Datenstatus
Dynamisches SOC-Soll
SOC-Abweichung
SOC-Ladeplan
Dynamisch erforderliche Ladeleistung
Prognosebasierter Mindest-SOC
SOC-Freigabegrenze
Freigebare Akkuenergie
SOC-Freigabe-Soll
```

Alle neuen Diagnosewerte werden auch bei ausgeschalteter SOC-Freigabe
berechnet. Es wird noch kein Stellbefehl an den NOAH gesendet.

### PV-Learning nach dem Neustart prüfen

Direkt nach dem Update sollte gelten:

```text
Gelernte PV-Korrektur verwenden = Aus
PV-Learning bereit              = Aus
PV-Lerntage                     = 0   # bei neuer Lernhistorie
```

Während PV-Erzeugung sollte **PV-Energie heute** ansteigen. Früh am Tag sollte
**PV-Prognosereferenz heute** einen plausiblen Wert erhalten. Nach jedem
vollständig ausgewerteten gültigen Lerntag steigt **PV-Lerntage**.

Die gelernte Korrektur erst einschalten, wenn mindestens drei Lerntage
vorliegen und der PV-Lernfaktor plausibel ist.

## 10. Dynamischen SOC-Ladeplan prüfen

Die Beta-10-Ladeplankurve bleibt unverändert. Beta 12 ändert lediglich die
Nachladeleistung, wenn der Ist-SOC mehr als 2 Prozentpunkte hinter dieser
Kurve liegt: Das Nachholziel wird bis zum Ende der eingestellten Nachholzeit
vorausberechnet.

Bei Mindest-SOC `10 %` und Ziel-SOC `100 %` liegt das reine Zeit-Soll ungefähr
bei:

```text
Sonnenaufgang    10 %
25 % des Tages   32,5 %
50 % des Tages   55 %
75 % des Tages   77,5 %
Sonnenuntergang 100 %
```

Eine knappe Restprognose darf diese Kurve progressiv nach oben ziehen, soll sie
aber morgens nicht allein deshalb sofort auf `100 %` setzen.

## 11. SOC-Freigabewerte plausibilisieren

Die neuen Werte beantworten drei verschiedene Fragen:

```text
Prognosebasierter Mindest-SOC
= Welchen SOC muss der Akku mindestens behalten, damit der Ziel-SOC mit der
  noch prognostizierten PV-Energie wieder erreichbar bleibt?

SOC-Freigabegrenze
= Bis zu welchem SOC darf die neue Freigabe maximal entladen?

Freigebare Akkuenergie
= Wie viel Batterieenergie liegt aktuell oberhalb dieser Grenze?
```

Für die SOC-Freigabe wird die Wiederaufladeenergie so berechnet:

```text
PV-Energie für Wiederaufladung
= wirksame Restprognose
  - zusätzliche Energiereserve
```

Der erwartete Hausenergiebedarf wird hierbei **nicht abgezogen**. Falls die
PV-Energie später zum Wiederaufladen des Akkus benötigt wird, darf der
Hausverbrauch in diesem Zeitraum aus dem Netz versorgt werden.

Die dynamische SOC-Sollkurve selbst bleibt unverändert und berücksichtigt
weiterhin den erwarteten Hausenergiebedarf. Die separat berechnete
SOC-Nachladeleistung verwendet dagegen das vorausberechnete Soll am Ende des
Nachholfensters.

Die Freigabegrenze wird aus dem größeren Wert von dynamischem SOC-Soll und
prognosebasiertem Mindest-SOC plus 2 Prozentpunkten Sicherheitsreserve gebildet.

Beispiel passend zu einem fast vollen Akku:

```text
Ist-SOC:                         100,0 %
Dynamisches SOC-Soll:             93,3 %
Wirksame Restprognose:             0,543 kWh
Zusätzliche Energiereserve:        0,250 kWh
Ladewirkungsgrad:                  0,90
Akkukapazität:                     2,048 kWh
```

Dann stehen für die spätere Wiederaufladung rechnerisch zur Verfügung:

```text
0,543 kWh - 0,250 kWh = 0,293 kWh PV-Energie
0,293 kWh × 0,90      = 0,264 kWh Batterieenergie
```

Das entspricht ungefähr `12,9` SOC-Prozentpunkten.

Damit ergibt sich bei Ziel-SOC `100 %`:

```text
Prognosebasierter Mindest-SOC:   ca. 87,1 %
Dynamisches SOC-Soll:                93,3 %
SOC-Freigabegrenze:              ca. 95,3 %
```

Bei `100 %` Ist-SOC sind damit ungefähr `4,7` SOC-Prozentpunkte freigebbar.
Bei einer Akkukapazität von `2,048 kWh` entspricht das rund `0,096 kWh`.

Sinkt die Restprognose so weit, dass nach Abzug der Energiereserve keine
Wiederaufladeenergie mehr vorhanden ist, steigt der prognosebasierte
Mindest-SOC bis zum Ziel-SOC. Dann wird keine zusätzliche Akkuenergie
freigegeben.

Wichtig: Die Grenze ist **prognosebasiert**. Sie kann das Ziel-SOC nicht
garantieren, wenn der reale PV-Ertrag später deutlich geringer als prognostiziert
ausfällt.

## 12. Dynamische SOC-Steuerung aktivieren

Erst nach plausibler Beobachtung:

```text
Dynamische SOC-Steuerung aktiv = Ein
Vorausschauende SOC-Freigabe aktiv = Aus
NOAH-Steuerung aktiv = Aus
```

Dadurch kann bereits geprüft werden, ob der berechnete Reglermodus bei einem
SOC-Rückstand auf:

```text
SOC-Nachladung
```

wechselt und wie sich der berechnete Ausgangssollwert ändert. Wegen der noch
ausgeschalteten NOAH-Steuerung wird der Sollwert nicht geschrieben.

## 13. Vorausschauende SOC-Freigabe testen

Anschließend:

```text
Dynamische SOC-Steuerung aktiv = Ein
Vorausschauende SOC-Freigabe aktiv = Ein
NOAH-Steuerung aktiv = Aus
Betriebsart = Automatik
```

Der Reglermodus **SOC-Freigabe** kann jetzt erscheinen, wenn:

- Forecast.Solar verfügbar ist
- es Tag ist
- der Ist-SOC über der SOC-Freigabegrenze liegt
- freigebare Akkuenergie vorhanden ist
- aktuell positiver Netzbezug vorliegt

Der berechnete **SOC-Freigabe-Sollwert** entspricht näherungsweise:

```text
aktuelle NOAH-Ausgangsleistung + aktueller Netzbezug
```

begrenzt durch die maximale Ausgangsleistung.

Der endgültige Ausgangssollwert wird weiterhin auf das konfigurierte
Stellgrößenraster gerundet. Ziel ist ein möglichst kleiner Netzbezug; eine
absichtliche Batterieeinspeisung ins Netz wird nicht angefordert. Kleine
kurzzeitige Abweichungen um 0 W können durch Messverzögerung, Lastsprünge und
das Stellgrößenraster entstehen.

## 14. SOC-Nachholzeit einstellen

Standard:

```text
2,0 h
```

Ein kleinerer Wert reagiert stärker auf einen SOC-Rückstand. Ein größerer Wert
verteilt das Nachladen über einen längeren Zeitraum.

Die Nachholzeit wirkt auf **SOC-Nachladung**, nicht direkt auf die neue
SOC-Freigabe.

## 15. Stellgröße manuell testen

Vor Aktivierung der NOAH-Steuerung unter **Werkzeuge → Aktionen** den Dienst:

```text
number.set_value
```

mit der ausgewählten `NOAH System Output Power`-Entität testen.

Beispiel bei Watt:

```yaml
action: number.set_value
target:
  entity_id: number.dein_noah_system_output_power
data:
  value: 300
```

Danach prüfen, ob die Stellgröße den Wert annimmt.

## 16. Aktive NOAH-Steuerung einschalten

Erst wenn Ladeplan und SOC-Freigabewerte plausibel sind:

```text
Optimierer-Berechnung aktiv = Ein
Dynamische SOC-Steuerung aktiv = Ein
Vorausschauende SOC-Freigabe aktiv = Ein
NOAH-Steuerung aktiv = Ein
Betriebsart = Automatik
```

Wenn die SOC-Freigabe noch nicht aktiv eingesetzt werden soll, kann ihr eigener
Schalter auf **Aus** bleiben.

## 17. Schutzmechanismen

Die aktive Steuerung enthält weiterhin:

- Schalt-Hysterese
- Stellgrößenraster
- Mindestabstand zwischen normalen Stellbefehlen
- Wiederholungsversuch
- 10-Minuten-Failsafe bei dauerhaft fehlenden kritischen Daten
- persistente Home-Assistant-Benachrichtigung
- Sperre gegen den Legacy-YAML-Controller

Seit Beta 12 schützt die SOC-Freigabe zusätzlich durch:

- dynamisches SOC-Soll
- prognosebasierten Mindest-SOC
- 2 Prozentpunkte SOC-Sicherheitsreserve
- Freigabe nur bei positivem Netzbezug
- Freigabe nur am Tag
- sofortige Sollwertreduzierung, wenn ein zuvor gesetzter SOC-Freigabe-Sollwert aus Sicherheitsgründen sinken muss
- sofortige Sollwertreduzierung im Modus **SOC-Ladeplan halten**, wenn die verfügbare PV-Leistung sinkt

## 18. Legacy-YAML-Optimizer

Der ältere YAML-Optimizer darf nicht gleichzeitig mit der aktiven
HACS-Steuerung denselben NOAH regeln.

Die HACS-Integration prüft:

```text
input_boolean.noah_optimizer_enabled
```

Steht dieser Helfer auf `on`, werden normale HACS-Stellbefehle blockiert.

Die dynamische SOC-Regelung und die vorausschauende SOC-Freigabe werden nicht
in die Legacy-YAML-Regelung zurückportiert.

## 19. Weiterführende Dokumentation

- [Konfiguration](configuration.md)
- [Fehlerbehebung](troubleshooting.md)
- [HACS Beta / Pre-Release](hacs-beta.md)


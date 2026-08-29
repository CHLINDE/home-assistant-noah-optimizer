# Konfiguration

Dieses Dokument beschreibt die HACS-Integration **Growatt NOAH Optimizer**
für den Pre-Release `2.1.0-beta.4`.

`2.1.0-beta.1` ergänzt auf Basis des stabilen Stands `2.0.0` passives,
persistentes PV-Learning. `2.1.0-beta.2` korrigiert zusätzlich die Automatik
bei aktivem dynamischem SOC-Ladeplan: Ein bereits erfüllter Ladeplan wird nicht
mehr durch die klassische Prognosemarge erneut in Ladepriorität versetzt.
`2.1.0-beta.3` verwendet bei einer nativen Forecast.Solar-Quelle zusätzlich
die vollständige zeitaufgelöste PV-Leistungskurve für den dynamischen SOC-
Ladeplan und zeigt diese Kurve im Dashboard an.
`2.1.0-beta.4` ergänzt eine datumsabhängige SOC-Ladeplan-Historie und
persistente Forecast-/Plan-Snapshots für die letzten 31 Tage.

Die tatsächlichen Entity-IDs können durch Bereichsnamen oder manuelle
Umbenennungen abweichen. Die Integration und das automatische Dashboard lösen
die eigenen Entitäten über stabile Unique IDs auf.

## 1. Schalter

### Optimierer-Berechnung aktiv

Aktiviert die Berechnung des Ausgangssollwerts.

Ist dieser Schalter aus, wird der Reglermodus auf `off` gesetzt und es werden
keine normalen Stellbefehle ausgeführt.

### NOAH-Steuerung aktiv

Gibt das aktive Schreiben auf die konfigurierte `NOAH System Output Power`-
Entität frei.

Standard:

```text
Aus
```

Berechnung und aktive Stellregelung sind absichtlich getrennt.

### Dynamische SOC-Steuerung aktiv

Seit Beta 8 verfügbar.

Die dynamische SOC-Berechnung läuft unabhängig von diesem Schalter, sodass die
neuen Sensoren zunächst beobachtet werden können.

Erst bei:

```text
Dynamische SOC-Steuerung aktiv = Ein
Betriebsart = Automatik
```

kann ein SOC-Rückstand den Ausgangssollwert beeinflussen.

Standard:

```text
Aus
```

Die Betriebsarten **Manuell**, **Eigenverbrauch** und **Ladepriorität** werden
durch diesen Schalter nicht verändert.

### Vorausschauende SOC-Freigabe aktiv

Neu in Beta 11.

Dieser Schalter erlaubt dem Optimizer, einen sicher prognostizierten
SOC-Vorsprung tagsüber zur Deckung von aktuellem Netzbezug zu nutzen. Ziel ist,
bei einem früh weit geladenen Akku wieder Ladekapazität für späteren
PV-Überschuss zu schaffen.

Standard:

```text
Aus
```

Die Freigabe wirkt nur bei:

```text
Dynamische SOC-Steuerung aktiv = Ein
Vorausschauende SOC-Freigabe aktiv = Ein
Betriebsart = Automatik
```

Die zusätzliche Abhängigkeit von der dynamischen SOC-Steuerung stellt sicher,
dass bei einer späteren Verschlechterung der Prognose auch die
**SOC-Nachladung** zur Verfügung steht.

Die Betriebsarten **Manuell**, **Eigenverbrauch**, **Ladepriorität** und die
Nachtregelung werden nicht verändert.

### Gelernte PV-Korrektur verwenden

Neu in `2.1.0-beta.1`.

Das PV-Learning selbst sammelt unabhängig von diesem Schalter Tagesdaten. Erst
wenn mindestens drei gültige Lerntage vorliegen und dieser Schalter
eingeschaltet ist, wird der gelernte PV-Faktor auf die Forecast.Solar-
Restprognose angewendet.

Standard:

```text
Aus
```

Dadurch verändert das PV-Learning allein das Regelverhalten nach dem Update
zunächst nicht. Die späteren Beta-Versionen können unabhängig davon weitere
Regelungsänderungen enthalten.

### PV-Lerndaten zurücksetzen

Die Schaltfläche löscht die gespeicherte Lernhistorie. Danach beginnt das
Learning wieder bei null und benötigt erneut mindestens drei gültige
Lerntage, bevor eine gelernte Korrektur wirksam werden kann.

## 2. Betriebsarten

Der Select **Betriebsart** bietet:

```text
Automatik
Eigenverbrauch
Ladepriorität
Manuell
```

### Automatik

Der Optimizer wählt seinen internen Reglermodus abhängig von:

- SOC
- Mindest-SOC
- Ziel-SOC
- PV-Restprognose
- erwarteter Hauslast
- Netzbezug beziehungsweise Einspeisung
- verbleibender Zeit bis Sonnenuntergang
- optional dem dynamischen SOC-Ladeplan

Mögliche interne Reglermodi sind:

```text
Aus
Manuell
Eigenverbrauch
Ladepriorität
SOC-Nachladung
SOC-Ladeplan halten
SOC-Freigabe
PV-Umlenkung
Mindest-SOC
Nachtbetrieb
Ziel-SOC erreicht
Konservativ ohne Prognose
Gleitende Reserve
```

### Eigenverbrauch

Die Ausgangsleistung wird so berechnet, dass der Netzbezug möglichst klein
bleibt und der gewünschte Rest-Netzbezug berücksichtigt wird.

### Ladepriorität

Ein Teil der verfügbaren PV-Leistung wird für das Erreichen des Ziel-SOC
reserviert. Die Ausgangsleistung wird entsprechend begrenzt.

### SOC-Ladeplan halten

Neu in `2.1.0-beta.2`. Dieser interne Automatikmodus wird verwendet, wenn die
dynamische SOC-Steuerung aktiv ist, Forecast-Daten verfügbar sind und der
Ist-SOC innerhalb der SOC-Toleranz im oder vor dem dynamischen Soll liegt.

Die klassische Prognosemarge wird in diesem Zustand nicht nochmals zur Wahl
der Ladepriorität herangezogen. Bei einer nativen Forecast.Solar-Kurve basiert
die dynamische Sollkurve bereits auf der zeitlichen wirksamen PV-Prognose
einschließlich Ladeeffizienz und Forecast-Energiereserve. Die erwartete Hauslast
wird nicht aus der nativen Ladeplan-Kurve abgezogen und bleibt separat in
Prognosemarge, Prognosedeckung und Ausgangsregelung berücksichtigt.

Der sichere Ausgangs-Rohwert lautet:

```text
SOC-Halten-Soll = min(PV-Leistung, Eigenverbrauchs-Soll)
```

Damit wird vorhandene PV-Leistung für das Haus genutzt, ohne absichtlich
Akkuenergie freizugeben. Der Sollwert wird auf das Stellgrößenraster abgerundet.
Eine gezielte Akkuentladung bleibt der optionalen **SOC-Freigabe** vorbehalten.

### Manuell

Der Parameter **Manuelle Ausgangsleistung** wird als Sollwert verwendet.

## 3. Dynamischer SOC-Ladeplan

Ab `2.1.0-beta.3` besitzt der Ladeplan zwei Berechnungswege. Ist die konfigurierte
**Forecast.Solar Restprognose heute** eine native Entität der Home-Assistant-
Integration Forecast.Solar, liest der NOAH Optimizer die bereits von Home
Assistant geladene vollständige Leistungskurve aus deren Config-Entry. Es
werden dabei keine zusätzlichen API-Abfragen ausgeführt.

Die wirksame Kurve wird aus Forecast.Solar-Leistung × Prognose-Sicherheitsfaktor
× optionalem PV-Lernfaktor gebildet. Für den SOC-Ladeplan wird die vollständige
wirksame PV-Kurve integriert; die erwartete Hauslast wird **nicht vorab von der
Forecast-Leistung abgezogen**. Dadurch bleibt PV auch dann als mögliche
Ladeenergie berücksichtigt, wenn die Regelung zeitweise den Hausverbrauch aus
dem Netz decken muss, um den Akku-Ladeplan einzuhalten. Ladewirkungsgrad und
Forecast-Energiereserve werden weiterhin berücksichtigt. Die erwartete Hauslast
bleibt Bestandteil von Prognosemarge, Prognosedeckung und Ausgangsregelung.

Der Ist-SOC und die tatsächlich gemessene PV-Leistung werden nicht verwendet,
um den Ladeplan nachträglich passend zu rechnen. Neue Ladepläne entstehen nur
durch neue Forecast.Solar-Daten oder geänderte Planungsparameter.

Kann keine native Forecast.Solar-Kurve ermittelt werden, bleibt der bisherige
zeitbasierte Algorithmus als **Tageslicht-Fallback** aktiv. Der Sensor
**Ladeplanbasis** zeigt `Forecast.Solar-Kurve` oder `Tageslicht-Fallback`.

### Zeitaufgelöster Ladeplan ab 2.1.0-beta.3

Die Forecast.Solar-Leistungspunkte bestimmen die zeitliche Form des Ladeplans.
Der Ladeplan steigt dort, wo Forecast.Solar PV-Energie erwartet. Bei einer
Süd-Anlage bleibt das dynamische Soll
daher am frühen Morgen niedrig und steigt erst mit der prognostizierten
Einstrahlung. Reicht die prognostizierte Tagesenergie nicht bis zum Ziel-SOC,
zeigt **Prognostizierter End-SOC** einen entsprechend niedrigeren Wert. Das
konfigurierte Ziel-SOC bleibt unverändert das Wunschziel.

Für die SOC-Nachladung wird auch der Sollpunkt am Ende der Nachholzeit aus
dieser Forecast-Kurve entnommen.

### Tageslicht-Fallback (Beta-10-Algorithmus)

Die folgenden Abschnitte 3.1 bis 3.5 beschreiben den weiterhin vorhandenen
Fallback, falls keine vollständige Forecast.Solar-Kurve verfügbar ist.

### 3.1 Tagesfortschritt

Für den Zeitraum zwischen Sonnenaufgang und Sonnenuntergang wird ein
Tagesfortschritt `p` berechnet:

```text
p = vergangene Zeit seit Sonnenaufgang / Tageslichtdauer
```

Der Wert wird auf `0 ... 1` begrenzt.

```text
Sonnenaufgang      p = 0
Tagesmitte         p ≈ 0,5
Sonnenuntergang    p = 1
```

Außerhalb der Tageslichtzeit wird für den SOC-Ladeplan `p = 0` verwendet.

### 3.2 Zeitbasiertes Grund-Soll

```text
Zeit-Soll
= Mindest-SOC
  + p × (Ziel-SOC - Mindest-SOC)
```

Beispiel mit Mindest-SOC `10 %` und Ziel-SOC `100 %`:

```text
p = 0,00  -> 10,0 %
p = 0,25  -> 32,5 %
p = 0,50  -> 55,0 %
p = 0,75  -> 77,5 %
p = 1,00  -> 100,0 %
```

Damit existiert unabhängig von kurzfristigen Schwankungen der Restprognose
eine nachvollziehbare Sollkurve über den Tag.

### 3.3 Verfügbare PV-Energie für den Akku

```text
PV-Energie für Akku
= wirksame Restprognose
  - erwarteter Hausenergiebedarf
  - zusätzliche Energiereserve
```

Negative Ergebnisse werden auf `0 kWh` begrenzt.

### 3.4 Prognose-Anforderung

Aus der verbleibenden PV-Energie wird weiterhin berechnet, wie viel SOC mit
dieser Energie voraussichtlich noch gewonnen werden kann:

```text
Speicherbare Energie
= PV-Energie für Akku × Ladewirkungsgrad

Möglicher SOC-Zuwachs
= Speicherbare Energie / nutzbare Akkukapazität × 100

Prognose-Anforderung
= Ziel-SOC - möglicher SOC-Zuwachs
```

Die Prognose-Anforderung wird auf den Bereich zwischen Mindest-SOC und
Ziel-SOC begrenzt.

Wichtig: Ab Beta 10 wird dieser Wert **nicht mehr direkt** als dynamisches
SOC-Soll verwendet.

### 3.5 Prognosedruck und dynamisches SOC-Soll

Liegt die Prognose-Anforderung über dem Zeit-Soll, entsteht Prognosedruck:

```text
Prognosedruck
= max(Prognose-Anforderung - Zeit-Soll, 0)
```

Das endgültige dynamische Soll lautet:

```text
Dynamisches SOC-Soll
= Zeit-Soll + p × Prognosedruck
```

und wird anschließend auf:

```text
Mindest-SOC <= dynamisches SOC-Soll <= Ziel-SOC
```

begrenzt.

Das bewirkt:

- bei ausreichender Restprognose folgt das Soll der zeitbasierten Grundkurve
- bei knapper Restprognose steigt das Soll früher und stärker
- morgens kann eine schlechte Prognose das Soll nicht sofort hart auf 100 % setzen
- spätestens bei Sonnenuntergang erreicht die Tageskurve den Ziel-SOC
- nachts fällt das dynamische Soll auf den Mindest-SOC zurück

### 3.6 SOC-Abweichung

```text
SOC-Abweichung
= Ist-SOC - dynamisches SOC-Soll
```

Tagsüber gilt eine feste Toleranz von 2 Prozentpunkten:

```text
mehr als +2 %-Punkte    = Vor Ladeplan
-2 bis +2 %-Punkte      = Im Ladeplan
weniger als -2 %-Punkte = Hinter Ladeplan
```

Im Nachtbetrieb ist diese Einteilung nicht sinnvoll, weil das dynamische
SOC-Soll auf den Mindest-SOC zurückfällt. Ab Beta 14 meldet der SOC-Ladeplan
deshalb während des Nachtbetriebs unabhängig von der numerischen Abweichung
den eigenen Zustand `night` beziehungsweise `Nachtbetrieb`.

### 3.7 Dynamisch erforderliche Ladeleistung

Liegt der Speicher hinter dem Ladeplan, wird die zum Aufholen des Rückstands
benötigte Ladeleistung berechnet.

Ab Beta 12 wird dabei berücksichtigt, dass das dynamische SOC-Soll während der
Nachholzeit weiter ansteigt. Das Nachholziel ist deshalb nicht mehr nur das
aktuelle dynamische SOC-Soll, sondern das vorausberechnete dynamische SOC-Soll
am Ende des Nachholfensters.

Das Nachholfenster ist:

```text
Nachholfenster
= min(SOC-Nachholzeit, verbleibende Zeit bis Sonnenuntergang)
```

Für die Projektion wird der Tageslichtfortschritt bis zum Ende dieses Fensters
weitergeführt. Die aktuell berechnete Prognose-Anforderung bleibt für diese
kurze Projektion konstant. Bei jedem Coordinator-Update wird sie mit den dann
aktuellen Forecast- und Zeitwerten neu berechnet.

Vereinfacht gilt:

```text
Nachholziel
= dynamisches SOC-Soll am Ende des Nachholfensters

SOC-Rückstand
= max(Nachholziel - Ist-SOC, 0)

Fehlende Batterieenergie
= Akkukapazität × SOC-Rückstand / 100

Benötigte PV-Energie
= fehlende Batterieenergie / Ladewirkungsgrad

Dynamische Ladeleistung
= benötigte PV-Energie / Nachholfenster
```

Die Nachladeleistung wird nur verwendet, wenn der Akku mehr als 2
Prozentpunkte hinter dem **aktuellen** dynamischen SOC-Soll liegt. Dadurch
bleibt die bestehende Einteilung in **Vor Ladeplan**, **Im Ladeplan** und
**Hinter Ladeplan** unverändert, während die aktive Nachladung ein bewegliches
Soll tatsächlich einholen kann.

### 3.8 Einfluss auf die Regelung

Nur wenn alle folgenden Bedingungen erfüllt sind, wird der Reglermodus
**SOC-Nachladung** aktiv:

- Optimierer-Berechnung ist aktiv
- Betriebsart ist **Automatik**
- Dynamische SOC-Steuerung ist aktiv
- Forecast.Solar ist verfügbar
- es ist Tag
- SOC liegt über dem Mindest-SOC
- SOC liegt unter dem Ziel-SOC
- der Speicher liegt mehr als 2 Prozentpunkte hinter dem dynamischen SOC-Soll

Dann wird für die Batterieladung mindestens der größere Wert aus:

```text
bisher erforderliche mittlere Ladeleistung
oder
dynamisch erforderliche Ladeleistung
```

reserviert.

Der NOAH-Ausgang wird entsprechend reduziert, ohne negative Ausgangsleistung
anzufordern.

### 3.9 Vorausschauende SOC-Freigabe

Beta 11 ergänzt die Gegenrichtung zur SOC-Nachladung. Beta 12 korrigiert
die dafür verwendete Wiederauflade-Reserve: Liegt der Akku sicher
**vor** dem Ladeplan, kann ein Teil dieses Vorsprungs für den Hausverbrauch
freigegeben werden.

#### Prognosebasierter Mindest-SOC

Für die SOC-Freigabe wird eine **eigene Wiederauflade-Reserve** berechnet.
Diese ist absichtlich nicht identisch mit der Prognose-Anforderung des
dynamischen Ladeplans.

Seit `2.1.0-beta.3` besitzt der dynamische Ladeplan zwei Berechnungswege:

- Bei der nativen **Forecast.Solar-Kurve** wird die vollständige wirksame
  PV-Kurve integriert. Der erwartete Hausenergiebedarf wird nicht vorab
  abgezogen; Ladeeffizienz und Forecast-Energiereserve bleiben berücksichtigt.
- Beim **Tageslicht-Fallback** bleibt die ältere konservative Berechnung aus
  wirksamer Restprognose abzüglich erwartetem Hausenergiebedarf und zusätzlicher
  Energiereserve aktiv.

Die SOC-Freigabe beantwortet eine andere Frage: Wie viel SOC darf jetzt
freigegeben werden, wenn die verbleibende prognostizierte PV-Energie später
notfalls zum Wiederaufladen des Akkus reserviert wird?

Dafür gilt:

```text
PV-Energie für Wiederaufladung
= wirksame Restprognose
  - zusätzliche Energiereserve
```

Negative Ergebnisse werden auf `0 kWh` begrenzt.

```text
Speicherbare Wiederaufladeenergie
= PV-Energie für Wiederaufladung × Ladewirkungsgrad

Möglicher Wiederauflade-SOC
= Speicherbare Wiederaufladeenergie
  / nutzbare Akkukapazität × 100

Prognosebasierter Mindest-SOC
= Ziel-SOC - möglicher Wiederauflade-SOC
```

Der Wert wird auf Mindest-SOC bis Ziel-SOC begrenzt.

Der **erwartete Hausenergiebedarf wird bei dieser Wiederauflade-Reserve nicht
abgezogen**. Das ist beabsichtigt. Wenn die prognostizierte PV-Energie später
zum Wiederaufladen des Akkus benötigt wird, kann der Hausverbrauch in diesem
Zeitraum gegebenenfalls aus dem Netz versorgt werden.

Dadurch führt eine negative normale Prognosemarge nicht mehr automatisch dazu,
dass der prognosebasierte Mindest-SOC der Freigabe auf `100 %` steigt und ein
voller Akku überhaupt nicht freigegeben werden kann.

#### SOC-Freigabegrenze

Für die Freigabe wird der konservativere der beiden SOC-Werte verwendet:

```text
Basis-Freigabegrenze
= max(Dynamisches SOC-Soll, Prognosebasierter Mindest-SOC)
```

Zusätzlich werden die bereits für den SOC-Ladeplan verwendeten 2
Prozentpunkte Toleranz als Sicherheitsreserve aufgeschlagen:

```text
SOC-Freigabegrenze
= min(Basis-Freigabegrenze + 2 %-Punkte, 100 %)
```

Damit wird der Akku durch die vorausschauende Freigabe nicht absichtlich bis
auf den eigentlichen Ladeplan heruntergezogen, sondern behält einen kleinen
Puffer.

#### Freigebare Akkuenergie

```text
Freigebarer SOC
= max(Ist-SOC - SOC-Freigabegrenze, 0)

Freigebare Akkuenergie
= Akkukapazität × Freigebarer SOC / 100
```

Nur dieser Anteil wird als sicher freigebar betrachtet.

#### SOC-Freigabe-Soll

Liegt gleichzeitig realer Netzbezug vor, wird der NOAH-Ausgang um diesen
Netzbezug erhöht:

```text
SOC-Freigabe-Soll
= aktuelle NOAH-Ausgangsleistung + max(Netzleistung, 0)
```

Der Wert wird auf die konfigurierte maximale Ausgangsleistung begrenzt und
anschließend wie alle anderen Ausgangssollwerte auf das Stellgrößenraster
gerundet.

Ziel ist, den aktuellen Netzbezug möglichst weit aus dem sicheren SOC-Vorsprung
zu decken. Es wird keine absichtliche Entladung zum Zweck einer Netzeinspeisung
angefordert. Durch Stellgrößenraster, Messverzögerung und Lastsprünge können
kurzfristig dennoch kleine Abweichungen um 0 W auftreten.

#### Aktivierungsbedingungen

Der Reglermodus **SOC-Freigabe** wird nur aktiv, wenn gleichzeitig:

- Optimierer-Berechnung aktiv ist
- Betriebsart **Automatik** gewählt ist
- Dynamische SOC-Steuerung aktiv ist
- Vorausschauende SOC-Freigabe aktiv ist
- Forecast.Solar verfügbar ist
- es Tag ist
- der Ist-SOC über der SOC-Freigabegrenze liegt
- freigebare Akkuenergie größer als `0 kWh` vorhanden ist
- aktuell Netzbezug vorliegt

**SOC-Nachladung** hat Vorrang vor **SOC-Freigabe**. Die beiden Zustände können
aufgrund ihrer entgegengesetzten SOC-Bedingungen normalerweise nicht
zeitgleich aktiv sein.

#### Prognosegrenze

Die Schutzwirkung bleibt prognosebasiert. Die SOC-Freigabe entlädt nicht
absichtlich unter den höheren Wert aus:

- dynamischem SOC-Soll
- prognosebasiertem Mindest-SOC für die Wiederaufladung
- zusätzlicher 2-Prozentpunkte-Sicherheitsreserve

Dabei gelten bewusst zwei unterschiedliche Prognosebetrachtungen:

```text
Dynamischer Ladeplan:
Restprognose - erwarteter Hausenergiebedarf - Energiereserve

SOC-Freigabe:
Restprognose - Energiereserve
```

Die zweite Betrachtung setzt voraus, dass verbleibende PV-Energie bei Bedarf
für das Wiederaufladen des Akkus priorisiert werden darf. Dadurch kann später
Netzbezug für den Hausverbrauch entstehen. Das ist Teil der beabsichtigten
Strategie, weil so jetzt Akkuenergie genutzt und gleichzeitig Aufnahmefähigkeit
für späteren PV-Überschuss geschaffen werden kann.

Ändert sich die Prognose, wird die Freigabegrenze neu berechnet. Sinkt die
erwartete Wiederaufladeenergie, steigt der prognosebasierte Mindest-SOC und die
Freigabe endet früher.

Die Berechnung ist keine absolute Garantie. Ist Forecast.Solar zu optimistisch,
kann der Ziel-SOC am Abend trotz Schutzgrenze unterschritten werden.

Wurde der letzte Stellbefehl im Modus **SOC-Freigabe** gesendet und muss der
Sollwert anschließend sinken, wird diese Reduzierung als sicherheitsrelevant
behandelt. Sie umgeht die normale 2-Minuten-Wartezeit und die übliche
Schalt-Hysterese, damit eine steigende Freigabegrenze oder sinkende Hauslast
nicht unnötig lange mit dem alten höheren Entladesollwert weiterläuft.

#### Schnellere Lastnachführung ab Beta 13

Die SOC-Freigabe reagiert auf den **aktuellen positiven Netzbezug** und muss
deshalb schneller nachgeführt werden als die prognosegetriebenen normalen
Regelzustände. Ab Beta 13 gilt:

```text
Controller-Auswertung:                 15 s
Normale Stellbefehle:                 120 s Mindestabstand
Sollwerterhöhung bei SOC-Freigabe:     30 s Mindestabstand
SOC-Freigabe-Deadband:             max. 25 W
Sollwertreduzierung nach Freigabe:   sofort möglich
```

Ist die konfigurierte Schalt-Hysterese kleiner als `25 W`, wird auch während
der SOC-Freigabe der kleinere konfigurierte Wert verwendet. Das
**Stellgrößenraster** bleibt unverändert maßgeblich; bei einem Raster von
beispielsweise `50 W` werden deshalb weiterhin nur entsprechend gerasterte
Sollwerte angefordert.

Die schnellere 15-Sekunden-Auswertung ändert den Mindestabstand der normalen
Betriebsarten nicht. Sie ermöglicht lediglich, eine aktive SOC-Freigabe bei
veränderter Hauslast zeitnah neu zu bewerten.

### 3.10 PV-Umlenkung ab Beta 14

Die PV-Umlenkung löst einen von der SOC-Freigabe getrennten Fall. Wenn der
Akku bereits mindestens am dynamischen SOC-Soll liegt, gleichzeitig noch lädt
und dennoch Netzbezug besteht, soll der Netzbezug nicht nur deshalb bestehen
bleiben, damit die Akkuladung höher bleibt.

Die maximal umlenkbare Leistung ist deshalb:

```text
PV-Umlenkungsleistung
= min(aktueller Netzbezug, aktuelle Akkuladeleistung)
```

Der Roh-Sollwert lautet:

```text
PV-Umlenkungs-Soll
= aktuelle NOAH-Ausgangsleistung + PV-Umlenkungsleistung
```

Danach gelten weiterhin maximale Ausgangsleistung und Stellgrößenraster.
Für die PV-Umlenkung wird der endgültige Sollwert auf das Raster **abgerundet**.
Dadurch kann das Rastern den sicheren Rohwert nicht überschreiten und nicht
allein durch Aufrundung eine absichtliche Akkuentladung anfordern. Ergibt das
Raster keinen Sollwert oberhalb der aktuell gemessenen NOAH-Ausgangsleistung,
wird die PV-Umlenkung für diesen Zyklus nicht aktiviert.

Aktivierungsbedingungen:

- Optimierer-Berechnung aktiv
- Betriebsart **Automatik**
- Dynamische SOC-Steuerung aktiv
- Forecast verfügbar
- Tagbetrieb
- Ist-SOC größer oder gleich dynamischem SOC-Soll
- Akkuladeleistung größer als `0 W`
- positiver Netzbezug
- keine aktive SOC-Nachladung

Die PV-Umlenkung benötigt den Schalter **Vorausschauende SOC-Freigabe aktiv**
**nicht**, weil sie keine absichtliche Akkuentladung anfordert. Sie reduziert
lediglich die gleichzeitig vorhandene Akkuladung.

Die Priorität in der Automatik ist dabei:

```text
Mindest-SOC / Nacht
SOC-Nachladung
SOC-Freigabe
PV-Umlenkung
restliche Prognose-/Ladeprioritätslogik
```

Ist der SOC so weit voraus, dass die separate SOC-Freigabe zulässig ist, darf
diese weiterhin auch zusätzliche Akkuenergie einsetzen. Andernfalls kann die
PV-Umlenkung zumindest den Anteil des Netzbezugs beseitigen, der gleichzeitig
als Akkuladung vorhanden ist.

#### Schnelle Lastnachführung

Ab Beta 14 gelten die schnelleren Lastfolgeparameter sowohl für
**SOC-Freigabe** als auch für **PV-Umlenkung**:

```text
Controller-Auswertung:                  15 s
Normale Stellbefehle:                  120 s Mindestabstand
SOC-Freigabe / PV-Umlenkung:            30 s Mindestabstand
Deadband in Lastfolgemodi:          max. 25 W
Sollwertreduzierung nach Lastfolgemodus: sofort möglich
```

## 4. Parameter

### Nutzbare Akkukapazität

Standard:

```text
2,048 kWh
```

Gesamte nutzbare Kapazität der angeschlossenen NOAH-Speicher.

### Ziel-SOC bei Sonnenuntergang

Standard:

```text
95 %
```

### Mindest-SOC

Standard:

```text
10 %
```

### Angenommener Ladewirkungsgrad

Standard:

```text
0,90
```

### Prognose-Sicherheitsfaktor

Standard:

```text
0,80
```

Der Prognose-Sicherheitsfaktor bleibt die bewusst konfigurierte konservative
Bewertung der Forecast.Solar-Prognose. Ohne angewendetes PV-Learning gilt:

```text
wirksamer Prognosefaktor
= Prognose-Sicherheitsfaktor

wirksame Restprognose
= Restprognose × Prognose-Sicherheitsfaktor
```

Beispiel:

```text
Restprognose:                5,0 kWh
Prognose-Sicherheitsfaktor:  0,80
Wirksame Restprognose:       4,0 kWh
```

Ist PV-Learning bereit und **Gelernte PV-Korrektur verwenden** aktiviert:

```text
wirksamer Prognosefaktor
= Prognose-Sicherheitsfaktor × PV-Lernfaktor

wirksame Restprognose
= Restprognose × wirksamer Prognosefaktor
```

### PV-Learning

PV-Learning verwendet keine zusätzliche Quellentität. Es nutzt:

- NOAH Solar Power
- Forecast.Solar Restprognose heute
- Sun-Integration

Die tatsächliche PV-Energie wird aus der NOAH-Solarleistung zeitlich
integriert. Für einen gültigen Lerntag gilt:

```text
Tagesverhältnis
= tatsächlicher PV-Ertrag / PV-Prognosereferenz
```

Die letzten maximal sieben gültigen Tagesverhältnisse werden persistent
gespeichert. Ihr Median ergibt den PV-Lernfaktor.

```text
Lernfenster:                    7 gültige Tage
Mindestens erforderlich:        3 gültige Tage
Lernfaktor pro Tag:             0,50 ... 1,50
Maximale Tages-Messlücke:       10 Minuten
Mindestbeobachtungszeit:        2 Stunden Tagesbetrieb
Mindest-Tageslichtfortschritt:  85 %
```

Die Prognosereferenz wird möglichst früh am Tag aus der Forecast.Solar-
Restprognose gebildet. Startet die Beobachtung kurz nach Sonnenaufgang, wird
der bereits gemessene PV-Ertrag zur Restprognose addiert, um eine angenäherte
Tagesreferenz zu erhalten. Vor Sonnenaufgang kann eine verfügbare Restprognose
als Referenz übernommen werden. Sobald die Tagesbeobachtung begonnen hat, wird
nachts keine neue Referenz mehr angelegt; ein Restwert nach Sonnenuntergang
kann damit nicht versehentlich zur Tagesreferenz werden.

Ein erster deutlich zu spät begonnener Teil-Tag wird nicht gelernt. Zusätzlich
muss ein gültiger Lerntag mindestens 85 % des Tageslichtfensters erreicht haben.
Eine Messlücke von mehr als zehn Minuten, die die Tagesbeobachtung berührt,
verwirft den gesamten Lerntag statt die fehlende PV-Produktion als Nullertrag
zu behandeln.

Das Learning läuft passiv. Der gelernte Faktor beeinflusst die Regelung erst,
wenn **Gelernte PV-Korrektur verwenden** eingeschaltet ist und mindestens drei
gültige Lerntage vorliegen.

### Zusätzliche Energiereserve

Standard:

```text
0,25 kWh
```

### Freigabemarge

Standard:

```text
0,50 kWh
```

### Erwartete mittlere Hauslast

Standard:

```text
250 W
```

### Gewünschter Rest-Netzbezug

Standard:

```text
50 W
```

### Maximale Ausgangsleistung

Standard:

```text
800 W
```

### Maximale Ausgangsleistung nachts

Standard:

```text
400 W
```

### Manuelle Ausgangsleistung

Standard:

```text
200 W
```

### Stellgrößenraster

Standard:

```text
50 W
```

### Schalt-Hysterese

Standard:

```text
50 W
```

### SOC-Nachholzeit

Seit Beta 8 verfügbar.

Standard:

```text
2,0 h
```

Bereich:

```text
0,5 ... 6,0 h
```

Ein kleinerer Wert reagiert aggressiver auf einen SOC-Rückstand. Ein größerer
Wert verteilt das Nachladen über einen längeren Zeitraum.

## 5. Wichtige berechnete Sensoren

### Netzleistung

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

### Netzbezug / Netzeinspeisung

Aus der saldierten Netzleistung abgeleitete positive Richtungswerte.

### Hauslast

Näherungsweise:

```text
Hauslast = Netzleistung + NOAH-Ausgangsleistung
```

### Batterieleistung

Kombinierter Batteriefluss. Positive Werte entsprechen Entladung, negative
Werte Ladung.

Für das Dashboard werden zusätzlich die getrennten Sensoren **Ladeleistung**
und **Entladeleistung** verwendet.

### Netzleistung 5 min

Zeitgewichteter gleitender Mittelwert der Netzleistung.

### Ladebedarf

Noch erforderliche Energie zum Ziel-SOC unter Berücksichtigung des
Ladewirkungsgrads.

### Wirksame Restprognose

Forecast.Solar-Restprognose multipliziert mit dem **wirksamen
Prognosefaktor**. Ohne aktive gelernte Korrektur entspricht dieser dem
Prognose-Sicherheitsfaktor. Mit bereitem und aktiviertem PV-Learning ist er
das Produkt aus Prognose-Sicherheitsfaktor und PV-Lernfaktor.

### PV-Prognosekurve

Tagesenergie der nativen Forecast.Solar-Kurve. Die Entität enthält zusätzlich
die Attribute `raw_power`, `effective_power` und `soc_plan`, die vom
automatischen Dashboard für die Zeitreihendarstellung verwendet werden.

### Wirksame Tagesprognose

Tagesenergie der Forecast.Solar-Kurve nach Prognose-Sicherheitsfaktor und
optionalem PV-Lernfaktor.

### PV-Prognose aktualisiert

Zeitstempel des Zustandsupdates der als Restprognose ausgewählten
Forecast.Solar-Entität. Er zeigt im Dashboard, auf welchem Forecast-Stand die
aktuelle Kurve basiert.

### Prognostizierter End-SOC

Endpunkt des aus der aktuellen Forecast.Solar-Kurve abgeleiteten SOC-Ladeplans.
Liegt er unter dem Ziel-SOC, reicht die aktuelle Prognose unter den
konfigurierten Annahmen nicht für das Wunschziel.

### Ladeplanbasis

Enum-Sensor mit:

```text
forecast_curve      = Forecast.Solar-Kurve
daylight_fallback   = Tageslicht-Fallback
```

### PV-Lernfaktor

Median der letzten maximal sieben gültigen Tagesverhältnisse. Vor dem ersten
gültigen Lerntag wird `1,0` angezeigt.

### Wirksamer Prognosefaktor

Tatsächlich auf Forecast.Solar angewendeter Faktor. Solange die gelernte
Korrektur ausgeschaltet oder noch nicht bereit ist, entspricht er dem
Prognose-Sicherheitsfaktor.

### PV-Lerntage

Anzahl der aktuell gespeicherten gültigen Lerntage, maximal sieben.

### Letztes PV-Tagesverhältnis

Unbegrenztes Verhältnis aus gemessenem PV-Tagesertrag und der zugehörigen
Prognosereferenz des zuletzt abgeschlossenen gültigen Lerntags.

### PV-Energie heute

Aus der NOAH-Solarleistung integrierter PV-Ertrag des laufenden Tages.

### PV-Prognosereferenz heute

Früh am Tag erfasste beziehungsweise angenäherte Forecast.Solar-Tagesreferenz
für das aktuelle Learning.

### PV-Learning bereit

Ist **Ein**, sobald mindestens drei gültige Lerntage gespeichert sind.

### Erwarteter Hausenergiebedarf

Abschätzung aus verbleibender Zeit bis Sonnenuntergang und erwarteter mittlerer
Hauslast.

### Prognosemarge

Verbleibende Energiemarge nach Ladebedarf, erwartetem Hausenergiebedarf und
zusätzlicher Reserve.

### Prognosedeckung

Prozentuale Deckung des erwarteten Restbedarfs durch die wirksame Prognose.

### Dynamisches SOC-Soll

Zeit- und prognoseabhängiger SOC-Sollwert für den aktuellen Zeitpunkt.

### SOC-Abweichung

Ist-SOC minus dynamisches SOC-Soll.

### SOC-Ladeplan

Enum-Sensor mit:

```text
ahead     = Vor Ladeplan
on_track  = Im Ladeplan
behind    = Hinter Ladeplan
night     = Nachtbetrieb
```

Die ersten drei Zustände gelten für den Tages-Ladeplan. `night` wird gesetzt,
sobald dieselbe Nachtbedingung gilt, die auch den Reglermodus `Nachtbetrieb`
aktiviert. Die numerische SOC-Abweichung wird dadurch nicht verändert.

### Dynamisch erforderliche Ladeleistung

Zusätzliche Ladeleistung zum Aufholen eines SOC-Rückstands. Ab Beta 12 wird
dafür das vorausberechnete dynamische SOC-Soll am Ende des Nachholfensters
verwendet, damit die Nachladung einer steigenden Sollkurve nicht dauerhaft
hinterherläuft.

### Prognosebasierter Mindest-SOC

Mindest-SOC für die vorausschauende Wiederaufladung. Er wird aus wirksamer
Restprognose minus zusätzlicher Energiereserve berechnet. Der erwartete
Hausenergiebedarf wird bei diesem Freigabe-Diagnosewert bewusst nicht
abgezogen.

### SOC-Freigabegrenze

Untergrenze, bis zu der die vorausschauende SOC-Freigabe den Akku maximal
nutzen darf. Sie berücksichtigt dynamisches SOC-Soll, prognosebasierten
Mindest-SOC und 2 Prozentpunkte Sicherheitsreserve.

### Freigebare Akkuenergie

Batterieenergie oberhalb der aktuellen SOC-Freigabegrenze.

### SOC-Freigabe-Soll

NOAH-Ausgangssollwert, der bei aktiver SOC-Freigabe den aktuellen positiven
Netzbezug möglichst aus dem sicheren SOC-Vorsprung decken soll.

### Ausgangssollwert

Endgültiger berechneter NOAH-Sollwert nach Betriebsart, Grenzwerten,
dynamischer SOC-Regelung und Stellgrößenraster.

## 6. Controllerdiagnose

Ab Beta 14 gibt es einen eigenen Enum-Sensor **Controllerstatus**. Seine
Zustände werden über die Integrationsübersetzungen lokalisiert und stehen damit
auch außerhalb des NOAH-Dashboards sauber zur Verfügung.

Der Schalter **NOAH-Steuerung aktiv** behält aus Kompatibilitätsgründen die
Attribute:

```text
control_status
last_command_target
last_command_at
```

Der neue Sensor und das Attribut `control_status` verwenden dieselben Rohwerte.
Typische Werte:

| Status | Bedeutung |
|---|---|
| `disabled` | Aktive Steuerung aus |
| `optimizer_disabled` | Berechnung aus |
| `legacy_controller_active` | Legacy-YAML-Regler blockiert HACS |
| `critical_data_missing` | Kritische Messwerte fehlen |
| `actuator_unavailable` | Stellgröße nicht erreichbar |
| `target_unavailable` | Kein gültiger Sollwert |
| `rate_limited` | Ein erforderlicher Stellbefehl wartet noch auf seinen Mindestabstand |
| `waiting_for_retry` | Warte auf Stellwertübernahme; der gewünschte Sollwert wurde bereits gesendet, ist an der Stellgröße aber noch nicht bestätigt |
| `in_sync` | Stellgröße liegt innerhalb der Hysterese |
| `command_sent` | Stellbefehl gesendet |
| `command_failed` | Stellbefehl fehlgeschlagen |
| `failsafe` | Failsafe aktiv |

## 7. Failsafe

Fehlen kritische Messwerte zehn Minuten ununterbrochen, während die aktive
Steuerung eingeschaltet ist:

1. Home Assistant erzeugt eine persistente Benachrichtigung.
2. Ist die Stellgröße erreichbar, versucht die Integration `0 W` zu setzen.
3. Ist sie nicht erreichbar, wird die Warnung trotzdem erzeugt.
4. Nach Wiederkehr der Daten werden Failsafe-Zustand und Benachrichtigung
   zurückgesetzt.

## 8. Legacy-Sperre

Existiert:

```text
input_boolean.noah_optimizer_enabled
```

und steht auf `on`, blockiert die HACS-Steuerung normale Ausgangsbefehle.

Legacy-YAML-Optimizer und HACS-Controller dürfen nicht gleichzeitig aktiv
denselben NOAH steuern.

## 9. Dashboard

Ab `2.1.0-beta.3` zeigt das Dashboard zusätzlich eine Karte **PV-Prognose**
mit Forecast.Solar-Leistung, wirksamer korrigierter Prognose und realer
PV-Leistung. Der Aktualisierungszeitpunkt, der prognostizierte End-SOC und die
Ladeplanbasis werden in den Planungsdetails angezeigt. Beta 3 führte dafür
Dashboard-Template-Version 14 ein; der aktuelle `2.1.0-beta.4`-Stand verwendet
nach Historienkarte und vollständiger Serienfarben-Migration **Template-Version 17**.


Das automatische Dashboard verwendet für Power Flow Card Plus:

```text
Grid:
consumption = Netzbezug
production  = Netzeinspeisung

Battery:
consumption = Entladeleistung
production  = Ladeleistung
```

Damit entspricht die animierte Richtung dem realen Energiefluss.

Seit Beta 8 enthält das Dashboard außerdem:

- Dynamische SOC-Steuerung aktiv
- Dynamisches SOC-Soll
- SOC-Abweichung
- SOC-Ladeplan
- Dynamisch erforderliche Ladeleistung
- SOC-Nachholzeit
- Diagramm mit Ist-SOC, dynamischem SOC-Soll und Ziel-SOC

Beta 11 ergänzt:

- Vorausschauende SOC-Freigabe aktiv
- Prognosebasierter Mindest-SOC
- SOC-Freigabegrenze
- Freigebare Akkuenergie
- SOC-Freigabe-Soll
- Reglermodus `SOC-Freigabe`

Ein bestehendes Dashboard wird gezielt migriert und nicht vollständig durch
die Standardvorlage ersetzt.

Beta 11 erhöht wegen der neuen Dashboardelemente die Dashboard-Template-Version
von 9 auf 10. Bestehende Benutzeranpassungen werden nicht pauschal
überschrieben.

Beta 12 und Beta 13 verändern die Dashboard-Struktur nicht und verwenden
Template-Version 10. Beta 14 erhöht die Dashboard-Template-Version auf 11.
Die Migration ergänzt `Nachtbetrieb` für den SOC-Ladeplan, `PV-Umlenkung` als
Reglermodus und stellt die Controllerstatus-Zeile auf den neuen Enum-Sensor um.
Die Controllerstatus-Texte kommen dadurch zentral aus den Übersetzungsdateien.
Benutzeranpassungen am übrigen Dashboard werden nicht pauschal ersetzt.

`2.1.0-beta.1` erhöht die Dashboard-Template-Version von 11 auf 12. Ergänzt
werden die PV-Learning-Diagnosewerte, **Gelernte PV-Korrektur verwenden** und
**PV-Lerndaten zurücksetzen**. Auch diese Migration ergänzt nur gezielt die
neuen Zeilen und ersetzt das übrige gespeicherte Dashboard nicht.


### Dashboard-Migration in 2.1.0-beta.2

`2.1.0-beta.2` erhöht die Dashboard-Template-Version von 12 auf 13. Bestehende
Reglerstatus-Karten erhalten automatisch die Anzeige für den neuen internen
Modus `soc_hold` als **SOC-Ladeplan halten** beziehungsweise **Hold SOC
schedule**. Es werden keine neuen Entitäten benötigt.

## Historische Ladeplanansicht ab 2.1.0-beta.4

Für die Historienansicht ist keine zusätzliche Benutzerkonfiguration nötig.
Die Integration lädt die Home-Assistant-Komponenten `frontend` und `history` als
Abhängigkeiten. `history` verwendet den Recorder für die tatsächlich aufgezeichneten
Zustände; `frontend` stellt die mitgelieferte Historienkarte bereit.

Die mitgelieferte Karte zeigt für das gewählte Datum:

```text
Ist-SOC
Dynamisches Soll
Ziel-SOC
Gespeicherter Planstand (falls vorhanden)
```

Der aktuelle Tag ist voreingestellt. Über Vor/Zurück, **Heute** und ein
Datumsfeld kann der dargestellte Tag gewechselt werden.

### Persistente Plan-Snapshots

Bei einer inhaltlichen Änderung der nativen Forecast.Solar-Kurve oder eines
planungsrelevanten Parameters speichert der Optimizer einen Snapshot des
Forecasts und des vollständigen daraus resultierenden SOC-Plans. Identische
Pläne werden nicht doppelt gespeichert.

Aufbewahrung:

```text
31 Kalendertage
maximal 48 unterschiedliche Snapshots je Tag
```

Die Daten liegen in Home Assistants `.storage` und werden beim Entfernen alter
Tage rollierend bereinigt. Die Snapshot-Historie wird nicht für die Regelung
verwendet; sie dient ausschließlich der späteren Nachvollziehbarkeit.

## Feste Dashboard-Serienfarben

Ab dem aktuellen `2.1.0-beta.4`-Stand verwendet das erzeugte Dashboard eine
feste Serienpalette. Dadurch bleiben Kurven auch nach Dashboard-Migrationen und
ApexCharts-Änderungen visuell eindeutig.

Für die SOC-Historie gilt:

```text
Ist-SOC             #2196F3
Dynamisches Soll    #009B21
Ziel-SOC            #FF6A00
Gespeicherter Plan  #FFD800
```

Das Diagramm **Reglerverhalten** verwendet Blau `#2196F3`, Grün `#009B21`,
Orange `#FF6A00`, Gelb `#FFD800`, Cyan `#00FFFF` und Violett `#B200FF`.
Bei der Migration auf Dashboard-Template-Version 17 werden fehlende Farben
ergänzt. Zusätzlich wird ausschließlich der frühere NOAH-Standard
Ziel-SOC Rot `#F44336` auf Orange `#FF6A00` umgestellt; andere manuell
gesetzte Farben werden nicht überschrieben.

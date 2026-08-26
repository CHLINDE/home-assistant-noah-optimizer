# Home Assistant Growatt NOAH Optimizer

Prognosebasierte Steuerung der Ausgangsleistung eines Growatt NOAH 2000
über Home Assistant und Noah-MQTT.

> **Status:** Stabiler Release `2.0.0`. Aktueller Pre-Release:
> `2.1.0-beta.3` mit zeitaufgelöster Forecast.Solar-Kurve und prognosebasiertem SOC-Ladeplan.
> Die aktive Steuerung kann die NOAH-Ausgangsleistung verändern. Vor der
> Aktivierung sollten Quellwerte, Netzvorzeichen und Stellgröße geprüft werden.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

## Ziele

- Netzbezug reduzieren
- unnötige PV-Einspeisung bei noch aufnahmefähigem Speicher reduzieren
- Akku bis zum Abend auf einen konfigurierbaren Ziel-SOC laden
- Nachtentladung bis zu einem Mindest-SOC ermöglichen
- Forecast.Solar in die Ladeplanung einbeziehen
- dynamischen SOC-Ladeplan aus der zeitaufgelösten Forecast.Solar-Kurve ableiten
- systematische Abweichungen zwischen Forecast.Solar und realem PV-Ertrag automatisch lernen
- Regelzustand, Prognose und Energiefluss in einem Dashboard darstellen

## HACS-Integration

Eine HACS-kompatible Custom Integration ist verfügbar.

Aktuelle stabile Version:

```text
2.0.0
```

Version `2.0.0` übernimmt den Funktionsstand von `2.0.0-beta.14` unverändert.
Gegenüber Beta 14 wurden keine Berechnungs- oder Regelalgorithmen geändert;
nur Versionierung und Release-Dokumentation wurden auf den stabilen Stand
umgestellt.

Aktueller Pre-Release:

```text
2.1.0-beta.3
```

`2.1.0-beta.1` ergänzt ein zunächst passiv arbeitendes **PV-Learning**. Es
vergleicht den gemessenen PV-Tagesertrag mit Forecast.Solar, bildet aus bis zu
sieben gültigen Tagen einen robusten Lernfaktor und kann diesen optional auf
die bestehende Restprognose anwenden. Die Anwendung ist nach dem Update
standardmäßig ausgeschaltet.

`2.1.0-beta.2` korrigiert zusätzlich die Automatik bei aktivem dynamischem
SOC-Ladeplan. Liegt der Ist-SOC im oder über dem dynamischen Soll, wird die
alte Prognosemarge nicht nochmals als Ladepriorität ausgewertet. Der neue
interne Reglermodus **SOC-Ladeplan halten** nutzt die aktuell verfügbare
PV-Leistung für den Hausverbrauch, ohne absichtlich Akkuenergie freizugeben.
Eine bewusste Akkuentladung bleibt Aufgabe der optionalen SOC-Freigabe.

`2.1.0-beta.3` ersetzt bei einer nativen Forecast.Solar-Quelle die bisherige
zeitbasierte SOC-Sollkurve durch einen **zeitaufgelösten PV-Ladeplan**. Die
Integration verwendet die bereits von Home Assistant geladene Forecast.Solar-
Leistungskurve und erzeugt daraus – unter Berücksichtigung von Prognosefaktor,
optionalem PV-Lernfaktor, erwarteter Hauslast, Ladeeffizienz und Energiereserve –
den dynamischen SOC-Verlauf. Es erfolgen keine zusätzlichen Forecast.Solar-API-
Aufrufe. Das Dashboard zeigt Forecast.Solar, wirksame Prognose und reale PV-
Leistung einschließlich des Aktualisierungszeitpunkts. Ist keine native
Forecast.Solar-Kurve verfügbar, bleibt der bisherige Tageslicht-Ladeplan als
Fallback aktiv.

Ab Beta 5 kann die Integration den berechneten Sollwert optional aktiv an
`NOAH System Output Power` übertragen.

Ab Beta 6 wird zusätzlich ein eigenes Lovelace-Dashboard erzeugt.

Beta 7 korrigiert die Batterie-Flussrichtung im Dashboard.

Beta 8 ergänzt einen dynamischen SOC-Ladeplan. Die neue Regelungsfunktion ist
nach dem Update standardmäßig ausgeschaltet und kann zunächst rein beobachtet
werden.

Beta 9 behebt einen Fehler in der Dashboard-Migration von Beta 8. Bei bereits
migrierten Installationen konnte die Karte **Reglerstatus** wegen eines
fehlerhaften Jinja-Ausdrucks mit `TemplateSyntaxError: unexpected '}'`
ausfallen. Beta 9 repariert betroffene gespeicherte Dashboards automatisch,
ohne Benutzeranpassungen am übrigen Dashboard zu ersetzen.

Beta 10 überarbeitet den dynamischen SOC-Ladeplan. Das dynamische Soll folgt
nun einer zeitbasierten Kurve von Mindest-SOC bei Sonnenaufgang bis Ziel-SOC
bei Sonnenuntergang. Eine knappe PV-Restprognose hebt diese Kurve progressiv
an, ohne das Soll bereits früh am Tag hart auf 100 % zu setzen.

Beta 11 ergänzt eine **vorausschauende SOC-Freigabe**. Liegt der Speicher
sicher über dem aktuellen Ladeplan und über dem prognosebasierten Mindest-SOC
für eine spätere Wiederaufladung, darf dieser SOC-Vorsprung für den
Hausverbrauch genutzt werden. Dabei kann verbleibende PV-Energie später für
das Wiederaufladen des Akkus reserviert werden. Dadurch wird Netzbezug
reduziert und gleichzeitig wieder Platz für späteren PV-Überschuss geschaffen.
Die neue Funktion ist standardmäßig ausgeschaltet.

Beta 12 korrigiert die Berechnung der **prognosebasierten Wiederauflade-Reserve**
für die SOC-Freigabe. Der erwartete Hausenergiebedarf wird für diese separate
Freigabe-Reserve nicht mehr von der Restprognose abgezogen. Dadurch kann ein
bereits voller Akku bei vorhandenem Netzbezug kontrolliert Energie freigeben,
wenn noch genügend PV-Energie für eine spätere Wiederaufladung prognostiziert
ist. Zusätzlich berücksichtigt die SOC-Nachladung jetzt, dass das dynamische
SOC-Soll während der Nachholzeit weiter ansteigt. Die Sollkurve selbst bleibt
unverändert.

Beta 13 beschleunigt die **Lastnachführung während der SOC-Freigabe**. Die
Regellogik wird alle 15 Sekunden ausgewertet. Während `SOC-Freigabe` dürfen
erforderliche Sollwerterhöhungen im Abstand von 30 Sekunden geschrieben
werden; normale Betriebsarten behalten den konservativen Mindestabstand von
zwei Minuten. Sicherheitsrelevante Reduzierungen nach einer SOC-Freigabe
bleiben weiterhin sofort möglich.

Beta 14 bündelt drei Korrekturen und eine Diagnoseverbesserung. Der
**SOC-Ladeplan** erhält nachts den eindeutigen Status `Nachtbetrieb`. Zusätzlich
führt die Automatik die neue **PV-Umlenkung** ein: Liegt der Ist-SOC mindestens
am dynamischen Soll, während der Akku gleichzeitig lädt und Netzbezug besteht,
wird nur der gleichzeitig vorhandene Ladestrom zum Haus umgelenkt. Dadurch soll
kein Netzstrom mehr bezogen werden, nur um den Akku stärker zu laden; eine
gezielte Akkuentladung ist für diese Funktion nicht erforderlich. Außerdem gibt
es jetzt einen eigenen Enum-Sensor **Controllerstatus** mit zentralen deutschen
und englischen Übersetzungen. `waiting_for_retry` wird dabei als **Warte auf
Stellwertübernahme** beziehungsweise **Waiting for setpoint confirmation**
angezeigt.

## Voraussetzungen

- Home Assistant
- HACS
- MQTT
- Noah-MQTT
- Forecast.Solar
- Sun-Integration
- saldierter Netzleistungssensor
- beschreibbare `number`-Entität für NOAH System Output Power

Für das erweiterte Dashboard zusätzlich:

- Power Flow Card Plus
- ApexCharts Card

Die beiden Custom Cards werden nicht automatisch installiert. Der Optimizer
selbst funktioniert auch ohne sie.

## Installation über HACS

### Direkt in HACS öffnen

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

Der Button öffnet das Repository direkt in HACS über **My Home Assistant**.

> **Hinweis zu Home Assistant 2026.8 und neuer:**  
> Home Assistant OS verwendet bei neuen Installationen standardmäßig Port 80
> statt Port 8123. Home Assistant Container verwendet weiterhin standardmäßig
> Port 8123. Der HACS-Link selbst enthält keinen Home-Assistant-Port.
>
> Falls My Home Assistant noch eine Adresse mit `:8123` öffnet, muss dort die
> im Browser gespeicherte Instanz-URL auf die tatsächlich verwendete
> Home-Assistant-Adresse angepasst werden.

Alternativ kann das Repository als benutzerdefiniertes Repository eingetragen
werden:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

Danach **Growatt NOAH Optimizer** installieren und Home Assistant neu starten.

Die vollständige Anleitung steht unter:

- [Installation](docs/installation.md)
- [Konfiguration](docs/configuration.md)
- [Fehlerbehebung](docs/troubleshooting.md)
- [HACS Beta / Pre-Release](docs/hacs-beta.md)

## Benötigte Quell-Entitäten

Beim Einrichten werden ausgewählt:

- saldierte Netzleistung
- NOAH Solar Power
- NOAH Output Power
- NOAH SOC
- NOAH Charging Power
- NOAH Discharge Power
- Forecast.Solar Restprognose heute
- NOAH System Output Power

Unterstützte Einheiten:

```text
Leistung: W oder kW
Energie:  Wh oder kWh
SOC:      %
```

Die erwartete Netzkonvention lautet:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Bei umgekehrter Konvention kann während der Einrichtung
**Netzvorzeichen umkehren** aktiviert werden.

## Optimizer-Berechnung

Die Integration berechnet unter anderem:

- Netzbezug und Netzeinspeisung
- Hauslast
- Batterieleistung
- 5-Minuten-Mittelwert der Netzleistung
- verbleibende Zeit bis Sonnenuntergang
- verfügbare Akkuenergie
- benötigte Ladeenergie
- wirksame PV-Restprognose
- vollständige Forecast.Solar-Leistungskurve für den aktuellen Tag
- Zeitpunkt der letzten Forecast-Aktualisierung
- wirksame Tagesprognose und prognostizierten End-SOC
- Ladeplanbasis (Forecast.Solar-Kurve oder Tageslicht-Fallback)
- PV-Prognosereferenz des aktuellen Tages
- gemessene PV-Energie des aktuellen Tages
- PV-Lernfaktor aus bis zu sieben gültigen Lerntagen
- wirksamen Prognosefaktor aus Sicherheits- und optionalem Lernfaktor
- Bereitschaftsstatus des PV-Learnings
- erwarteten Hausenergiebedarf
- Prognosemarge
- Prognosedeckung
- erforderliche mittlere Ladeleistung
- verbleibende Zeit bis Ziel-SOC
- Eigenverbrauch-Sollwert
- Ladeprioritäts-Sollwert
- dynamisches SOC-Soll
- SOC-Abweichung zum dynamischen Ladeplan
- dynamisch erforderliche Nachladeleistung
- prognosebasierten Mindest-SOC
- SOC-Freigabegrenze
- freigebare Akkuenergie
- SOC-Freigabe-Sollwert
- Reglermodus
- Controllerstatus
- endgültigen Ausgangssollwert

Die ursprüngliche Berechnungslogik wurde in Beta 4 gegen den bisherigen
YAML-Optimizer verglichen. Bei identischen Einstellungen stimmten die
relevanten Berechnungsergebnisse, der Reglermodus und der Ausgangssollwert mit
der YAML-Version überein.

## PV-Learning ab 2.1.0-beta.1

PV-Learning gleicht systematische Unterschiede zwischen der Forecast.Solar-
Prognose und dem tatsächlich vom NOAH gemessenen PV-Ertrag aus. Es benötigt
keine zusätzliche Quellentität. Verwendet werden die bereits konfigurierte
**NOAH Solar Power**-Entität, die **Forecast.Solar Restprognose heute** und die
Sun-Integration.

Die Integration integriert die PV-Leistung über den Tag und bildet für jeden
gültigen Lerntag:

```text
Tagesverhältnis
= gemessene PV-Energie / PV-Prognosereferenz
```

Der **PV-Lernfaktor** ist der Median der letzten maximal sieben gültigen
Tagesverhältnisse. Ein Tageswert wird für das Learning auf `0,50 ... 1,50`
begrenzt, damit einzelne Ausreißer das Ergebnis nicht übermäßig verändern.
Mindestens drei gültige Lerntage sind erforderlich, bevor der Lernfaktor auf
die Regelung angewendet werden kann.

Ohne angewendetes PV-Learning gilt unverändert:

```text
wirksamer Prognosefaktor
= Prognose-Sicherheitsfaktor
```

Ist PV-Learning bereit und **Gelernte PV-Korrektur verwenden** eingeschaltet:

```text
wirksamer Prognosefaktor
= Prognose-Sicherheitsfaktor × PV-Lernfaktor

wirksame Restprognose
= Forecast.Solar Restprognose × wirksamer Prognosefaktor
```

Das Learning selbst läuft immer passiv. Der neue Schalter ist standardmäßig
**Aus**. Solange er ausgeschaltet ist, verändert der gelernte PV-Faktor die
Forecast-Berechnung nicht. Die unabhängig davon mit `2.1.0-beta.2` und
`2.1.0-beta.3` eingeführten Änderungen am dynamischen SOC-Ladeplan bleiben
natürlich aktiv, wenn die dynamische SOC-Steuerung eingeschaltet ist. Mit
**PV-Lerndaten zurücksetzen** kann die gespeicherte Lernhistorie gelöscht werden.

Ein Tag wird unter anderem verworfen, wenn die Integration erst deutlich nach
Tagesbeginn gestartet wurde, keine ausreichende Prognosereferenz vorliegt,
weniger als zwei Stunden gültige Tagesdaten beobachtet wurden oder der Tag nicht
bis mindestens 85 % des Tageslichtfensters verfolgt werden konnte. Eine
Messlücke von mehr als zehn Minuten, die die Tagesbeobachtung berührt, macht den
gesamten Lerntag ungültig, damit fehlende PV-Produktion nicht als zu geringer
Tagesertrag angelernt wird. Nach begonnener Tagesbeobachtung wird nachts keine
neue Prognosereferenz mehr übernommen.

## Betriebsarten

Der Optimizer unterstützt:

```text
Automatik
Eigenverbrauch
Ladepriorität
Manuell
```

### Automatik

Die Betriebsart wird abhängig von unter anderem SOC, Ziel-SOC, Mindest-SOC,
Restprognose, Prognosemarge, erwarteter Hauslast, Netzleistung und verbleibender
Zeit bis Sonnenuntergang automatisch gewählt.

Ist zusätzlich **Dynamische SOC-Steuerung aktiv** eingeschaltet, kann die
Automatik den Reglermodus **SOC-Nachladung** verwenden. Ist außerdem die
**Vorausschauende SOC-Freigabe** aktiviert und ausreichend sicherer
SOC-Vorsprung vorhanden, kann der Reglermodus **SOC-Freigabe** verwendet
werden. Ab Beta 14 kann die Automatik außerdem **PV-Umlenkung** verwenden,
wenn der Akku mindestens am dynamischen SOC-Soll liegt, gleichzeitig geladen
wird und dennoch Netzbezug besteht. Ab `2.1.0-beta.2` wird bei erfülltem
dynamischem Ladeplan andernfalls **SOC-Ladeplan halten** verwendet, statt die
alte Prognosemarge nochmals als Ladepriorität auszuwerten.

### Eigenverbrauch

Die Ausgangsleistung wird so geregelt, dass der Netzbezug möglichst reduziert
wird.

### Ladepriorität

Ein Teil der verfügbaren PV-Leistung wird für das Erreichen des Ziel-SOC
reserviert.

### SOC-Ladeplan halten ab 2.1.0-beta.2

Ist die dynamische SOC-Steuerung in **Automatik** aktiv und der Speicher liegt
innerhalb der SOC-Toleranz im oder vor dem dynamischen Ladeplan, wird die
klassische Prognosemarge nicht erneut als Ladepriorität ausgewertet. Der
Ladeplan enthält die wirksame Restprognose, erwartete Hauslast und
Sicherheitsreserve bereits.

In diesem Zustand gilt für den sicheren Roh-Sollwert:

```text
SOC-Halten-Soll = min(aktuelle PV-Leistung, Eigenverbrauchs-Soll)
```

Der Sollwert wird auf das Stellgrößenraster **abgerundet**, damit durch das
Rastern keine absichtliche Akkuentladung entsteht. Ist die vorausschauende
SOC-Freigabe aktiv und sicher möglich, hat diese weiterhin Vorrang und darf
gezielt freigebare Akkuenergie für den Hausverbrauch nutzen.

### Manuell

Die konfigurierte manuelle Ausgangsleistung wird als Sollwert verwendet.

### PV-Umlenkung ab Beta 14

Die PV-Umlenkung behandelt einen Zustand, der keine Akkuentladung erfordert:
Der Akku liegt bereits mindestens am dynamischen SOC-Soll, wird aber weiter
geladen, während das Haus gleichzeitig Leistung aus dem Netz bezieht.

Dann wird höchstens der kleinere Wert aus aktuellem Netzbezug und aktueller
Akkuladeleistung zum Haus umgelenkt:

```text
PV-Umlenkungsleistung
= min(Netzbezug, Akkuladeleistung)

Ausgangssollwert
= aktuelle NOAH-Ausgangsleistung + PV-Umlenkungsleistung
```

Beispiel:

```text
NOAH-Ausgang:       480 W
Netzbezug:          191 W
Akkuladung:         269 W

PV-Umlenkung:       191 W
neues Roh-Soll:     671 W
```

Die Umlenkung reduziert damit zunächst nur die Akkuladung. Sie fordert nicht
absichtlich mehr Leistung an, als gleichzeitig als Akkuladung vorhanden ist.
Der endgültige Sollwert wird für diesen Modus auf das konfigurierte
Stellgrößenraster **abgerundet**, damit das Rastern den sicheren Rohwert nicht
überschreitet. Ergibt das Raster keinen Sollwert oberhalb der aktuell gemessenen
NOAH-Ausgangsleistung, wird keine PV-Umlenkung aktiviert. Erst wenn eine
zusätzliche Entladung zulässig und erforderlich ist, greift die separate
vorausschauende SOC-Freigabe. **SOC-Nachladung** hat weiterhin Vorrang, wenn
der Speicher hinter dem Ladeplan liegt.

## Dynamischer SOC-Ladeplan ab Beta 10 / Forecast-Kurve ab 2.1.0-beta.3

Bis `2.1.0-beta.2` wurde das dynamische SOC-Soll aus dem Fortschritt zwischen
Sonnenaufgang und Sonnenuntergang abgeleitet. Das war robust, bildet aber die
tatsächliche zeitliche PV-Verteilung einer Anlage nur grob ab. Eine Süd-Anlage
kann beispielsweise lange nach Sonnenaufgang noch kaum Leistung liefern.

Ab `2.1.0-beta.3` verwendet der Optimizer deshalb – sofern die konfigurierte
Restprognose direkt aus der Home-Assistant-Integration **Forecast.Solar**
stammt – deren vollständige intern vorhandene Leistungskurve. Home Assistant
verwendet dieselben Forecast-Daten bereits für das Energiedashboard. Der NOAH
Optimizer greift auf die bereits geladenen Daten zu und verursacht **keine
zusätzlichen Forecast.Solar-API-Aufrufe**.

### 1. Zeitaufgelöste PV-Prognose

Forecast.Solar liefert Leistungspunkte über den Tagesverlauf. Daraus entsteht
beispielsweise eine Kurve wie:

```text
08:00    30 W
09:00   110 W
10:00   280 W
11:00   520 W
12:00   690 W
13:00   740 W
14:00   660 W
15:00   470 W
16:00   250 W
```

Die wirksame Leistungskurve verwendet denselben Faktor wie die vorhandene
Restprognose:

```text
wirksame PV-Leistung
= Forecast.Solar-Leistung
  × Prognose-Sicherheitsfaktor
  × optionaler PV-Lernfaktor
```

### 2. Für den Ladeplan verfügbare PV-Energie

Der Ladeplan wird aus der vollständigen wirksamen PV-Kurve aufgebaut. Die
konfigurierte erwartete Hauslast wird dabei **nicht vorab von jedem
Forecast-Intervall abgezogen**. Der Optimizer kann bei Bedarf prognostizierte
PV-Leistung für das Laden des Akkus reservieren und den Hausverbrauch in diesem
Zeitraum teilweise aus dem Netz decken.

Das ist wichtig, wenn die PV-Leistung beispielsweise unter der erwarteten
Hauslast liegt: Diese PV-Leistung ist trotzdem zum Akkuladen verfügbar, wenn die
Regelung dafür die NOAH-Ausgangsleistung reduziert.

Die wirksame PV-Kurve wird über den Tag integriert, mit der Ladeeffizienz
bewertet und um die konfigurierte Forecast-Energiereserve reduziert. Die
erwartete Hauslast bleibt weiterhin Bestandteil von Prognosemarge,
Prognosedeckung und der Entscheidung über die Ausgangsleistung.

### 3. Forecast-geformter SOC-Ladeplan

Der SOC-Ladeplan startet weiterhin beim Mindest-SOC. Er steigt aber nicht mehr
linear mit der Uhrzeit, sondern entsprechend der zeitlichen Verteilung der laut
Forecast.Solar verfügbaren PV-Energie.

Damit bleibt das Soll bei einer Süd-Anlage am frühen Morgen niedrig und steigt
erst mit der erwarteten Einstrahlung. Bei bedecktem Himmel kann der
prognostizierte End-SOC unter dem eingestellten Ziel-SOC liegen. Das Ziel-SOC
bleibt als Wunschziel sichtbar; der dynamische Ladeplan zeigt dagegen, was die
aktuelle Prognose unter den konfigurierten Annahmen erwarten lässt.

Wichtig: Der aktuelle Ist-SOC und die tatsächlich gemessene PV-Leistung werden
**nicht** verwendet, um den Tagesplan nachträglich passend zu machen. Änderungen
des Ladeplans entstehen nur durch neue Forecast.Solar-Daten oder geänderte
Planungsparameter. Dadurch bleibt sichtbar, ob die Prognose richtig oder falsch
war.

### 4. SOC-Nachladung

Die Abweichung bleibt:

```text
SOC-Abweichung = Ist-SOC - dynamisches SOC-Soll
```

Bei mehr als 2 Prozentpunkten Rückstand aktiviert die Automatik weiterhin
**SOC-Nachladung**. Für die Nachholzeit wird jetzt ebenfalls der zukünftige
Punkt auf der Forecast-geformten SOC-Kurve verwendet.

### 5. Fallback

Kann die konfigurierte Restprognose keiner nativen Forecast.Solar-Config-Entry
zugeordnet werden oder stellt Forecast.Solar vorübergehend keine Kurve bereit,
verwendet der Optimizer automatisch die bisherige Tageslichtberechnung aus
Beta 10 bis Beta 2.1.0-beta.2. Der Sensor **Ladeplanbasis** zeigt an, welcher
Pfad aktuell aktiv ist.

## Vorausschauende SOC-Freigabe ab Beta 11

Beta 11 nutzt einen sicher freigebbaren SOC-Vorsprung, um bei einem bereits
weit geladenen Akku unnötigen Netzbezug zu vermeiden und gleichzeitig wieder
Aufnahmekapazität für späteren PV-Überschuss zu schaffen.

Die Funktion wirkt ausschließlich in der Betriebsart **Automatik** und besitzt
einen eigenen Schalter:

```text
Vorausschauende SOC-Freigabe aktiv
```

Der Schalter ist standardmäßig **Aus**. Zusätzlich muss die dynamische
SOC-Steuerung aktiv sein. Dadurch bleibt die SOC-Nachladung verfügbar, falls
sich die Prognose später verschlechtert.

### Prognosebasierter Mindest-SOC

Für die **SOC-Freigabe** wird eine eigene Wiederauflade-Reserve berechnet.
Sie unterscheidet sich bewusst von der konservativen Prognose-Anforderung des
dynamischen Ladeplans.

Der dynamische Ladeplan berücksichtigt weiterhin:

```text
PV-Energie für Ladeplan
= wirksame Restprognose
  - erwarteter Hausenergiebedarf
  - zusätzliche Energiereserve
```

Für die SOC-Freigabe wird dagegen gefragt, wie viel Akkuenergie mit der
verbleibenden PV-Prognose später wieder aufgefüllt werden könnte, wenn diese
PV-Energie bei Bedarf für den Akku reserviert wird:

```text
PV-Energie für Wiederaufladung
= wirksame Restprognose
  - zusätzliche Energiereserve

Speicherbare Wiederaufladeenergie
= PV-Energie für Wiederaufladung × Ladewirkungsgrad

Möglicher Wiederauflade-SOC
= Speicherbare Wiederaufladeenergie / Akkukapazität × 100

Prognosebasierter Mindest-SOC
= Ziel-SOC - möglicher Wiederauflade-SOC
```

Der erwartete Hausenergiebedarf wird bei **dieser Freigabe-Reserve nicht
abgezogen**. Das ist beabsichtigt: Falls erforderlich, kann späterer
Hausverbrauch aus dem Netz versorgt werden, während die prognostizierte
PV-Energie zum Wiederaufladen des zuvor freigegebenen Akkuanteils verwendet
wird.

Dadurch wird ein bereits voller Akku nicht allein deshalb bei `100 %`
festgehalten, weil die normale Prognosemarge wegen des erwarteten
Hausverbrauchs negativ ist.

Der Wert wird auf Mindest-SOC bis Ziel-SOC begrenzt.

### SOC-Freigabegrenze

Für eine Entladung wird nicht nur der aktuelle dynamische Ladeplan betrachtet.
Die sichere Untergrenze ist der größere Wert aus dynamischem SOC-Soll und
prognosebasiertem Mindest-SOC. Zusätzlich bleiben 2 SOC-Prozentpunkte Reserve:

```text
SOC-Freigabegrenze
= max(Dynamisches SOC-Soll, Prognosebasierter Mindest-SOC)
  + 2 %-Punkte Sicherheitsreserve
```

Die Grenze wird maximal auf `100 %` begrenzt.

Der Optimizer gibt nur den Anteil oberhalb dieser Grenze frei:

```text
Freigebarer SOC
= max(Ist-SOC - SOC-Freigabegrenze, 0)

Freigebare Akkuenergie
= Akkukapazität × Freigebarer SOC / 100
```

### Regelwirkung

Die SOC-Freigabe wird nur aktiv, wenn gleichzeitig:

- Optimierer-Berechnung aktiv ist
- Betriebsart **Automatik** gewählt ist
- Dynamische SOC-Steuerung aktiv ist
- Vorausschauende SOC-Freigabe aktiv ist
- Forecast.Solar verfügbar ist
- es Tag ist
- der Ist-SOC über der SOC-Freigabegrenze liegt
- tatsächlich Netzbezug vorhanden ist

Dann erhöht der Optimizer die NOAH-Ausgangsleistung um den aktuell gemessenen
Netzbezug, höchstens bis zur maximalen Ausgangsleistung:

```text
SOC-Freigabe-Soll
= aktuelle NOAH-Ausgangsleistung + aktueller Netzbezug
```

Ziel ist ein möglichst kleiner Netzbezug. Es wird **keine absichtliche
Batterieeinspeisung ins Netz** angefordert. Wegen Stellgrößenraster,
Messverzögerungen und Laständerungen können kurzfristig dennoch kleine
Abweichungen um 0 W entstehen.

### Sicherheitsgrenze der Prognose

Die SOC-Freigabe ist prognosebasiert. Sie verhindert, dass der Optimizer den
Akku absichtlich unter den höheren Wert aus dynamischem Ladeplan und
prognosebasierter Wiederauflade-Reserve entlädt.

Wichtig ist die bewusste Prioritätsverschiebung:

- der **dynamische Ladeplan** berücksichtigt weiterhin den erwarteten
  Hausenergiebedarf
- die **Freigabe-Reserve** reserviert die verbleibende PV-Energie bei Bedarf
  für das spätere Wiederaufladen des Akkus
- dadurch kann zu einem späteren Zeitpunkt Netzbezug für den Hausverbrauch
  entstehen, wenn die PV-Energie zum Wiederaufladen benötigt wird

Das ist beabsichtigt: Ziel der Freigabe ist, jetzt vorhandenen Netzbezug aus
einem sicheren SOC-Vorsprung zu decken und gleichzeitig Ladekapazität für
späteren PV-Überschuss zu schaffen.

Die Berechnung kann keine absolute Garantie geben. Fällt der reale PV-Ertrag
geringer aus als Forecast.Solar oder ändern sich die Lastverhältnisse stark,
kann das tatsächliche Abend-SOC vom Ziel abweichen.

Verschlechtert sich die Prognose, steigt die SOC-Freigabegrenze. Die Freigabe
endet dann automatisch; bei aktiviertem dynamischem SOC-Regler kann anschließend
wieder **SOC-Nachladung** erforderlich werden.

## Aktive Steuerung

Die Integration besitzt getrennte Schalter:

```text
Optimierer-Berechnung aktiv
NOAH-Steuerung aktiv
Dynamische SOC-Steuerung aktiv
Vorausschauende SOC-Freigabe aktiv
```

Die aktive NOAH-Steuerung, die dynamische SOC-Steuerung und die
vorausschauende SOC-Freigabe sind standardmäßig ausgeschaltet.

Der Controller enthält unter anderem:

- Schalt-Hysterese
- Stellgrößenraster
- Mindestabstand von zwei Minuten zwischen normalen Stellbefehlen
- schnellere Lastnachführung während SOC-Freigabe und PV-Umlenkung mit 30 Sekunden Mindestabstand für Sollwerterhöhungen
- Controller-Auswertung alle 15 Sekunden
- sofortige sicherheitsrelevante Sollwertreduzierung nach SOC-Freigabe, PV-Umlenkung oder im Modus SOC-Ladeplan halten
- eigener Enum-Sensor `Controllerstatus` mit zentralen Übersetzungen
- erneute Sollwertübernahme, wenn ein zuvor geschriebener Sollwert nicht bestätigt wurde
- Failsafe bei längerem Verlust kritischer Daten
- persistente Home-Assistant-Benachrichtigung
- Sperre gegen den alten YAML-Controller

Der alte YAML-Optimizer und die HACS-Steuerung dürfen niemals gleichzeitig
denselben NOAH aktiv regeln.

## Dashboard ab Beta 6

Die Integration erzeugt beim ersten Start ein eigenes Lovelace-Dashboard mit
dem Seitenleisteneintrag:

```text
NOAH Optimizer
```

Bei einer Neuinstallation kann im Einrichtungsdialog gewählt werden, ob der
Eintrag in der Seitenleiste erscheinen soll. Standard ist **Ein**.

Die Integration löst ihre eigenen Entity-IDs über die Home-Assistant Entity
Registry auf. Bereichspräfixe oder vom Benutzer geänderte Entity-IDs müssen
deshalb nicht fest in den Dashboard-Dateien stehen.

Die Standardsprache des Dashboards richtet sich bei der erstmaligen Erzeugung
nach der Home-Assistant-Sprache:

- Deutsch → `dashboard_de.yaml`
- alle anderen Sprachen → `dashboard_en.yaml`

### Dashboard-Migration in Beta 8

Ein vorhandenes Beta-6-/Beta-7-Dashboard wird nicht vollständig ersetzt.
Beta 8 ergänzt gezielt die neuen dynamischen SOC-Entitäten und den SOC-Chart.
Vorhandene Benutzeranpassungen bleiben erhalten. Gleichzeitig wird die alte
fehlerhafte Batterie-Flusszuordnung korrigiert, falls sie noch exakt im
Beta-6-Zustand vorhanden ist.

### Dashboard-Migration in Beta 11

Beta 11 ergänzt die neue Freigabefunktion und deren Diagnosesensoren gezielt in
bestehende Dashboards. Dafür wird die Dashboard-Template-Version von 9 auf 10
erhöht. Das Dashboard wird nicht vollständig ersetzt; vorhandene
Benutzeranpassungen bleiben erhalten, soweit die bekannten Standardkarten
eindeutig erkannt werden können.

### Dashboard-Migration in Beta 14

Beta 14 erhöht die Dashboard-Template-Version von 10 auf 11. Die gezielte
Migration ergänzt den SOC-Ladeplanstatus `night`, den Reglermodus `PV-Umlenkung`
und stellt die Controllerstatus-Anzeige auf den neuen Enum-Sensor um. Die
Statusübersetzungen kommen damit aus `translations/de.json` beziehungsweise
`translations/en.json` statt aus einer separaten Jinja-Tabelle im Dashboard.
Benutzeranpassungen am übrigen Dashboard werden nicht ersetzt.

### Dashboard-Migration in 2.1.0-beta.1

PV-Learning erhöht die Dashboard-Template-Version von 11 auf 12. Bestehende
Dashboards werden gezielt um die PV-Learning-Diagnosewerte, den Opt-in-Schalter
und die Reset-Schaltfläche ergänzt.

### Dashboard-Migration in 2.1.0-beta.2

`2.1.0-beta.2` erhöht die Dashboard-Template-Version von 12 auf 13. Die
Reglerstatus-Karte wird gezielt um den lokalisierten Modus **SOC-Ladeplan halten**
erweitert. Übrige Benutzeranpassungen bleiben erhalten, soweit die bekannte
Standardkarte eindeutig erkannt werden kann.

### Dashboard-Migration in 2.1.0-beta.3

`2.1.0-beta.3` erhöht die Dashboard-Template-Version von 13 auf 14. Bestehende
Standard-Dashboards erhalten eine neue Karte **PV-Prognose** mit der rohen
Forecast.Solar-Leistungskurve, der wirksamen korrigierten Kurve und der real
gemessenen PV-Leistung. In den Planungsdetails werden zusätzlich
Forecast-Aktualisierungszeitpunkt, wirksame Tagesprognose, prognostizierter
End-SOC und Ladeplanbasis ergänzt. Benutzeranpassungen werden weiterhin nur
gezielt migriert.

### Energiefluss

Für Power Flow Card Plus gilt:

```text
Netz:
consumption = Netzbezug
production  = Netzeinspeisung

NOAH:
consumption = Entladeleistung
production  = Ladeleistung
```

Damit zeigt die Card Ladeleistung als Energiefluss **in** den Akku und
Entladeleistung als Energiefluss **aus** dem Akku.

### Dashboard-Inhalt

- aktueller Energiefluss
- Netzbezug und Netzeinspeisung getrennt
- Laden und Entladen des NOAH getrennt
- Akkustand und Prognosedeckung
- dynamischer SOC-Ladeplan mit Ist-SOC, dynamischem Soll und Ziel-SOC
- PV-Prognosekurve mit Forecast.Solar, wirksamer Prognose und Ist-PV
- Forecast-Aktualisierungszeitpunkt und prognostizierter End-SOC
- SOC-Abweichung und Ladeplanstatus
- prognosebasierter Mindest-SOC und SOC-Freigabegrenze
- freigebare Akkuenergie und SOC-Freigabe-Soll
- Reglermodus und Controllerstatus
- letzter Stellwert und letzter Stellbefehl
- Energieplanung bis Sonnenuntergang
- Leistung heute
- Reglerverhalten
- Planung im Detail
- Kalibrierparameter
- Diagnose

### Browseransicht

![NOAH Optimizer Dashboard im Browser](screenshots/noah_dashboard_browser.png)

### Mobile Ansicht

![NOAH Optimizer Dashboard auf dem iPhone](screenshots/noah_dashboard_iPhone.jpeg)

## Versionshistorie

### 2.0.0-beta.1

Erste HACS-kompatible Custom Integration im reinen Beobachtungsbetrieb mit
Config Flow, Quellentitäten, Einheiten-Normalisierung und grundlegenden
Energiefluss-Sensoren.

### 2.0.0-beta.2

Integrationstyp auf `device` umgestellt und HACS-Updatepfad verbessert.

### 2.0.0-beta.3

Berechnungslogik des Legacy-YAML-Optimizers nach Python portiert. Noch keine
aktive Stellwertausgabe.

### 2.0.0-beta.4

Fehlende `select.py` ergänzt und Berechnungswerte 1:1 gegen die Legacy-Version
geprüft.

### 2.0.0-beta.5

Optionale aktive NOAH-Steuerung, Hysterese, Mindestabstand zwischen Befehlen,
Retry, Failsafe, Controllerdiagnose und Legacy-Sperre ergänzt.

### 2.0.0-beta.6

Automatisches Lovelace-Dashboard mit dynamischer Entity-Auflösung, deutschen
und englischen Vorlagen, Power Flow Card Plus und ApexCharts eingeführt.

### 2.0.0-beta.7

Batterie-Flussrichtung im Dashboard korrigiert:

```text
consumption = Entladeleistung
production  = Ladeleistung
```

### 2.0.0-beta.8

Dynamischen SOC-Ladeplan ergänzt:

- dynamisches SOC-Soll
- SOC-Abweichung
- Ladeplanstatus
- dynamisch erforderliche Nachladeleistung
- neue SOC-Nachholzeit
- separate, standardmäßig deaktivierte Freigabe der dynamischen Regelung
- neuer Reglermodus `SOC-Nachladung`
- Diagramm mit Ist-SOC, dynamischem Soll und Ziel-SOC im Dashboard
- gezielte Dashboard-Migration für bestehende Installationen

### 2.0.0-beta.9

Dashboard-Hotfix:

- fehlerhaften Jinja-Ausdruck im Reglerstatus behoben
- bereits von Beta 8 beschädigte Reglerstatus-Karten werden automatisch repariert
- Dashboard-Template-Version auf 9 erhöht
- Benutzeranpassungen am Dashboard bleiben erhalten
- keine Änderung an Berechnung oder aktiver NOAH-Regelung

### 2.0.0-beta.10

Dynamischen SOC-Ladeplan neu aufgebaut:

- zeitbasierte Sollkurve von Sonnenaufgang bis Sonnenuntergang
- Mindest-SOC als Startwert und Ziel-SOC als Endwert
- Restprognose wirkt als progressive Anhebung der Sollkurve
- kein sofortiges 100-%-Soll mehr nur wegen einer knappen Restprognose
- Ladeplanstatus und Nachladeleistung verwenden die neue Sollkurve
- keine Änderung der Dashboard-Struktur; Template-Version bleibt 9

### 2.0.0-beta.11

Vorausschauende SOC-Freigabe ergänzt:

- sicher freigebbarer SOC-Vorsprung wird aus Ladeplan und Restprognose ermittelt
- neuer prognosebasierter Mindest-SOC
- neue SOC-Freigabegrenze mit 2 Prozentpunkten Sicherheitsreserve
- freigebare Akkuenergie wird separat angezeigt
- neuer Sollwert für die SOC-Freigabe
- neuer Reglermodus `SOC-Freigabe`
- eigener, standardmäßig deaktivierter Freigabeschalter
- Netzbezug kann bei sicherem SOC-Vorsprung bevorzugt aus dem Akku gedeckt werden
- keine absichtliche Batterieeinspeisung ins Netz
- Dashboard-Template-Version auf 10 erhöht und bestehende Dashboards gezielt migriert
- sicherheitsrelevante Sollwertreduzierungen nach SOC-Freigabe umgehen die normale 2-Minuten-Wartezeit

### 2.0.0-beta.12

SOC-Freigabe-Reserve und SOC-Nachladung korrigiert:

- eigene Wiederauflade-Reserve für die SOC-Freigabe eingeführt
- erwarteter Hausenergiebedarf wird bei dieser Reserve nicht mehr abgezogen
- dynamische SOC-Sollkurve bleibt weiterhin konservativ und unverändert
- SOC-Nachladung zielt auf das vorausberechnete Soll am Ende der Nachholzeit
- verhindert dauerhaftes Hinterherlaufen hinter einer steigenden SOC-Sollkurve
- verhindert eine unnötige 100-%-Freigabegrenze nur wegen negativer normaler Prognosemarge
- prognosebasierter Mindest-SOC beschreibt nun den für spätere Wiederaufladung notwendigen SOC
- Dashboard-Struktur unverändert; Template-Version bleibt 10

### 2.0.0-beta.13

Schnellere Lastnachführung der SOC-Freigabe:

- Controller-Auswertung von 60 auf 15 Sekunden verkürzt
- Sollwerterhöhungen in `SOC-Freigabe` können alle 30 Sekunden geschrieben werden
- normale Betriebsarten behalten den 2-Minuten-Mindestabstand
- SOC-Freigabe verwendet intern eine engere Deadband von maximal 25 W; das Stellgrößenraster bleibt maßgeblich
- sicherheitsrelevante Reduzierungen nach SOC-Freigabe bleiben ohne Wartezeit möglich
- `rate_limited` wird nur noch angezeigt, wenn tatsächlich ein neuer Stellbefehl ansteht und noch auf den Mindestabstand wartet
- keine neuen Entitäten oder Dashboardelemente; Template-Version bleibt 10

### 2.0.0-beta.14

Nachtstatus, PV-Umlenkung und zentrale Controllerstatus-Anzeige:

- neuer Enum-Zustand `night` für den Sensor `SOC-Ladeplan`
- deutsche Anzeige `Nachtbetrieb`, englische Anzeige `Night operation`
- neuer Reglermodus `pv_redirect` / `PV-Umlenkung` / `PV diversion`
- bei Ist-SOC mindestens am dynamischen Soll wird gleichzeitig vorhandene Akkuladung bevorzugt zum Abbau von Netzbezug verwendet
- PV-Umlenkung ist auf `min(Netzbezug, Akkuladeleistung)` begrenzt und fordert damit keine absichtliche Akkuentladung an
- PV-Umlenkungs-Sollwerte werden auf das Stellgrößenraster abgerundet, damit das Rastern den sicheren Umlenkungswert nicht überschreitet
- SOC-Nachladung und SOC-Freigabe behalten ihre bisherigen Schutzbedingungen und Prioritäten
- eigener Enum-Sensor `Controllerstatus` hinzugefügt
- Controllerstatus wird zentral über `translations/de.json` und `translations/en.json` lokalisiert
- `waiting_for_retry`: `Warte auf Stellwertübernahme` / `Waiting for setpoint confirmation`
- PV-Umlenkung verwendet wie SOC-Freigabe die schnelle 15-/30-Sekunden-Lastnachführung und sofortige Absenkung
- Dashboard-Template-Version von 10 auf 11 erhöht
- bestehende Reglerstatus-Karten werden gezielt migriert

### 2.0.0

Erster stabiler Release der 2.x-Reihe:

- Funktionsstand entspricht `2.0.0-beta.14`
- keine Änderung an Optimizer-Berechnung oder aktiver NOAH-Regelung gegenüber Beta 14
- keine neuen Entitäten, Schalter oder Dashboardelemente
- Dashboard-Template-Version bleibt 11
- Versions- und Release-Dokumentation auf stabilen Betrieb umgestellt

### 2.1.0-beta.1

- passives, persistentes PV-Learning ergänzt
- Median aus bis zu sieben gültigen Lerntagen; ab drei Tagen einsatzbereit
- neue Diagnoseentitäten für Lernfaktor, Lerntage, Tagesertrag und Prognosereferenz
- neuer Opt-in-Schalter **Gelernte PV-Korrektur verwenden**
- neue Schaltfläche **PV-Lerndaten zurücksetzen**
- wirksamer Prognosefaktor optional aus Sicherheitsfaktor × Lernfaktor
- Dashboard-Template-Version von 11 auf 12 erhöht
- bei ausgeschaltetem Lern-Schalter bleibt das Regelverhalten von 2.0.0 erhalten

### 2.1.0-beta.2

- neuer interner Reglermodus `soc_hold` / **SOC-Ladeplan halten**
- bei aktivem dynamischem SOC-Ladeplan wird eine negative klassische Prognosemarge nicht mehr doppelt als Ladepriorität ausgewertet, wenn der Ist-SOC im oder vor dem Ladeplan liegt
- SOC-Halten nutzt höchstens die aktuell verfügbare PV-Leistung bis zum Eigenverbrauchs-Soll und fordert damit keine absichtliche Akkuentladung an
- SOC-Nachladung, SOC-Freigabe und PV-Umlenkung behalten höhere Priorität
- Dashboard-Template-Version von 12 auf 13 erhöht; bestehende Reglerstatus-Karten werden migriert

### 2.1.0-beta.3

- vollständige Forecast.Solar-Leistungskurve aus Home Assistants bereits geladenen Forecast-Daten übernommen
- keine zusätzlichen Forecast.Solar-API-Aufrufe
- dynamischen SOC-Ladeplan bei nativer Forecast.Solar-Quelle von Tageslichtfortschritt auf zeitaufgelöste Prognosekurve umgestellt
- Prognose-/Lernfaktor, Ladeeffizienz und Energiereserve in die prognostizierte Akku-Ladekurve einbezogen; Hauslast bleibt separat in Prognosemarge und Ausgangsregelung
- prognostizierten End-SOC und Ladeplanbasis als neue Diagnosewerte ergänzt
- neue Dashboard-Karte für rohe Prognose, wirksame Prognose und reale PV-Leistung
- Forecast-Aktualisierungszeitpunkt im Dashboard ergänzt
- Tageslichtmodell als kompatiblen Fallback beibehalten
- Dashboard-Template-Version von 13 auf 14 erhöht

## Legacy-YAML-Optimizer

Die ältere Package-Variante bleibt im Repository enthalten.

Dateien:

```text
noah_optimizer.yaml
dashboards/noah_dashboard.yaml
```

Für neue Installationen wird die HACS-Integration empfohlen.

Die Legacy-YAML-Regelung muss ausgeschaltet sein, bevor die aktive
HACS-Steuerung eingeschaltet wird.

## Sicherheit

Dieses Projekt ist ein Community-Projekt und keine offizielle Growatt-
Integration.

Die aktive Steuerung sollte erst eingeschaltet werden, nachdem:

- alle Quellwerte plausibel geprüft wurden
- das Netzvorzeichen stimmt
- Forecast.Solar plausible Werte liefert
- NOAH System Output Power manuell beschreibbar ist
- der berechnete Ausgangssollwert plausibel ist

Nach Änderungen an der dynamischen SOC-Logik sollte die dynamische
SOC-Steuerung zunächst ausgeschaltet bleiben, bis dynamisches Soll,
SOC-Abweichung und Nachladeleistung über einen geeigneten Zeitraum plausibel
beobachtet wurden.

Die vorausschauende SOC-Freigabe sollte nach einem Update ebenfalls zunächst
ausgeschaltet bleiben. Vor der Aktivierung sollten insbesondere
prognosebasierter Mindest-SOC, SOC-Freigabegrenze und freigebare Akkuenergie
plausibel geprüft werden.

## Projektstruktur

```text
home-assistant-noah-optimizer/
├── .github/
│   └── workflows/
├── custom_components/
│   └── noah_optimizer/
│       ├── translations/
│       │   ├── de.json
│       │   └── en.json
│       ├── __init__.py
│       ├── binary_sensor.py
│       ├── button.py
│       ├── config_flow.py
│       ├── const.py
│       ├── control.py
│       ├── coordinator.py
│       ├── dashboard.py
│       ├── dashboard_de.yaml
│       ├── dashboard_en.yaml
│       ├── entity.py
│       ├── manifest.json
│       ├── number.py
│       ├── pv_learning.py
│       ├── select.py
│       ├── sensor.py
│       └── switch.py
├── dashboards/
│   └── noah_dashboard.yaml
├── docs/
│   ├── configuration.md
│   ├── hacs-beta.md
│   ├── installation.md
│   └── troubleshooting.md
├── screenshots/
├── CHANGELOG.md
├── LICENSE
├── README.md
├── THIRD_PARTY.md
├── hacs.json
└── noah_optimizer.yaml
```

## Lizenz

Dieses Projekt steht unter der MIT License.

Siehe:

- [LICENSE](LICENSE)
- [THIRD_PARTY.md](THIRD_PARTY.md)

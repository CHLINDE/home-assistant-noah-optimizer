# Home Assistant Growatt NOAH Optimizer

Prognosebasierte Steuerung der Ausgangsleistung eines Growatt NOAH 2000
über Home Assistant und Noah-MQTT.

> **Status:** Beta. Die aktive Steuerung kann die NOAH-Ausgangsleistung
> verändern und sollte während der Testphase überwacht werden.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

## Ziele

- Netzbezug reduzieren
- unnötige PV-Einspeisung bei noch aufnahmefähigem Speicher reduzieren
- Akku bis zum Abend auf einen konfigurierbaren Ziel-SOC laden
- Nachtentladung bis zu einem Mindest-SOC ermöglichen
- Forecast.Solar in die Ladeplanung einbeziehen
- dynamischen SOC-Ladeplan aus der verbleibenden PV-Prognose ableiten
- Regelzustand, Prognose und Energiefluss in einem Dashboard darstellen

## HACS-Integration

Eine HACS-kompatible Custom Integration ist als Beta verfügbar.

Aktuelle Beta:

```text
2.0.0-beta.11
```

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
sicher über dem aktuellen Ladeplan und über dem prognosebasiert benötigten
Mindest-SOC, darf dieser SOC-Vorsprung für den Hausverbrauch genutzt werden.
Dadurch wird Netzbezug reduziert und gleichzeitig wieder Platz für späteren
PV-Überschuss geschaffen. Die neue Funktion ist standardmäßig ausgeschaltet.

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
- [HACS Beta](docs/hacs-beta.md)

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
- endgültigen Ausgangssollwert

Die ursprüngliche Berechnungslogik wurde in Beta 4 gegen den bisherigen
YAML-Optimizer verglichen. Bei identischen Einstellungen stimmten die
relevanten Berechnungsergebnisse, der Reglermodus und der Ausgangssollwert mit
der YAML-Version überein.

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
werden.

### Eigenverbrauch

Die Ausgangsleistung wird so geregelt, dass der Netzbezug möglichst reduziert
wird.

### Ladepriorität

Ein Teil der verfügbaren PV-Leistung wird für das Erreichen des Ziel-SOC
reserviert.

### Manuell

Die konfigurierte manuelle Ausgangsleistung wird als Sollwert verwendet.

## Dynamischer SOC-Ladeplan ab Beta 10

Beta 10 verwendet einen echten zeitbasierten Ladeplan. Das dynamische SOC-Soll
soll nicht mehr nur beantworten, welchen SOC der Speicher aufgrund der
Restprognose theoretisch bereits haben müsste. Stattdessen entsteht eine
Sollkurve über den Tagesverlauf.

### 1. Tagesfortschritt

Zwischen Sonnenaufgang und Sonnenuntergang wird ein Tagesfortschritt `p`
zwischen `0` und `1` berechnet:

```text
p = vergangene Zeit seit Sonnenaufgang
    / Tageslichtdauer
```

Damit gilt:

```text
Sonnenaufgang      p = 0
Tagesmitte         p ≈ 0,5
Sonnenuntergang    p = 1
```

Außerhalb der Tageslichtzeit wird für den SOC-Ladeplan `p = 0` verwendet.

### 2. Zeitbasiertes Grund-Soll

Aus Mindest-SOC und Ziel-SOC entsteht zunächst eine lineare Sollkurve:

```text
Zeit-Soll
= Mindest-SOC
  + p × (Ziel-SOC - Mindest-SOC)
```

Bei beispielsweise:

```text
Mindest-SOC = 10 %
Ziel-SOC    = 100 %
```

ergibt sich ohne zusätzliche Prognosekorrektur ungefähr:

```text
Sonnenaufgang    10 %
25 % des Tages   32,5 %
50 % des Tages   55 %
75 % des Tages   77,5 %
Sonnenuntergang 100 %
```

### 3. Prognoseeinfluss

Zusätzlich wird weiterhin berechnet, wie viel der verbleibenden PV-Prognose
nach erwartetem Hausverbrauch und Energiereserve noch für den Akku zur
Verfügung steht:

```text
PV-Energie für Akku
= wirksame Restprognose
  - erwarteter Hausenergiebedarf
  - zusätzliche Energiereserve
```

Daraus entsteht eine interne Prognose-Anforderung:

```text
Prognose-Anforderung
= Ziel-SOC - möglicher zukünftiger SOC-Zuwachs
```

Diese Prognose-Anforderung wird in Beta 10 nicht mehr direkt als dynamisches
Soll verwendet.

Ist die Prognose knapp, wird das Zeit-Soll stattdessen progressiv angehoben:

```text
Prognosedruck
= max(Prognose-Anforderung - Zeit-Soll, 0)

Dynamisches SOC-Soll
= Zeit-Soll + p × Prognosedruck
```

Dadurch bleibt das Soll morgens niedrig und steigt im Tagesverlauf kontinuierlich.
Eine schlechte Restprognose zieht die Kurve früher nach oben, führt aber nicht
mehr unmittelbar zu einem 100-%-Soll.

Bei ausreichender Restprognose entspricht das dynamische Soll dem Zeit-Soll.

### 4. SOC-Ladeplan

Die Abweichung wird weiterhin als:

```text
SOC-Abweichung = Ist-SOC - dynamisches SOC-Soll
```

berechnet.

Mit einer Toleranz von 2 Prozentpunkten entstehen die Zustände:

```text
Vor Ladeplan
Im Ladeplan
Hinter Ladeplan
```

Liegt der Speicher hinter dem Ladeplan, wird zusätzlich eine dynamisch
erforderliche Nachladeleistung berechnet. Der Parameter **SOC-Nachholzeit**
legt fest, innerhalb welcher Zeit der Rückstand aufgeholt werden soll.
Standard sind `2,0 h`.

### 5. Nacht

Nach Sonnenuntergang gilt für den dynamischen SOC-Ladeplan wieder der
Mindest-SOC. Die eigentliche Nachtregelung bleibt unverändert und darf den
Speicher bis zum konfigurierten Mindest-SOC entladen.

### Sichere Aktivierung

Nach dem Update auf Beta 11 sollte zunächst gelten:

```text
NOAH-Steuerung aktiv = Aus
Dynamische SOC-Steuerung aktiv = Aus
Vorausschauende SOC-Freigabe aktiv = Aus
```

Die Sensoren rechnen trotzdem bereits mit der neuen Kurve. Dadurch kann das
Verhalten zunächst im Dashboard beobachtet werden.

Die dynamische SOC-Steuerung beeinflusst den Sollwert nur in der Betriebsart
**Automatik**. Manuell, Eigenverbrauch und Ladepriorität bleiben unverändert.

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

Aus der noch für den Akku erwarteten PV-Energie wird weiterhin berechnet,
welcher SOC bereits vorhanden sein muss, damit der Ziel-SOC bis
Sonnenuntergang prognostisch noch erreichbar ist:

```text
Prognosebasierter Mindest-SOC
= Ziel-SOC - möglicher zukünftiger SOC-Zuwachs
```

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
Akku absichtlich unter den nach aktuellem Ladeplan und aktueller Prognose
benötigten SOC entlädt. Sie kann jedoch keine absolute Garantie geben, wenn
sich PV-Ertrag oder Hausverbrauch später deutlich anders entwickeln als
prognostiziert.

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
- Mindestabstand zwischen normalen Stellbefehlen
- sofortige sicherheitsrelevante Sollwertreduzierung nach SOC-Freigabe
- Wiederholungsversuch bei nicht übernommenem Sollwert
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

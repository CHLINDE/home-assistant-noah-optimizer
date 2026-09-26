# Growatt NOAH Optimizer 2.1.0

Erster stabiler Stand der 2.1-Reihe für Home Assistant und HACS. Ein Upgrade
von 2.0.0 und den 2.1-Betas übernimmt vorhandene Einstellungen, Entitäten,
Ladeplan-Snapshots und das automatisch erzeugte Dashboard.

## Neu gegenüber 2.0.0

- Optionales PV-Learning aus den letzten gültigen Tagen; die Anwendung des
  Lernfaktors bleibt standardmäßig ausgeschaltet.
- Dynamischer SOC-Ladeplan aus der zeitaufgelösten Forecast.Solar-Kurve mit
  Ist-SOC-Verankerung und separater historischer Ansicht.
- Überbrückung kurzer Forecast-Ausfälle und Schutz vor Stellbefehlen mit
  veralteten oder als offline gemeldeten NOAH-Daten.
- Gebündelte Energieflusskarte, die den Pfad NOAH → Haus ausschließlich aus
  gemessener Ausgangsleistung darstellt.
- Optionaler Batterieheizungsstatus über Growatts OpenAPI sowie gespeicherte
  Zähler der **beobachteten** Einschaltungen heute, diese Woche und diesen
  Monat. Bei eingerichtetem API-Zugang erscheinen sie auch im NOAH-Dashboard.

Ein [aktueller Desktop-Screenshot](screenshots/noah_dashboard_2.1.0.png) zeigt
die Karte mit verfügbarem Status und allen drei Zählern. Eine tatsächlich
aktive Heizphase ist damit noch nicht belegt.

## Installation und Update

In HACS das Repository **Growatt NOAH Optimizer** öffnen und `2.1.0`
installieren. Vorabversionen müssen dafür nicht aktiviert sein. Home Assistant
danach vollständig neu starten. Die OpenAPI-Felder sind optional und benötigen
den Growatt-API-Token und die Seriennummer des NOAH, nicht die des NEO.

Vor der erneuten Freigabe aktiver Steuerung Quellwerte, Netzvorzeichen,
NOAH-Connectivity, Sollwert und Dashboard prüfen. Hinweise stehen in
[`docs/installation.md`](docs/installation.md) und
[`docs/troubleshooting.md`](docs/troubleshooting.md).

## Grenzen

- Die Heizung wird alle fünf Minuten abgefragt. Kürzere Heizzyklen oder
  Zustandswechsel bei Verbindungsunterbrechung können ungezählt bleiben;
  frühere Einschaltungen werden nicht rückwirkend rekonstruiert.
- Bei fehlenden oder mehr als 30 Minuten alten OpenAPI-Daten werden die
  Heizungsentitäten nicht verfügbar; die Optimiererregelung läuft unabhängig.
- Ob NOAH bei sehr kleiner PV-Leistung (beobachtet: etwa 40 W) noch lädt,
  ist geräteabhängig und bleibt Gegenstand einer Messung. Es wurde kein
  pauschaler Schwellwert in die Regelung eingebaut.

# 2.1.0-beta.19 – Historischer SOC-Ladeplan

## 2.1.0-beta.19 – Stabiler historischer SOC-Ladeplan

Bei einem neuen Forecast wird der bisherige Plan bis zum Zeitpunkt der
Aktualisierung beibehalten. Ab diesem Zeitpunkt beginnt ein neuer Zukunftsplan
am gemessenen SOC. Zwischen Forecast-Aktualisierungen bleibt dieser Plan
unverändert; ein neuer Zeitstempel des Restenergiesensors allein löst keine
Neuplanung aus.

Die Tagesprognose im Verlauf stammt nun aus der integrierten Leistungskurve.
Zusätzlich zeigt der Snapshot die **Restenergie im Ladeplan**, die nach der
Normierung auf den Forecast.Solar-Restenergiesensor für den Zukunftsplan
verwendet wurde. Der End-SOC hängt auch vom gemessenen SOC am Anker und der
Sicherheitsreserve ab. Bereits gespeicherte Snapshots werden nicht verändert.

Die Energieflusskarte behält das Layout von Beta 18. Bei 0 W gemessener
NOAH-Ausgangsleistung erscheint weiterhin kein Fluss NOAH → Haus. Die
Ladung bei etwa 40 W PV hängt von NOAH-Eigenverbrauch, Geräte-/MPPT-Schwellen
und den tatsächlich gemessenen Ladeleistungswerten ab; aus der PV-Leistung
allein lässt sich kein Ladefluss ableiten.

Basis: `main` `099470153d273665a8503c226815dbc52816281c`.

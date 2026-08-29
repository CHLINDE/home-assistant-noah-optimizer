# Konfiguration

Dieses Dokument beschreibt die Konfiguration des Growatt NOAH Optimizers für
den stabilen Regelstand `2.0.0` und den aktuellen Pre-Release
`2.1.0-beta.8`.

## 1. Quell-Entitäten

Der Config Flow erwartet:

- saldierte Netzleistung
- NOAH Solar Power
- NOAH Output Power
- NOAH SOC
- NOAH Charging Power
- NOAH Discharge Power
- Forecast.Solar Restprognose heute
- NOAH System Output Power

Leistungssensoren dürfen W oder kW verwenden. Forecast-Energie darf Wh oder kWh
verwenden. Der Optimizer normalisiert intern.

## 2. Netzvorzeichen

Standard:

```text
positiv = Netzbezug
negativ = Netzeinspeisung
```

Bei umgekehrter Quelle **Netzvorzeichen umkehren** aktivieren.

## 3. Berechnung und aktive Steuerung

Die Integration trennt:

```text
Optimierer-Berechnung aktiv
NOAH-Steuerung aktiv
```

Damit können Berechnung und Diagnose beobachtet werden, ohne Stellbefehle an den
NOAH zu senden.

## 4. Dynamische SOC-Steuerung

Der dynamische SOC-Ladeplan nutzt bei nativer Forecast.Solar-Quelle die
zeitaufgelöste Leistungskurve. Relevante Größen sind unter anderem:

- Mindest-SOC
- Ziel-SOC
- Akkukapazität
- Ladewirkungsgrad
- Prognose-Sicherheitsfaktor
- zusätzliche Energiereserve
- SOC-Nachholzeit

Ist keine native Forecast.Solar-Kurve verfügbar, wird automatisch der
Tageslicht-Fallback verwendet.

## 5. PV-Learning

PV-Learning sammelt Tagesverhältnisse aus gemessener PV-Energie und
Forecast.Solar-Referenz. Der gelernte Faktor wird erst nach ausreichend gültigen
Lerntagen als bereit markiert.

Schalter:

```text
Gelernte PV-Korrektur verwenden
```

Die Anwendung ist opt-in. Ein Reset der Lerndaten ist über die zugehörige
Schaltfläche möglich.

## 6. Vorausschauende SOC-Freigabe

Die SOC-Freigabe kann bei ausreichendem SOC-Vorsprung vorhandene Akkuenergie
verwenden, um aktuellen Netzbezug zu reduzieren. Die Freigabe berücksichtigt
den dynamischen Ladeplan und eine prognosebasierte Wiederauflade-Reserve.

Die Funktion ist separat schaltbar und bleibt bei einer neuen Einrichtung aus.

## 7. Controllerstatus

Der Controllerstatus wird über einen eigenen Enum-Sensor bereitgestellt und
zentral über die Übersetzungsdateien lokalisiert.

Typische Zustände:

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

`waiting_for_retry` wird als **Warte auf Stellwertübernahme** beziehungsweise
**Waiting for setpoint confirmation** dargestellt.

## 8. Failsafe und Legacy-Sperre

Fehlen kritische Messwerte über längere Zeit während aktiver Steuerung, erzeugt
die Integration eine persistente Warnung und fordert – soweit möglich – `0 W`
an.

Ist der alte YAML-Optimizer noch aktiv, blockiert die Integration normale
Stellbefehle, um parallele Regler zu vermeiden.

## 9. Dashboard

Das automatische Dashboard verwendet für Power Flow Card Plus:

```text
Grid:
consumption = Netzbezug
production  = Netzeinspeisung

Battery:
consumption = Entladeleistung
production  = Ladeleistung
```

Das Dashboard enthält unter anderem:

- Energiefluss
- PV-Prognose
- dynamischen SOC-Ladeplan
- historische SOC-Ladeplanansicht
- SOC-Abweichung und Ladeplanstatus
- PV-Learning-Diagnose
- Forecast- und Ladeplan-Diagnose
- Reglermodus und Controllerstatus
- Reglerverhalten
- Planung im Detail

Der aktuelle `2.1.0-beta.8`-Stand verwendet nach der korrigierten
Serienfarben-Migration **Dashboard-Template-Version 18**.

## 10. Feste Serienfarben

Ab dem aktuellen `2.1.0-beta.8`-Stand verwendet das generierte Dashboard die
folgende stabile Palette:

```text
Blau    #2196F3
Grün    #009B21
Orange  #FF6A00
Gelb    #FFD800
Cyan    #00FFFF
Violett #B200FF
```

Zuordnung **Dynamischer SOC-Ladeplan**:

```text
Ist-SOC             #2196F3
Dynamisches Soll    #009B21
Ziel-SOC            #FF6A00
Historischer Plan   #FFD800
```

Zuordnung **Reglerverhalten**:

```text
Regler-Soll                   #2196F3
Ist-Ausgang                   #009B21
Eigenverbrauch-Soll           #FF6A00
Ladepriorität-Soll            #FFD800
Erforderliche Ladeleistung    #00FFFF
Dynamische Nachladeleistung   #B200FF
```

Bei der Migration auf Dashboard-Template-Version 18 werden eindeutig erkannte
generierte NOAH-Standarddiagramme einmalig auf die dokumentierte Palette
ausgerichtet. Das gilt auch dann, wenn dort bereits alte `color`-Werte aus
früheren Templates gespeichert sind.

Zusätzliche beziehungsweise benutzerdefinierte ApexCharts-Karten werden nicht
verändert. Die Erkennung erfolgt über bekannte Standard-Kartentitel und die
zugehörigen Entity-Kombinationen.

## 11. Dashboard-Migrationsprinzip

Die Integration ersetzt ein vorhandenes Dashboard nicht pauschal. Migrationen
sind gezielt und versionsgebunden.

Für Beta 8 gilt:

```text
alte Template-Version < 18
→ bekannte ältere Dashboard-Migrationen anwenden
→ Standardchart-Farben für eindeutig erkannte Karten ausrichten
→ Konfiguration speichern
→ Template-Version 18 persistieren
```

Dadurch wird die Migration nur einmal ausgeführt.

## 12. Historienkarte

Die gebündelte Historienkarte wird als Lovelace-Modulressource registriert.
Beta 8 verwendet zur Cache-Invalidierung:

```text
/noah_optimizer/noah-soc-history-card.js?v=8
```

# Growatt NOAH Optimizer v2.2.0-beta.3

## Bugfix: Ruhige Dashboard-Anzeige nach nächtlicher NOAH-Abschaltung

Beta 3 baut auf v2.2.0-beta.2 auf und korrigiert die Anzeige unvollständiger Live-Daten am Morgen.

- **Keine vier Fehlermeldungs-Kacheln mehr:** Wenn die kritischen NOAH-Messwerte (insbesondere der Batterieladezustand) noch fehlen, werden die Standardinstrumente durch eine verständliche Statusmeldung ersetzt.
- **Richtige Freigabebedingung:** Die Live-Anzeige verwendet jetzt „Kritische Daten gültig“ anstatt lediglich „Stellgröße erreichbar“. So werden bei einem nach der Nachtabschaltung wieder verbundenen Gerät keine ungültigen SOC-Werte dargestellt.
- **Unbekannter SOC bleibt unbekannt:** Die Anzeige erfindet keinen Batteriestand und behauptet nicht, dass der letzte Messwert aktuell sei.
- **Automatische Rückkehr zur Normalansicht:** Sobald wieder gültige Messwerte vorhanden sind, erscheinen die bisherigen Energiefluss- und Kennzahlenkarten unverändert.
- **Dashboard-Migration v23:** Bereits unter Beta 2 gespeicherte Standardkarten sowie neu erzeugte Dashboards werden berücksichtigt. Vorhandene persönliche Einstellungen der Online-Karten bleiben erhalten.

### Sicherheit

Die bereits in Beta 2 implementierte SOC-Plausibilitätsprüfung und Sperre der aktiven Ausgangssteuerung bei fehlenden kritischen Messwerten bleiben unverändert.

### Tests

Neue automatische Tests prüfen die Migration bestehender Beta-2-Karten, den Unterschied zwischen Stellgrößen-Erreichbarkeit und Datenverfügbarkeit, die Wiederherstellung der Live-Karten und den Erhalt individueller Darstellungsoptionen.

### Installation

Nach dem Update auf v2.2.0-beta.3 Home Assistant vollständig neu starten, damit die automatische Dashboard-Migration ausgeführt wird.

Die Änderung betrifft die Anzeige. Sie beschleunigt nicht das Einschalten des NOAH und stellt keine fehlenden Messwerte wieder her.

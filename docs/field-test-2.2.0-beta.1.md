# Praxistest 2.2.0-beta.1 – PV-Überschussladung

> **Entwicklungsstand:** Dieser Branch ist noch kein HACS-Release. Kein automatisches Update in Home Assistant. Die lokale Installation bleibt bis zur manuellen Übernahme unverändert.
>
> Das Testen der Beta geschieht auf ausdrückliche Entscheidung der Betreiberin bzw. des Betreibers. Die vorab abgeschaltete aktive Steuerung ist Voraussetzung für den Dateiaustausch.

## 1. Vorbereitung und Sicherung

1. In Home Assistant den Schalter **NOAH-Steuerung aktiv** ausschalten. **Optimierer-Berechnung aktiv** darf eingeschaltet bleiben.
2. Aktuelle Einstellungen dokumentieren, vor allem **Restnetzbezug**, **Stellschritt**, **Deadband**, Betriebsart, **Dynamische SOC-Steuerung** und **Vorausschauende SOC-Freigabe**.
3. Ein vollständiges Home-Assistant-Backup erstellen (**Einstellungen → System → Backups**).
4. Zusätzlich den vollständigen bisherigen Ordner `/config/custom_components/noah_optimizer/` außerhalb von `custom_components` oder auf dem PC als Rückfallkopie sichern. Dieser Schritt ist besonders wichtig, weil HACS für den unveröffentlichten Feature-Branch kein reguläres Versionsupdate anbietet.

## 2. Entwicklungsstand laden

1. ZIP aus dem Branch laden: https://github.com/CHLINDE/home-assistant-noah-optimizer/archive/refs/heads/feature/pv-surplus-charge-priority.zip
2. ZIP lokal entpacken. **Nur** den darin enthaltenen Ordner `custom_components/noah_optimizer/` verwenden, nicht den kompletten Projektordner.
3. Die darin enthaltenen Dateien und Unterordner vollständig nach `/config/custom_components/noah_optimizer/` kopieren und vorhandene Integrationsdateien überschreiben. Kein zusätzliches Verzeichnis `noah_optimizer/noah_optimizer` erzeugen.
4. In `/config/custom_components/noah_optimizer/manifest.json` muss `"version": "2.2.0-beta.1"` stehen.
5. Home Assistant vollständig neu starten. Nicht nur YAML neu laden.
6. Zunächst **NOAH-Steuerung aktiv = Aus** belassen und die Entitäten, MQTT-Connectivity und die Home-Assistant-Protokolle auf Fehler prüfen.
7. Während dieses Tests kein HACS-Update für diese Integration ausführen, weil es die manuell eingesetzte Beta überschreiben könnte.

## 3. Test unter realen PV-Bedingungen

Voraussetzungen: NOAH erreichbar, aktuelle Leistungs- und SOC-Messwerte, Hausstromsensor mit **positiv = Netzbezug, negativ = Einspeisung**, ausreichend PV-Produktion, Akku oberhalb des Mindest-SOC und unterhalb des Ziel-SOC.

1. Betriebsart **Automatik**, **Dynamische SOC-Steuerung aktiv**. Vorhandene übrige Einstellungen zunächst unverändert lassen.
2. Nach erfolgreicher Zustandsprüfung **NOAH-Steuerung aktiv = Ein** setzen.
3. Ein Testfenster mit schwankender PV-Leistung beobachten, idealerweise 15–30 Minuten.
4. Folgende Daten und Zeitpunkte dokumentieren:
   - Netzleistung (vorzeichenbehaftet, W)
   - PV-Leistung (W)
   - NOAH-Ausgangsleistung und Ausgangssoll (W)
   - NOAH-Ladeleistung (W)
   - Ist-SOC, dynamisches SOC-Soll, prognostizierter End-SOC (%)
   - Reglermodus und Controllerstatus
   - Restnetzbezug und Stellschritt (W)
5. **Einspeise-Szenario:** Bei SOC < Ziel-SOC und Einspeisung soll der Sollwert schnell sinken. Im SOC-Halten darf die 5-Minuten-Netzmittelung keine größere Ausgangsleistung erzwingen als die momentane Netzbilanz erlaubt.
6. **PV-Umlenkungs-Szenario:** Bei laufender Akkuladung und Netzbezug darf nur Leistung oberhalb der eingestellten Restnetzbezugsreserve zum Haus umgelenkt werden; die Umlenkung darf nie größer als die aktuelle Ladeleistung sein.
7. **Leistungswechsel:** Wechsel zwischen den Modi beobachten; es soll kein dauerhaftes Pendeln zwischen Netzbezug und Einspeisung auftreten.

**Wichtig:** Der NOAH setzt Stellwerte in konfigurierten Schritten um. Deshalb sind kleine unvermeidbare Abweichungen vom beabsichtigten Restnetzbezug normal. Für eine feinere Regelung kann nach dem ersten Basistest schrittweise `Restnetzbezug = 20 W` und, sofern der NOAH die Schrittweite akzeptiert, `Stellschritt = 10–20 W` geprüft werden. Immer nur einen Parameter gleichzeitig ändern.

## 4. Sofortige Abbruchkriterien

- NOAH-Connectivity ist nicht `on`, relevante Quellwerte sind `unknown` oder `unavailable`.
- Der Controller schreibt trotz erkennbar falscher Messwerte oder fehlerhafter Stellgrößen.
- Unerwartete starke Regelschwingungen, dauerhafter unnötiger Netzbezug oder wiederholte Netzeinspeisung trotz Aufnahmekapazität.
- Fehler im Home-Assistant-Protokoll, die der neuen Integration zugeordnet werden können.

Beim Abbruch **NOAH-Steuerung aktiv = Aus** setzen und auf den gesicherten alten Code zurückrollen.

## 5. Rückkehr zur bisherigen Version

1. **NOAH-Steuerung aktiv = Aus**.
2. Den Beta-Ordner `/config/custom_components/noah_optimizer/` durch die **zuvor gesicherte ursprüngliche Ordnerkopie** ersetzen.
3. Home Assistant vollständig neu starten.
4. Wiederhergestellte `manifest.json`-Version, MQTT-Connectivity, Sensorwerte und Protokolle prüfen.
5. Die vorherigen Reglerparameter wiederherstellen, dann **NOAH-Steuerung aktiv = Ein**, sofern alles plausibel ist.

**Keine Integration aus Geräte & Dienste löschen:** Damit bleiben die Konfiguration und vorhandene History/Entity-IDs erhalten.

## 6. Testbericht

| Zeit | PV W | Netz W | NOAH Output W | NOAH-Soll W | Ladung W | SOC % | Soll-SOC % | Modus | Controllerstatus |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| | | | | | | | | | |

## Stand automatisierter Prüfungen

Die GitHub-CI für den Entwicklungsbranch umfasst pytest, Ruff, Python-Syntaxprüfung, HACS und Hassfest. Die automatisierten Tests simulieren Home Assistant und den Controller, ersetzen aber keinen Praxistest am physischen NOAH.

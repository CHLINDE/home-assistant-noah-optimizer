# Installation

Diese Anleitung beschreibt die Installation und das Update des **Home Assistant
Growatt NOAH Optimizers** für den Pre-Release `2.1.0-beta.8`.

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

| Funktion | Entitätstyp | Einheit |
|---|---|---|
| Saldierte Netzleistung | `sensor` | W oder kW |
| NOAH Solar Power | `sensor` | W oder kW |
| NOAH Output Power | `sensor` | W oder kW |
| NOAH SOC | `sensor` | % |
| NOAH Charging Power | `sensor` | W oder kW |
| NOAH Discharge Power | `sensor` | W oder kW |
| Forecast.Solar Restprognose heute | `sensor` | Wh oder kWh |
| NOAH System Output Power | `number` | W oder kW |

Für den zeitaufgelösten Forecast-Ladeplan muss die Forecast-Entität direkt von
Forecast.Solar stammen. Template- oder Fremdsensoren verwenden automatisch den
Tageslicht-Fallback.

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

Die historische SOC-Ladeplankarte ist Bestandteil der Integration und benötigt
keine zusätzliche HACS-Karte.

## 4. Repository in HACS öffnen

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CHLINDE&repository=home-assistant-noah-optimizer&category=integration)

Alternativ als benutzerdefiniertes Repository hinzufügen:

```text
https://github.com/CHLINDE/home-assistant-noah-optimizer
```

Typ:

```text
Integration
```

> **Home Assistant 2026.8+:** Neue HA-OS-Installationen verwenden standardmäßig
> Port 80. Der HACS-Link selbst enthält keinen Home-Assistant-Port.

## 5. Version 2.1.0-beta.8 installieren

In HACS Vorabversionen für dieses Repository aktivieren und auswählen:

```text
2.1.0-beta.8
```

Danach Home Assistant vollständig neu starten.

## 6. Neue Installation einrichten

Öffne:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

und suche nach:

```text
Growatt NOAH Optimizer
```

Wähle die acht Quell-Entitäten aus.

Zusätzlich stehen zur Verfügung:

- Netzvorzeichen umkehren
- Dashboard in der Seitenleiste anzeigen

Die Seitenleistenanzeige ist standardmäßig aktiv.

## 7. Update auf 2.1.0-beta.8

Vor dem Update empfiehlt sich für die kontrollierte Prüfung:

```text
NOAH-Steuerung aktiv = Aus
Dynamische SOC-Steuerung aktiv = Aus
Vorausschauende SOC-Freigabe aktiv = Aus
```

`2.1.0-beta.8` übernimmt den Funktionsstand der vorherigen 2.1-Betas und
repariert zusätzlich die Dashboard-Farbmigration. Bereits gespeicherte Farben
in eindeutig erkannten NOAH-Standarddiagrammen werden beim Wechsel auf
Template-Version 18 einmalig auf die dokumentierte Palette ausgerichtet.
Zusätzliche oder benutzerdefinierte ApexCharts-Karten bleiben unverändert.

Nach dem Update Home Assistant vollständig neu starten und das NOAH-Dashboard
neu öffnen.

### Update von 2.1.0-beta.7

Beim ersten Start mit Beta 8 wird die gespeicherte Dashboard-Template-Version
von 17 auf 18 angehoben. Dadurch läuft die korrigierte Farb-Migration auch dann,
wenn Beta 7 das Dashboard bereits auf Version 17 gespeichert hatte.

Geändert werden ausschließlich erkannte generierte NOAH-Standardcharts.

### Update von 2.0.0

Beta 8 enthält zusätzlich zum stabilen 2.0.0 unter anderem:

- PV-Learning
- `SOC-Ladeplan halten`
- zeitaufgelöste Forecast.Solar-Leistungskurve
- Forecast-geformten SOC-Ladeplan mit Tageslicht-Fallback
- Forecast-Diagnosewerte und PV-Prognosekarte
- historische SOC-Ladeplanansicht
- persistente Forecast-/Plan-Snapshots
- feste Serienfarben
- Dashboard-Template-Version 18

Die gelernte PV-Korrektur bleibt opt-in.

## 8. Dashboard und Migration

Aktueller Stand:

```text
Dashboard-Template-Version = 18
```

Frühere 2.1-Betas erhöhten die Version schrittweise für PV-Learning,
SOC-Halten, Forecast-Kurve und Historienkarte. `2.1.0-beta.8` erhöht die
Template-Version auf **18** und korrigiert alte gespeicherte Serienfarben in
eindeutig erkannten NOAH-Standarddiagrammen.

Die Erkennung verwendet den bekannten Standard-Kartentitel und die erwartete
Entity-Kombination. Zusätzliche beziehungsweise benutzerdefinierte
ApexCharts-Karten werden nicht verändert.

## 9. Erste Prüfung nach dem Update

1. Unter **Einstellungen → Geräte & Dienste** prüfen, dass der Optimizer geladen ist.
2. Unter **Werkzeuge → Zustände** die Quell-Entitäten kontrollieren.
3. NOAH-Dashboard öffnen.
4. Bei **Reglerverhalten** die sechs Serienfarben prüfen.
5. Historischen SOC-Ladeplan öffnen und Blau/Grün/Orange/Gelb prüfen.
6. Erst danach aktive Steuerung wieder einschalten.

## 10. Erwartete Serienfarben

```text
Blau    #2196F3
Grün    #009B21
Orange  #FF6A00
Gelb    #FFD800
Cyan    #00FFFF
Violett #B200FF
```

Reglerverhalten:

```text
Regler-Soll                   Blau
Ist-Ausgang                   Grün
Eigenverbrauch-Soll           Orange
Ladepriorität-Soll            Gelb
Erforderliche Ladeleistung    Cyan
Dynamische Nachladeleistung   Violett
```

Historischer SOC-Ladeplan:

```text
Ist-SOC                       Blau
Dynamisches Soll              Grün
Ziel-SOC                      Orange
Gespeicherter Plan            Gelb
```

## 11. Browser-/Frontend-Cache

Beta 8 registriert die gebündelte Historienkarte mit:

```text
/noah_optimizer/noah-soc-history-card.js?v=8
```

Der Versionssprung von `v=7` auf `v=8` sorgt dafür, dass bereits geladener
Frontend-Code nicht aus einem alten Browser-Cache weiterverwendet wird.

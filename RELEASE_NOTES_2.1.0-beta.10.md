# 2.1.0-beta.10 – NOAH-Offline-Erkennung

## Added

- Automatische Erkennung des Noah-MQTT-Connectivity-Sensors des konfigurierten
  NOAH.
- Offline-/Stale-Data-Schutz vor gecachten Noah-MQTT-Werten.
- Persistente Home-Assistant-Benachrichtigung bei NOAH-Offline-Zustand.
- Automatisches Entfernen der Benachrichtigung nach Wiederverbindung.

## Safety

- Keine normalen Stellbefehle, solange der NOAH offline ist.
- Kein 0-W-Failsafe-Befehl während eines erkannten Offline-Zustands.
- Ein bereits laufender Missing-Data-Failsafe wird zurückgesetzt, damit nach
  Wiederverbindung nicht sofort ein alter Failsafe-Schreibbefehl ausgelöst wird.
- `Datenstatus` und `Controllerstatus` können bei gecachten Werten nicht mehr
  fälschlich `OK` / `Synchron` bleiben.

## Implementation

Die vorhandene `NoahOptimizerController`-Logik bleibt unverändert und wird von
einem `NoahOfflineGuard` geschützt. Dadurch bleibt die eigentliche Regelung
isoliert von der neuen Geräteerreichbarkeitsprüfung.

Basis dieses Overlays:
`main` Commit `51744ec1cf429636ed975a2410237707b55831ed`
(`2.1.0-beta.9`).

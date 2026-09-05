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

## Review correction

The first feature implementation refreshed the coordinator every 15 seconds
even while the NOAH was offline. Because Noah-MQTT can retain the last PV
power value and PV learning integrates power over elapsed time, this could
create fictitious PV energy during an outage.

The corrected implementation checks connectivity **before** consuming source
states and pauses coordinator/PV-learning refreshes while offline. Source-state
events and periodic controller ticks use the same guard lock.

### Final review correction

The previous guard covered source-state callbacks and the 15-second controller
tick, but the `DataUpdateCoordinator` still had its own scheduled refresh path.
That independent refresh, as well as option/reset-triggered refreshes, could
still consume retained Noah-MQTT values while the physical NOAH was offline.

Beta 10 now uses a guarded coordinator wrapper. The connectivity check runs
before **every** coordinator data update, including:

- initial config-entry refresh
- Home Assistant's scheduled coordinator refresh
- source-state refreshes
- controller-triggered refreshes
- option changes
- PV-learning reset refreshes

When the NOAH is offline, the last snapshot is retained only for display
context, but it is marked unavailable for control, the output target is cleared,
and no cached source values are reprocessed or integrated into PV learning.


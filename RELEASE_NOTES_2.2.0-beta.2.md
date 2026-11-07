# Growatt NOAH Optimizer 2.2.0-beta.2

Base: `v2.2.0-beta.1` (commit `897c85fd`).

## SOC recovery after sleep

- NOAH's retained 0 % SOC after night shutdown is considered an unconfirmed measurement while the configured minimum SOC is above 0 %.
- Two distinct fresh SOC state updates, at least 30 seconds after first seeing 0 %, are required to confirm a real 0 %. Without new measurement timestamps, SOC remains unavailable and active output control remains blocked.
- A configured minimum SOC of 0 % permits 0 % immediately.
- Offline optimizer SOC is **unavailable**, not a fabricated 0 %. The last trusted SOC is stored internally for diagnostics and night-shutdown classification only, never as a live control input.
- The historical SOC card now breaks lines at unavailable values instead of connecting across the overnight data gap.

## Tests

New regression tests cover retained startup zeros, real zero confirmation, no fresh readings, repeated shutdowns, and offline controller data. CI additionally checks the bundled history-card JavaScript syntax.

## Installation

Install this beta from HACS or replace the custom component from the repository branch, then restart Home Assistant. The first valid SOC reading after wake-up should appear normally; if the source persists at 0 % without fresh timestamps, it intentionally remains unavailable.

Do not merge without reviewing GitHub Actions and validating the next NOAH sleep/wake cycle.

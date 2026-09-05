# 2.1.0-beta.11 – Connectivity status fix

## Fixed

Beta 10 could falsely mark a normally operating NOAH as offline after a few
minutes even though the Noah-MQTT `Connectivity` binary sensor still showed
`Connected` / `on`.

The cause was the use of Home Assistant's `State.last_reported` as an MQTT
message-freshness indicator.

Home Assistant MQTT entities do not necessarily write a new entity state when
the same MQTT payload or numeric value is received again. Therefore an entity's
`last_reported` timestamp can remain unchanged even though Noah-MQTT continues
to receive and process current data.

Beta 11 removes:

- the three-minute `Connectivity.last_reported` stale check
- the reconnect barrier based on `System Output Power.last_reported`

## Current offline logic

The optimizer now evaluates the actual Noah-MQTT Connectivity state:

```text
on          -> online
off         -> offline
unknown     -> unavailable
unavailable -> unavailable
```

A previously discovered Connectivity entity that disappears is still treated
as unavailable/offline.

## Safety retained from Beta 10

While the NOAH is genuinely offline:

- no normal output command is sent
- no `0 W` missing-data failsafe command is sent
- coordinator source updates are blocked
- cached Noah-MQTT source values are not reprocessed
- PV learning cannot integrate a cached PV-power value as fictitious production
- the persistent `NOAH Optimizer: NOAH offline` notification is shown

When Connectivity returns to `on`, the offline guard is released without an
additional `last_reported` timestamp requirement.

## Version

```text
2.1.0-beta.11
```

Base: `main` commit `bd9191ff28d31da18ec44d87276bcdb789143874`
(`2.1.0-beta.10`).

No dashboard-template migration is required.

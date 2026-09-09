# 2.1.0-beta.12 – History tooltip and smarter offline notifications

## Added

### Shared tooltip for the historical SOC schedule

The bundled **Historical SOC schedule** card now shows a shared tooltip for the
selected chart timestamp.

Desktop:

- move the mouse over the chart

Mobile / tablet:

- tap the chart

The tooltip shows the timestamp and all available values for:

- Actual SOC
- Dynamic target
- Target SOC
- Saved plan

The marker colors match the existing chart series. The bundled frontend cache
version is increased from `v8` to `v9` so existing installations load the new
card code after the update.

## Changed

### Expected minimum-SOC shutdown at night

A NOAH that becomes unavailable after reaching the configured minimum SOC at
night is treated as an expected sleep/shutdown condition for notification
purposes.

In this situation:

- output control stays blocked
- no normal command is sent
- no 0 W failsafe command is sent
- cached Noah-MQTT values remain blocked from coordinator/PV-learning updates
- **no persistent `NOAH Optimizer: NOAH offline` notification is shown**

The suppression remains active during night / early dawn while the sun
elevation is below 3°. If the NOAH is still unavailable later in the morning,
the normal offline warning becomes active again.

### Startup notification grace period

During the first 90 seconds after integration startup, `unknown`, `unavailable`
or temporarily missing Connectivity states block active control immediately but
do not yet create the persistent offline notification.

An explicit `Connectivity = off` remains actionable immediately unless it is
the expected minimum-SOC night shutdown described above.

This avoids false offline notifications while Noah-MQTT/Home Assistant MQTT
entities are still initializing after a Home Assistant restart.

## Safety

Notification suppression never means that the NOAH is treated as safe to
control. Every non-online Connectivity state continues to block source updates
and all output writes.

## Version

```text
2.1.0-beta.12
```

Base: `main` commit `c8718deb6155791132379a83dc60551f4e15427a`
(`2.1.0-beta.11`).

No dashboard-template migration is required.

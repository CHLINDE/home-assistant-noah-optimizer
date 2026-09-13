# 2.1.0-beta.14 – Intraday SOC plan rebasing

Beta 14 fixes a planning error that becomes especially visible on days where
actual PV production deviates strongly from the morning forecast.

## Problem

The native Forecast.Solar runtime data contains a complete time-resolved power
curve for the current day. Past time slots remain forecast values; they are not
replaced by measured PV production.

The previous SOC schedule was rebuilt from minimum SOC using that complete daily
curve. Later in the day this could therefore still include forecast energy from
the morning even when rain prevented that energy from being produced. The
planned end SOC could consequently be too optimistic and the battery could look
far behind a plan that was no longer physically reachable.

## Intraday plan anchor

When Forecast.Solar publishes a new source update or its native power curve changes, Beta 14 records:

- the current battery SOC, and
- the current timestamp.

That point becomes the new actionable SOC-plan anchor. Only forecast PV energy
after the anchor is integrated for the future charging schedule.

In simplified form:

```text
new plan start = measured SOC at Forecast.Solar update
future SOC gain = usable forecast energy after that timestamp
planned end SOC = new plan start + future SOC gain
```

The existing forecast safety reserve and charging efficiency are still applied.
The plan remains capped between configured minimum SOC and target SOC.

## No continuous self-rebasing

The plan is deliberately **not** anchored to the current SOC on every normal
coordinator refresh. A signature combining the Forecast.Solar source update timestamp and the native power curve is used to detect a genuine forecast update.

This preserves normal catch-up behavior between forecast updates: if the battery
falls behind the active plan, the controller can still detect that deviation and
reserve charging power.

## History

When a new forecast rebases the plan, the already established plan section from
earlier in the same day remains visible in the newest history snapshot. Only the
future section is replaced. This makes forecast corrections traceable instead of
rewriting the past.

## Existing Beta 13 protections

Beta 14 keeps the previous protections unchanged:

- short native Forecast.Solar runtime gaps reuse the last valid same-day plan
  for up to three hours
- NOAH offline source updates remain blocked
- cached NOAH values are not consumed by active control or PV learning
- expected minimum-SOC night shutdown handling remains active
- SOC release hysteresis remains active

## Version

```text
2.1.0-beta.14
```

Base: `main` commit `b17f6beab4fe8a28976f1864a0d4a419ddda7909`
(`2.1.0-beta.13`).

No dashboard-template migration and no translation migration are required.

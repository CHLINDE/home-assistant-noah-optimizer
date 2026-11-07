"""Validate zero-percent NOAH SOC samples after night shutdowns.

Noah-MQTT can publish a retained 0 % while the physical NOAH is asleep.
A single 0 % is therefore not sufficient evidence that the battery is empty.
A genuine 0 % is accepted only after two distinct, fresh HA state updates
while the source is online. Until then the optimizer treats SOC as missing,
so its existing critical-data interlock blocks output control.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

ZERO_CONFIRM_DURATION = timedelta(seconds=30)


@dataclass
class SocZeroGuard:
    """Reject unconfirmed 0 % reports while retaining the last trusted SOC."""

    last_trusted_soc: float | None = None
    _first_zero_at: datetime | None = None
    _last_zero_update: datetime | None = None
    _fresh_zero_updates: int = 0
    _zero_confirmed: bool = False

    def reset_pending(self) -> None:
        """Force a new confirmation after any offline episode."""
        self._first_zero_at = None
        self._last_zero_update = None
        self._fresh_zero_updates = 0
        self._zero_confirmed = False

    def observe(
        self,
        value: float | None,
        *,
        now: datetime,
        source_updated_at: datetime | None,
        minimum_soc: float,
    ) -> float | None:
        """Return a trusted live SOC or None, never a cached control value."""
        if value is None:
            self.reset_pending()
            return None

        if value != 0 or minimum_soc <= 0:
            self.reset_pending()
            self.last_trusted_soc = value
            return value

        if self._zero_confirmed:
            return 0.0

        if self._first_zero_at is None:
            self._first_zero_at = now
            return None

        # A stale 0 %, including one retained from before reconnecting, is
        # never evidence of an awake device. last_reported is deliberately not
        # used: it may advance without a fresh measurement.
        if (
            source_updated_at is not None
            and source_updated_at > self._first_zero_at
            and (
                self._last_zero_update is None
                or source_updated_at > self._last_zero_update
            )
        ):
            self._last_zero_update = source_updated_at
            self._fresh_zero_updates += 1

        if (
            self._fresh_zero_updates >= 2
            and now - self._first_zero_at >= ZERO_CONFIRM_DURATION
        ):
            self._zero_confirmed = True
            self.last_trusted_soc = 0.0
            return 0.0
        return None

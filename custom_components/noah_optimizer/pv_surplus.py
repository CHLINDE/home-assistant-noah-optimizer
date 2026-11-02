"""Pure helpers for grid-balanced PV charging in automatic mode."""

from __future__ import annotations


def pv_redirect_headroom(
    grid_power: float,
    charging_power: float,
    grid_reserve: float,
) -> float:
    """Redirect only grid import above reserve, capped by present charging.

    Positive grid_power means import; negative grid_power means export.
    Limiting redirect to grid import *above* the reserve avoids commands
    which remove the entire import and easily overshoot into feed-in.
    """
    return min(
        max(grid_power - max(grid_reserve, 0.0), 0.0),
        max(charging_power, 0.0),
    )


def instantaneous_hold_cap(
    output_power: float,
    grid_power: float,
    grid_reserve: float,
) -> float:
    """Cap SOC-hold output using *current* grid balance, not only its average.

    An old positive five-minute average must not increase output when the
    latest measurement is already close to zero import or shows export.
    """
    return max(
        output_power + grid_power - max(grid_reserve, 0.0),
        0.0,
    )

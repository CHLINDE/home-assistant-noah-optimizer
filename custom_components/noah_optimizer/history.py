"""Persistent forecast snapshots and history websocket support."""

from __future__ import annotations

from datetime import date, datetime, timedelta
import hashlib
import json
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .forecast_curve import ForecastCurveData

STORAGE_VERSION = 1
MAX_HISTORY_DAYS = 31
MAX_SNAPSHOTS_PER_DAY = 48

_DATA_HISTORY_STORES = f"{DOMAIN}_history_stores"
_DATA_HISTORY_WS_REGISTERED = f"{DOMAIN}_history_ws_registered"


def _compact_points(
    points: tuple[tuple[datetime, float], ...],
) -> list[list[str | float]]:
    """Serialize points in a compact dashboard-friendly representation."""
    return [
        [timestamp.isoformat(), round(float(value), 2)]
        for timestamp, value in points
    ]


def _snapshot_signature(
    curve: ForecastCurveData,
) -> str:
    """Return a stable signature for plan-relevant snapshot content."""
    payload = {
        "raw_power": _compact_points(curve.raw_power),
        "effective_power": _compact_points(curve.effective_power),
        "soc_plan": _compact_points(curve.soc_plan),
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:20]


class NoahHistoryStore:
    """Persist forecast and charging-plan snapshots for recent days."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
    ) -> None:
        """Initialize the history store."""
        self.hass = hass
        self.entry_id = entry_id
        self._store: Store[dict[str, Any]] = Store(
            hass,
            STORAGE_VERSION,
            f"{DOMAIN}.history.{entry_id}",
        )
        self._data: dict[str, Any] = {"days": {}}

    async def async_load(self) -> None:
        """Load persisted history data."""
        data = await self._store.async_load()
        if isinstance(data, dict) and isinstance(data.get("days"), dict):
            self._data = data
        self._prune_old_days()

    async def async_save(self) -> None:
        """Persist history data immediately."""
        await self._store.async_save(self._data)

    async def async_record_forecast_snapshot(
        self,
        curve: ForecastCurveData,
        *,
        forecast_factor: float,
        pv_learning_factor: float,
        pv_learning_applied: bool,
        effective_factor: float,
        battery_capacity_kwh: float,
        efficiency: float,
        forecast_safety_kwh: float,
        min_soc: float,
        target_soc: float,
    ) -> bool:
        """Store a new forecast/plan snapshot when the plan actually changed."""
        if not curve.soc_plan:
            return False

        metadata: dict[str, float | bool] = {
            "forecast_factor": round(float(forecast_factor), 4),
            "pv_learning_factor": round(float(pv_learning_factor), 4),
            "pv_learning_applied": bool(pv_learning_applied),
            "effective_factor": round(float(effective_factor), 4),
            "battery_capacity_kwh": round(float(battery_capacity_kwh), 4),
            "efficiency": round(float(efficiency), 4),
            "forecast_safety_kwh": round(float(forecast_safety_kwh), 4),
            "min_soc": round(float(min_soc), 2),
            "target_soc": round(float(target_soc), 2),
        }

        signature = _snapshot_signature(curve)
        local_day = dt_util.as_local(curve.soc_plan[0][0]).date().isoformat()
        days = self._data.setdefault("days", {})
        day_data = days.setdefault(local_day, {"snapshots": []})
        snapshots = day_data.setdefault("snapshots", [])

        if snapshots and snapshots[-1].get("signature") == signature:
            return False

        captured_at = dt_util.utcnow()
        snapshot = {
            "captured_at": captured_at.isoformat(),
            "forecast_updated_at": (
                curve.updated_at.isoformat() if curve.updated_at else None
            ),
            "signature": signature,
            "raw_power": _compact_points(curve.raw_power),
            "effective_power": _compact_points(curve.effective_power),
            "soc_plan": _compact_points(curve.soc_plan),
            "raw_day_energy_kwh": round(curve.raw_day_energy_kwh, 3),
            "effective_day_energy_kwh": round(
                curve.effective_day_energy_kwh,
                3,
            ),
            "planned_end_soc": round(curve.planned_end_soc, 1),
            **metadata,
        }
        snapshots.append(snapshot)

        if len(snapshots) > MAX_SNAPSHOTS_PER_DAY:
            del snapshots[:-MAX_SNAPSHOTS_PER_DAY]

        self._prune_old_days()
        await self.async_save()
        return True

    def get_day(self, requested_day: str) -> dict[str, Any]:
        """Return snapshots for one local calendar day."""
        day_data = self._data.get("days", {}).get(requested_day, {})
        snapshots = day_data.get("snapshots", [])
        if not isinstance(snapshots, list):
            snapshots = []
        return {
            "date": requested_day,
            "retention_days": MAX_HISTORY_DAYS,
            "snapshots": snapshots,
        }

    def _prune_old_days(self) -> None:
        """Keep only the configured rolling history window."""
        days = self._data.setdefault("days", {})
        if not isinstance(days, dict):
            self._data["days"] = {}
            return

        cutoff = dt_util.now().date() - timedelta(days=MAX_HISTORY_DAYS - 1)
        for key in list(days):
            try:
                stored_day = date.fromisoformat(key)
            except (TypeError, ValueError):
                days.pop(key, None)
                continue
            if stored_day < cutoff:
                days.pop(key, None)


@callback
def async_register_history_store(
    hass: HomeAssistant,
    entry_id: str,
    store: NoahHistoryStore,
) -> None:
    """Expose a history store to the dashboard websocket endpoint."""
    stores = hass.data.setdefault(_DATA_HISTORY_STORES, {})
    stores[entry_id] = store

    if not hass.data.get(_DATA_HISTORY_WS_REGISTERED):
        websocket_api.async_register_command(hass, websocket_get_history_snapshots)
        hass.data[_DATA_HISTORY_WS_REGISTERED] = True


@callback
def async_unregister_history_store(
    hass: HomeAssistant,
    entry_id: str,
) -> None:
    """Remove a config-entry store from websocket lookup."""
    stores = hass.data.get(_DATA_HISTORY_STORES)
    if isinstance(stores, dict):
        stores.pop(entry_id, None)


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/history_snapshots",
        vol.Required("entry_id"): str,
        vol.Required("date"): str,
    }
)
@websocket_api.async_response
async def websocket_get_history_snapshots(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return persisted forecast/plan snapshots for one day."""
    requested_day = msg["date"]
    try:
        parsed_day = date.fromisoformat(requested_day)
    except ValueError:
        parsed_day = None

    if parsed_day is None or parsed_day.isoformat() != requested_day:
        connection.send_error(
            msg["id"],
            "invalid_date",
            "Date must use YYYY-MM-DD format",
        )
        return

    stores = hass.data.get(_DATA_HISTORY_STORES, {})
    store = stores.get(msg["entry_id"]) if isinstance(stores, dict) else None
    if not isinstance(store, NoahHistoryStore):
        connection.send_error(
            msg["id"],
            "not_found",
            "NOAH Optimizer history store is not available",
        )
        return

    connection.send_result(msg["id"], store.get_day(requested_day))

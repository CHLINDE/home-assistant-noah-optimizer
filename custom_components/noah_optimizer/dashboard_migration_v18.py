"""Dashboard template-v19 color migration for the NOAH Optimizer.

The existing dashboard implementation remains the single source for dashboard
creation and all older migrations. This module installs the stricter template
v19 series-color migration and then delegates to dashboard.py.

Template v19 replaces stale explicit series colors only on recognized generated
NOAH standard charts. User-created/custom ApexCharts cards are not modified.
"""

from __future__ import annotations

from typing import Any

from . import dashboard as _dashboard

DASHBOARD_TEMPLATE_VERSION = 19
_PATCH_MARKER = "_noah_template_v19_color_patch_installed"


def _apply_standard_series_colors_v19(
    config: dict[str, Any],
    replacements: dict[str, str],
) -> bool:
    """Apply the stable palette to recognized generated NOAH charts.

    Recognition deliberately combines the known chart title with the expected
    entity set. This allows stale colors from earlier generated dashboards to
    be corrected without overwriting unrelated/user-created ApexCharts cards.

    Returning ``True`` for a recognized standard chart also ensures that the
    storage version can be persisted as template v19 even when its colors were
    already correct.
    """
    changed = False
    recognized_standard_chart = False

    for card in _dashboard._iter_dicts(config):
        if card.get("type") != "custom:apexcharts-card":
            continue

        series = card.get("series")
        if not isinstance(series, list):
            continue

        header = card.get("header")
        title = header.get("title") if isinstance(header, dict) else None

        entity_ids = {
            item.get("entity")
            for item in series
            if isinstance(item, dict)
            and isinstance(item.get("entity"), str)
        }

        colors: dict[str, str] | None = None
        forecast_curve = False

        forecast_generators = [
            item.get("data_generator")
            for item in series
            if isinstance(item, dict)
            and item.get("entity") == replacements["__FORECAST_CURVE__"]
            and isinstance(item.get("data_generator"), str)
        ]

        if (
            title in {"PV-Prognose", "PV forecast"}
            and {
                replacements["__FORECAST_CURVE__"],
                replacements["__SOLAR_POWER__"],
            }.issubset(entity_ids)
            and any(
                "raw_power" in generator
                for generator in forecast_generators
            )
            and any(
                "effective_power" in generator
                for generator in forecast_generators
            )
        ):
            forecast_curve = True

        elif (
            title in {
                "Dynamischer SOC-Ladeplan",
                "Dynamic SOC charging schedule",
            }
            and {
                replacements["__SOC__"],
                replacements["__DYNAMIC_SOC_TARGET__"],
                replacements["__TARGET_SOC__"],
            }.issubset(entity_ids)
        ):
            colors = {
                replacements["__SOC__"]: "#2196F3",
                replacements["__DYNAMIC_SOC_TARGET__"]: "#009B21",
                replacements["__TARGET_SOC__"]: "#FF6A00",
            }

        elif (
            title in {
                "Energieplanung bis Sonnenuntergang",
                "Energy planning until sunset",
            }
            and {
                replacements["__EFFECTIVE_FORECAST__"],
                replacements["__CHARGE_NEED__"],
                replacements["__EXPECTED_LOAD_ENERGY__"],
                replacements["__FORECAST_MARGIN__"],
            }.issubset(entity_ids)
        ):
            colors = {
                replacements["__EFFECTIVE_FORECAST__"]: "#2196F3",
                replacements["__CHARGE_NEED__"]: "#009B21",
                replacements["__EXPECTED_LOAD_ENERGY__"]: "#FF6A00",
                replacements["__FORECAST_MARGIN__"]: "#FFD800",
            }

        elif (
            title in {"Leistung heute", "Power today"}
            and {
                replacements["__SOLAR_POWER__"],
                replacements["__OUTPUT_POWER__"],
                replacements["__GRID_IMPORT__"],
                replacements["__GRID_EXPORT__"],
                replacements["__BATTERY_POWER__"],
                replacements["__SOC__"],
            }.issubset(entity_ids)
        ):
            colors = {
                replacements["__SOLAR_POWER__"]: "#2196F3",
                replacements["__OUTPUT_POWER__"]: "#009B21",
                replacements["__GRID_IMPORT__"]: "#FF6A00",
                replacements["__GRID_EXPORT__"]: "#FFD800",
                replacements["__BATTERY_POWER__"]: "#00FFFF",
                replacements["__SOC__"]: "#B200FF",
            }

        elif title in {"Reglerverhalten", "Controller behavior"}:
            # Existing dashboards can contain either the older five-series
            # controller chart or the current six-series variant. The dynamic
            # required charge-power series was added later, so requiring it
            # would prevent the color migration from recognizing older stored
            # dashboards.
            core_entities = {
                replacements["__OUTPUT_TARGET__"],
                replacements["__OUTPUT_POWER__"],
                replacements["__SELF_CONSUMPTION_TARGET__"],
                replacements["__CHARGE_PRIORITY_TARGET__"],
                replacements["__REQUIRED_CHARGE_POWER__"],
            }
            if core_entities.issubset(entity_ids):
                colors = {
                    replacements["__OUTPUT_TARGET__"]: "#2196F3",
                    replacements["__OUTPUT_POWER__"]: "#009B21",
                    replacements["__SELF_CONSUMPTION_TARGET__"]: "#FF6A00",
                    replacements["__CHARGE_PRIORITY_TARGET__"]: "#FFD800",
                    replacements["__REQUIRED_CHARGE_POWER__"]: "#00FFFF",
                }
                dynamic_required = replacements[
                    "__DYNAMIC_REQUIRED_CHARGE_POWER__"
                ]
                if dynamic_required in entity_ids:
                    colors[dynamic_required] = "#B200FF"

        if not forecast_curve and colors is None:
            continue

        recognized_standard_chart = True

        for item in series:
            if not isinstance(item, dict):
                continue

            entity_id = item.get("entity")
            color: str | None = None

            if forecast_curve:
                if entity_id == replacements["__FORECAST_CURVE__"]:
                    generator = item.get("data_generator")
                    if (
                        isinstance(generator, str)
                        and "raw_power" in generator
                    ):
                        color = "#2196F3"
                    elif (
                        isinstance(generator, str)
                        and "effective_power" in generator
                    ):
                        color = "#009B21"
                elif entity_id == replacements["__SOLAR_POWER__"]:
                    color = "#FF6A00"

            elif colors is not None and isinstance(entity_id, str):
                color = colors.get(entity_id)

            if color is not None and item.get("color") != color:
                item["color"] = color
                changed = True

    return changed or recognized_standard_chart


def _install_template_v19_migration() -> None:
    """Extend dashboard.py with the strict v19 color migration exactly once."""
    _dashboard.DASHBOARD_TEMPLATE_VERSION = DASHBOARD_TEMPLATE_VERSION

    if getattr(_dashboard, _PATCH_MARKER, False):
        return

    # IMPORTANT:
    # Do not chain the old v17 color migration here. The v17 implementation
    # recognizes cards mainly from their entity combinations and can therefore
    # add colors to a user-created ApexCharts card that happens to use the same
    # NOAH entities.
    #
    # The v19 implementation covers all generated NOAH standard ApexCharts but
    # additionally requires the known German/English title. Replacing the old
    # color migration therefore fixes stale colors while preserving custom
    # charts.
    _dashboard._apply_standard_series_colors = (
        _apply_standard_series_colors_v19
    )

    setattr(_dashboard, _PATCH_MARKER, True)


_install_template_v19_migration()

# Keep dashboard.py as the central implementation. Its async_ensure_dashboard()
# now sees DASHBOARD_TEMPLATE_VERSION == 19 and the strict v19 color migration.
async_ensure_dashboard = _dashboard.async_ensure_dashboard
remove_dashboard_panel = _dashboard.remove_dashboard_panel

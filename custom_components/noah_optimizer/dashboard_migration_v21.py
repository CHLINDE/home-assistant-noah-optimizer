"""Dashboard template v21 adds an optional NOAH battery-heating card.

The heater card is inserted during dashboard setup whenever the OpenAPI
entities exist, including when credentials were added after the dashboard
had already migrated to this template version.
"""

from . import dashboard_migration_v20 as _previous_migration  # noqa: F401
from . import dashboard as _dashboard

_dashboard.DASHBOARD_TEMPLATE_VERSION = 21

async_ensure_dashboard = _dashboard.async_ensure_dashboard
remove_dashboard_panel = _dashboard.remove_dashboard_panel

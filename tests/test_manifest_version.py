"""Release metadata is internally consistent in beta branches."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_integration_manifest_version() -> None:
    manifest = json.loads(
        (ROOT / "custom_components" / "noah_optimizer" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["version"] == "2.2.0-beta.1"
    assert manifest["domain"] == "noah_optimizer"
    assert manifest["requirements"] == []

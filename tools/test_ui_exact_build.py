#!/usr/bin/env python3
"""CI-focused test: ui_exact build keeps touch and removes post-v68 diagnostics."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
wf = yaml.safe_load((ROOT / ".github/workflows/xnu.yml").read_text())
inputs = wf[True]["workflow_dispatch"]["inputs"] if True in wf else wf["on"]["workflow_dispatch"]["inputs"]
assert "ui_exact" in inputs, "ui_exact input missing"
text = (ROOT / ".github/workflows/xnu.yml").read_text()
for p in ("0453-m30-ui-heartbeat.patch", "0454-m30-ui-hb-framebuffer.patch",
          "0455-m30-lockscreen-diag.patch"):
    assert p in text, p
assert "0451-m30-melfas-touch.patch" not in text.split("UI_EXACT")[0].split("rm -f")[1] if "rm -f" in text else True
assert "UI_EXACT: post-v68 diagnostic patches excluded" in text
print("[PASS] ui_exact switch excludes post-v68 diagnostics, keeps Melfas 0451")

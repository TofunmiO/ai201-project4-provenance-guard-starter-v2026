#!/usr/bin/env python3
"""
Capstone demo: force each stage to fail and show what the writer gets back and
what the log records.

    python demo_failures.py

It does not need the server running, and it never touches logs/audit.jsonl. It
points the app at a temporary log folder, then makes one stage fail at a time:

    1. the detector crashes   (stands in for: model won't load, out of memory)
    2. the style signal crashes
    3. the main audit log can't be written

For each it prints the HTTP status and JSON the writer sees, then the entry the
failure left behind. A normal request runs first as the control.
"""

import json
import tempfile
from pathlib import Path

import config

TMP = Path(tempfile.mkdtemp(prefix="pg_demo_"))
config.LOG_DIR = TMP
config.AUDIT_LOG = TMP / "audit.jsonl"
config.AUDIT_FALLBACK_LOG = TMP / "audit_fallback.jsonl"
config.RATE_LIMITING_ENABLED = False   # a demo, not a flood

import app as service      # noqa: E402  (after config is pointed at the temp folder)
import audit               # noqa: E402
import detector            # noqa: E402
import stylometry          # noqa: E402

TEXT = " ".join(["The quick brown fox jumps over the lazy dog today."] * 8)  # 72 words
client = service.app.test_client()


def show(title, creator_id, new_entries):
    response = client.post("/submit", json={"text": TEXT, "creator_id": creator_id})
    print(f"\n=== {title}")
    print(f"writer sees: HTTP {response.status_code}")
    print(json.dumps(response.get_json(), indent=2))
    for label, path in new_entries:
        lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        print(f"{label}: {len(lines)} entr{'y' if len(lines) == 1 else 'ies'}")
        if lines:
            print("  last:", lines[-1])


def crash(message, kind=RuntimeError):
    def raiser(*args, **kwargs):
        raise kind(message)
    return raiser


real_model, real_style = detector.model_signal, stylometry.style_signal

show("0. control: nothing fails", "demo_ok", [("main log", config.AUDIT_LOG)])

detector.model_signal = crash("CUDA out of memory")
show("1. detector crashes", "demo_detector", [("main log", config.AUDIT_LOG)])
detector.model_signal = real_model

stylometry.style_signal = crash("division by zero", ZeroDivisionError)
show("2. style signal crashes", "demo_style", [("main log", config.AUDIT_LOG)])
stylometry.style_signal = real_style

# Make the main log unwritable: a directory can't be opened for appending.
config.AUDIT_LOG = TMP / "audit_is_a_folder"
config.AUDIT_LOG.mkdir()
show("3. the main audit log can't be written", "demo_audit",
     [("fallback log", config.AUDIT_FALLBACK_LOG)])

print(f"\n(temporary logs in {TMP}; your real logs/audit.jsonl was not touched)")

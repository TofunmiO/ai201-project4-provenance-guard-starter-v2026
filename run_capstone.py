#!/usr/bin/env python3
"""
Run capstone criteria 1 to 4 three times each.

    python run_capstone.py

No server needs to be running. The script loads the real app and sends requests
through Flask's test client, so it runs the same /submit code a server would.
Criterion 5 (the original system still works) is run separately with
`python run_eval.py` against a running server; see the README.

What it does, once per trial:

  * Points the audit log at a fresh folder, results/capstone/run_N/, and KEEPS
    it. Each run leaves its own audit.jsonl and audit_fallback.jsonl there, so
    anyone can open the files and see exactly what the test produced. Your real
    logs/audit.jsonl is never touched.
  * Forces each stage to fail, on purpose:
        detector      model_signal is replaced by a function that raises
        style signal  style_signal is replaced by a function that raises
        audit write   the main log path is pointed at a folder, which cannot be
                      opened for appending
    The other stages stay real, so a "stage fails" request really runs the model
    for the stages before it.
  * Checks each criterion and prints a pass/fail line with the evidence.

Rate limiting is switched off here (config.RATE_LIMITING_ENABLED = False)
because one process sends many requests as one caller. That setting only affects
this script; config.py is not edited.

Criterion 2 compares the new entry's timestamp with the moment the request was
sent, both to the millisecond (audit.py::_now records milliseconds).
"""

import datetime as dt
import json
import shutil
import sys

import config

config.RATE_LIMITING_ENABLED = False   # this script only; see the docstring

import app as service        # noqa: E402  (after the setting above)
import audit                 # noqa: E402
import detector              # noqa: E402
import stylometry            # noqa: E402
from eval_texts import HUMAN_TEXTS   # noqa: E402

TRIALS = 3
TEXT = HUMAN_TEXTS[5][1]      # H06: 113 words, a real human text, valid length
STAGES = ["detector", "style", "audit"]
OUT = config.RESULTS_DIR / "capstone"

client = service.app.test_client()

REAL_MODEL = detector.model_signal
REAL_STYLE = stylometry.style_signal


def _raise(message):
    def raiser(*args, **kwargs):
        raise RuntimeError(message)
    return raiser


class Forced:
    """Context manager: make one stage fail for the length of a `with` block."""

    def __init__(self, stage, run_dir):
        self.stage = stage
        self.run_dir = run_dir

    def __enter__(self):
        if self.stage == "detector":
            detector.model_signal = _raise("forced failure: detector")
        elif self.stage == "style":
            stylometry.style_signal = _raise("forced failure: style signal")
        elif self.stage == "audit":
            # A folder can't be opened for appending, so the main log is unwritable.
            blocked = self.run_dir / "audit_unwritable"
            blocked.mkdir(exist_ok=True)
            config.AUDIT_LOG = blocked

    def __exit__(self, *exc):
        detector.model_signal = REAL_MODEL
        stylometry.style_signal = REAL_STYLE
        config.AUDIT_LOG = self.run_dir / "audit.jsonl"


def submit(creator):
    return client.post("/submit", json={"text": TEXT, "creator_id": creator})


def main_log():
    return audit.read_entries()


def fallback_log():
    path = config.AUDIT_FALLBACK_LOG
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def failed_entries(entries, stage):
    return [e for e in entries if e.get("event") == "failed" and e.get("stage") == stage]


def run_trial(n):
    run_dir = OUT / f"run_{n}"
    if run_dir.exists():
        shutil.rmtree(run_dir)       # our own output folder, rebuilt each run
    run_dir.mkdir(parents=True)
    config.LOG_DIR = run_dir
    config.AUDIT_LOG = run_dir / "audit.jsonl"
    config.AUDIT_FALLBACK_LOG = run_dir / "audit_fallback.jsonl"

    result = {"run_dir": run_dir, "c1": {}, "c2": {}, "c3": {}, "c4": {}, "evidence": {}}

    # ── Criteria 1, 2 and 3: force each stage and look at what comes back ──
    for stage in STAGES:
        main_before = main_log()
        fallback_before = fallback_log()
        sent = dt.datetime.now(dt.timezone.utc)
        sent_ms = sent.replace(microsecond=(sent.microsecond // 1000) * 1000)

        with Forced(stage, run_dir):
            response = submit(f"capstone_c1_{stage}_{n}")
        body = response.get_json(silent=True)

        # Criterion 1: 503, JSON, error / message / next_step all non-empty.
        ok1 = (response.status_code == 503 and isinstance(body, dict)
               and all(isinstance(body.get(k), str) and body.get(k).strip()
                       for k in ("error", "message", "next_step")))
        result["c1"][stage] = ok1
        result["evidence"].setdefault("c1", {})[stage] = {
            "status": response.status_code, "body": body}

        main_new = main_log()[len(main_before):]
        fallback_new = fallback_log()[len(fallback_before):]

        if stage in ("detector", "style"):
            # Criterion 2: one new failed entry in audit.jsonl, right stage, and
            # a timestamp not earlier than the moment the request was sent.
            entry = main_new[0] if len(main_new) == 1 else {}
            stamp = entry.get("timestamp")
            later = bool(stamp) and dt.datetime.fromisoformat(stamp) >= sent_ms
            ok2 = (len(main_new) == 1 and entry.get("event") == "failed"
                   and entry.get("stage") == stage and later)
            result["c2"][stage] = ok2
            result["evidence"].setdefault("c2", {})[stage] = {
                "request_sent_at": sent.isoformat(timespec="milliseconds"),
                "new_entries_in_audit_jsonl": len(main_new),
                "entry": {k: entry.get(k) for k in
                          ("timestamp", "event", "stage", "error_type", "duration_ms")},
            }
        else:
            # Criterion 3: audit write fails -> entry lands in the fallback file,
            # and the response says record_failed.
            failed_fb = failed_entries(fallback_new, "audit")
            ok3 = (response.status_code == 503 and isinstance(body, dict)
                   and body.get("error") == "record_failed"
                   and len(failed_fb) == 1
                   and failed_fb[0].get("primary_log_failed") is True)
            result["c3"]["audit"] = ok3
            result["evidence"]["c3"] = {
                "status": response.status_code, "body": body,
                "new_entries_in_fallback": len(fallback_new),
                "failed_entry": {k: (failed_fb[0].get(k) if failed_fb else None) for k in
                                 ("timestamp", "event", "stage", "error_type",
                                  "primary_log_failed")},
            }

    # ── Criterion 4: replay each logged input under the same forced failure ──
    for stage in STAGES:
        source = main_log() if stage != "audit" else fallback_log()
        logged = failed_entries(source, stage)
        if not logged or not logged[-1].get("input"):
            result["c4"][stage] = False
            result["evidence"].setdefault("c4", {})[stage] = {"error": "no logged input"}
            continue
        replay_text = logged[-1]["input"]
        before_main, before_fb = len(main_log()), len(fallback_log())
        with Forced(stage, run_dir):
            response = client.post("/submit", json={"text": replay_text,
                                                    "creator_id": f"capstone_c4_{stage}_{n}"})
        new = (main_log()[before_main:] if stage != "audit"
               else fallback_log()[before_fb:])
        again = failed_entries(new, stage)
        ok4 = (replay_text == TEXT and response.status_code == 503 and len(again) == 1)
        result["c4"][stage] = ok4
        result["evidence"].setdefault("c4", {})[stage] = {
            "replayed_input_matches_original": replay_text == TEXT,
            "status": response.status_code,
            "stage_in_original_entry": logged[-1].get("stage"),
            "stage_in_replay_entry": again[0].get("stage") if again else None,
        }
    return result


def score(results, key):
    return [sum(1 for v in r[key].values() if v) for r in results]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for n in range(1, TRIALS + 1):
        print(f"\n=== trial {n}")
        r = run_trial(n)
        results.append(r)
        for key, label, total in (("c1", "1. 503 + error/message/next_step", 3),
                                  ("c2", "2. one failed entry, right stage, new timestamp", 2),
                                  ("c3", "3. fallback entry + record_failed", 1),
                                  ("c4", "4. replay fails at the same stage", 3)):
            got = sum(1 for v in r[key].values() if v)
            detail = ", ".join(f"{s}={'ok' if v else 'FAIL'}" for s, v in r[key].items())
            print(f"  criterion {label}: {got}/{total}   ({detail})")
        print(f"  logs kept in {r['run_dir'].relative_to(config.ROOT)}/")

    targets = {"c1": 3, "c2": 2, "c3": 1, "c4": 3}
    names = {"c1": "1. Failure returns a 503 with error, message, next_step",
             "c2": "2. Detector/style failure leaves one new failed entry",
             "c3": "3. Audit failure lands in the fallback, says record_failed",
             "c4": "4. Replaying the logged input fails at the same stage"}
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    path = config.RESULTS_DIR / f"capstone_run_{stamp}.md"
    lines = [f"# Capstone run log — criteria 1 to 4", "",
             "- Produced by: `run_capstone.py::main`", f"- {TRIALS} trials · {stamp}",
             f"- Each trial's logs are kept in `results/capstone/run_N/`", "",
             "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |", "|---|---|---|---|---|---|"]
    for key in ("c1", "c2", "c3", "c4"):
        t = targets[key]
        got = score(results, key)
        verdict = "MET" if all(g == t for g in got) else "MISSED"
        lines.append(f"| {names[key]} | {t} of {t} | "
                     + " | ".join(f"{g}/{t}" for g in got) + f" | {verdict} |")
    lines.append("| 5. Original system still works | 5 of 5 | (run_eval.py) | | | |")
    lines += ["", "---", "", "## What actually came back (trial 1)", ""]
    for key, title in (("c1", "Criterion 1: response for each forced stage"),
                       ("c2", "Criterion 2: the new entry in audit.jsonl"),
                       ("c3", "Criterion 3: the response and the fallback entry"),
                       ("c4", "Criterion 4: the replay")):
        lines += [f"### {title}", "", "```json",
                  json.dumps(results[0]["evidence"][key], indent=2), "```", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")

    all_ok = all(score(results, k)[i] == targets[k] for k in targets for i in range(TRIALS))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()

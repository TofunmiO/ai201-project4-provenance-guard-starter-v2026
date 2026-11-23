#!/usr/bin/env python3
"""
Measure the cost of one run, in seconds of compute (capstone, Milestone 3).

    PORT=5001 python app.py                    # restart it first: see below
    python measure_cost.py --url http://127.0.0.1:5001

How it measures:
  1. One COLD request first, to a freshly started server. The detector loads
     gpt2 on its first use, so this one is slow and is reported on its own.
  2. Then ten WARM requests, one for each text in eval_texts.HUMAN_TEXTS
     (H01-H10), so the average reflects texts of different lengths.
  3. For each request it records the time the caller waited (wall clock) and the
     server's own duration_ms, model_ms and style_ms from the audit log entry.

The average is over the ten warm requests. If the server has already scored
something, the first request isn't cold; the script says so rather than
presenting it as a cold start. Restart the server to get a real cold number.
"""

import argparse
import datetime as dt
import statistics
import sys
import time

import config
from eval_texts import HUMAN_TEXTS

COLD_TEXT = " ".join(["Measuring how long the first request takes while the model loads."] * 6)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default=f"http://{config.HOST}:{config.PORT}")
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    import requests

    try:
        health = requests.get(f"{args.url}/health", timeout=5).json()
    except Exception:  # noqa: BLE001
        sys.exit(f"Nothing answering at {args.url}. Start it:  PORT=5001 python app.py")
    cold = not health.get("detector_loaded")
    if not cold:
        print("!! The detector is already loaded, so the first request below is NOT "
              "a cold start. Restart the server for a real cold number.\n")

    def send(text, creator):
        start = time.monotonic()
        response = requests.post(f"{args.url}/submit",
                                 json={"text": text, "creator_id": creator},
                                 timeout=args.timeout)
        wall = time.monotonic() - start
        body = response.json()
        return response.status_code, body, wall

    def log_entry(content_id):
        entries = requests.get(f"{args.url}/log", timeout=10).json()["entries"]
        return next((e for e in entries if e.get("content_id") == content_id), {})

    rows = []
    status, body, wall = send(COLD_TEXT, "cost_cold")
    entry = log_entry(body.get("content_id"))
    cold_row = ("cold start" if cold else "first (NOT cold)", status, wall, entry)
    print(f"{cold_row[0]:>16}: HTTP {status}  wall {wall:6.2f}s  "
          f"model {entry.get('model_ms')} ms  total {entry.get('duration_ms')} ms")

    for tid, text in HUMAN_TEXTS:
        status, body, wall = send(text, f"cost_{tid}")
        entry = log_entry(body.get("content_id"))
        rows.append((tid, status, wall, entry))
        print(f"{tid:>16}: HTTP {status}  wall {wall:6.2f}s  "
              f"model {entry.get('model_ms')} ms  style {entry.get('style_ms')} ms  "
              f"total {entry.get('duration_ms')} ms  ({entry.get('word_count')} words)")

    ok = [r for r in rows if r[1] == 200]
    walls = [r[2] for r in ok]
    totals = [r[3]["duration_ms"] for r in ok]
    models = [r[3]["model_ms"] for r in ok]
    styles = [r[3]["style_ms"] for r in ok]
    print(f"\n{len(ok)} of {len(rows)} warm requests succeeded.")
    if not ok:
        sys.exit("Nothing to average.")
    summary = [
        f"cold start (first request, wall clock): {cold_row[2]:.2f} s"
        + ("" if cold else "  (NOT a true cold start)"),
        f"warm average, wall clock: {statistics.mean(walls):.2f} s",
        f"warm average, server duration_ms: {statistics.mean(totals):.0f} ms",
        f"  of which model_ms: {statistics.mean(models):.0f} ms",
        f"  of which style_ms: {statistics.mean(styles):.0f} ms",
        f"warm range, server duration_ms: {min(totals)} to {max(totals)} ms",
    ]
    print("\n".join(summary))

    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    path = config.RESULTS_DIR / f"cost_{stamp}.md"
    lines = [f"# Cost of one run — {stamp}", "", "```", *summary, "```", "",
             "| request | status | wall (s) | model_ms | style_ms | duration_ms | words |",
             "|---|---|---|---|---|---|---|"]
    for name, status, wall, entry in [cold_row] + rows:
        lines.append(f"| {name} | {status} | {wall:.2f} | {entry.get('model_ms')} | "
                     f"{entry.get('style_ms')} | {entry.get('duration_ms')} | "
                     f"{entry.get('word_count')} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()

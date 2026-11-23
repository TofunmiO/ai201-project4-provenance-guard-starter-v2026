#!/usr/bin/env python3
"""
Capstone criterion 5: do the five ORIGINAL criteria still give what they gave
before the capstone?

    python run_eval.py --url http://127.0.0.1:5001 --label capstone_after
    python check_regression.py results/run_<stamp>_capstone_after.md

`run_eval.py` saves what came back for the original five criteria. This reads
that file, applies each criterion's rule from criteria.md to every trial, and
compares the answer with the Nov 16 "after" run from unit 8
(results/run_2026-11-16_2148_after.md), or any file given with --baseline.

It judges nothing the criteria don't already say. The rules:

    1. at most 1 of 10 human texts labeled "ai", on each trial
    2. the 5 bad inputs all return 400 and add exactly 5 rejection entries
    3. all three labels (human, unsure, ai) appear
    4. 5 of 5 appeals return 200 / under_review; the unknown id returns 404
       and adds 0 log entries
    5. the AI texts' average combined score is at least 0.30 above the human
       texts' average (the first 5 of each)
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import config

DEFAULT_BASELINE = config.RESULTS_DIR / "run_2026-11-16_2148_after.md"


def parse(path):
    """{scenario name: [(results, check), ...]} — one pair per trial."""
    text = Path(path).read_text(encoding="utf-8")
    body = text.split("## What actually came back", 1)[1]
    scenarios = {}
    for section in re.split(r"^### ", body, flags=re.M)[1:]:
        name = section.splitlines()[0].strip()
        blocks = [json.loads(b) for b in re.findall(r"```json\n(.*?)\n```", section, flags=re.S)]
        scenarios[name] = list(zip(blocks[0::2], blocks[1::2]))
    return scenarios


def mean(values):
    return sum(values) / len(values)


def evaluate(path):
    s = parse(path)
    out = {"c1": [], "c2": [], "c3": [], "c4": [], "c5": [], "labels": Counter()}
    for scenario in s.values():
        for results, _ in scenario:
            out["labels"].update(r["guess"] for r in results if r.get("guess"))

    for results, _ in s["false positives"]:
        out["c1"].append(sum(1 for r in results if r.get("guess") == "ai"))      # want <= 1
    for results, check in s["bad input"]:
        ok = sum(1 for r in results if r.get("status") == 400)
        out["c2"].append(ok if check["new_rejections"] == len(results) else 0)  # want 5
    for results, _ in s["label coverage"]:
        out["c3"].append(len({r.get("guess") for r in results} & {"ai", "unsure", "human"}))  # want 3
    for results, check in s["appeal path"]:
        out["c4"].append((check["appeals_ok"], check["unknown_id_status"],
                          check["unknown_id_log_entries_added"]))                # want (5, 404, 0)
    for (ai, _), (hu, _) in zip(s["ai spread"], s["human spread"]):
        out["c5"].append(round(mean([r["confidence"] for r in ai])
                               - mean([r["confidence"] for r in hu]), 3))        # want >= 0.30
    return out


def verdicts(e):
    return {
        "1": all(v <= 1 for v in e["c1"]),
        "2": all(v == 5 for v in e["c2"]),
        "3": all(v == 3 for v in e["c3"]),
        "4": all(a == 5 and u == 404 and added == 0 for a, u, added in e["c4"]),
        "5": all(g >= 0.30 for g in e["c5"]),
    }


def cells(e):
    return {
        "1": [f"{v}/10 flagged" for v in e["c1"]],
        "2": [f"{v}/5" for v in e["c2"]],
        "3": [f"{v}/3 labels" for v in e["c3"]],
        "4": [f"{a}/5, unknown id +{added}" for a, _, added in e["c4"]],
        "5": [f"gap {g}" for g in e["c5"]],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", help="a results/run_*.md file written by run_eval.py")
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    args = parser.parse_args()

    now, before = evaluate(args.run), evaluate(args.baseline)
    v_now, v_before = verdicts(now), verdicts(before)
    c_now, c_before = cells(now), cells(before)

    names = {"1": "At most 1 of 10 human texts labeled ai", "2": "Bad input: 5 of 5 return 400, 5 rejections",
             "3": "All three labels appear", "4": "Appeals 5 of 5; unknown id adds 0 entries",
             "5": "AI average at least 0.30 above human"}
    def short(p):
        try:
            return str(Path(p).resolve().relative_to(config.ROOT))
        except ValueError:
            return str(p)

    print(f"run:      {short(args.run)}\nbaseline: {short(args.baseline)}\n")
    print("| Criterion | This run (3 trials) | Verdict | Baseline | Verdict |")
    print("|---|---|---|---|---|")
    for k in "12345":
        print(f"| {k}. {names[k]} | {', '.join(c_now[k])} | {'MET' if v_now[k] else 'MISSED'} "
              f"| {', '.join(c_before[k])} | {'MET' if v_before[k] else 'MISSED'} |")

    met_now, met_before = sum(v_now.values()), sum(v_before.values())
    print(f"\ncriteria met:       {met_now} of 5 (baseline {met_before} of 5)")
    print(f"labels:             {dict(sorted(now['labels'].items()))}"
          f"   baseline {dict(sorted(before['labels'].items()))}")
    same_verdicts = v_now == v_before
    same_labels = now["labels"] == before["labels"]
    same_numbers = c_now == c_before
    print(f"same verdicts as baseline:  {same_verdicts}")
    print(f"same labels as baseline:    {same_labels}")
    print(f"same per-trial numbers:     {same_numbers}")
    print(f"\ncapstone criterion 5 (5 of 5 still pass, labels unchanged): "
          f"{'MET' if met_now == 5 and same_labels else 'MISSED'}")
    print(f"no-regression check, reported beside it (same verdicts and labels as the "
          f"baseline): {'MET' if same_verdicts and same_labels else 'MISSED'}")
    sys.exit(0 if (same_verdicts and same_labels) else 1)


if __name__ == "__main__":
    main()

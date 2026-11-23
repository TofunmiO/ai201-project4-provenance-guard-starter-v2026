# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1.

<!-- Your criterion. It must name a number. -->

Of 10 human-written texts that I know a person wrote, at most 1 may get the high-confidence AI label. A text labeled "unsure" does not count as flagged. This has to hold on each of three separate runs of all 10 texts, so one run with 2 flagged texts is a miss, even if the other two runs are clean.

**Why this target:** On a writing site, accusing a real writer of using AI costs that person far more than missing some AI text costs the site, so I would rather let AI through than flag someone's own work. One in ten is the smallest rate I can measure with ten texts, and I want it to hold on every run because the detector can score the same text differently each time.



---

## 2.

<!-- Your criterion. -->

5 of 5 bad inputs (no `text`, empty `text`, non-string `text`, 44 words, 301 words) return status 400 with a reason, and each adds exactly 1 rejection entry to the audit log. Text of 45 to 300 words is accepted.

**Why this target:** `detector.py` reads at most 400 tokens, set by `DETECTOR_MAX_TOKENS` in `config.py`, which is about 300 words. Text past that is ignored, so I reject it. Under 45 words the scores are too noisy to judge, and the style signal in `stylometry.py` needs at least 2 sentences. Each rejection is logged with `audit.log_rejection` so a flood of bad requests shows up in the log.



---

## 3.

<!-- Your criterion. -->

Submitting real texts of 45 to 300 words through `/submit`, I get each of the 3 labels (`human`, `unsure`, `ai`) at least once, on each of 3 runs.

**Why this target:** The label ranges are set by `HUMAN_THRESHOLD` and `AI_THRESHOLD` in `config.py`. A label that no real text can reach is dead, and the reader never sees it. I expect "human" to be the hardest, because it needs a combined score of 0.35 or below.



---

## 4.

<!-- Your criterion. -->

Of 5 appeals sent with a valid `content_id`, 5 return 200 with status `under_review` and each adds exactly 1 appeal entry to the audit log, with the original decision entry still there. An appeal with an unknown `content_id` returns 404 and adds 0 entries.

**Why this target:** The appeal is the only thing a writer wrongly labeled AI can do (`/appeal` in `app.py`), so it has to work every time. `audit.log_appeal` only appends, so the original decision must stay in the log beside the appeal. A typo in the id must fail loudly with a 404 and not look like success.



---

## 5.

<!-- Your criterion. -->

The average combined score of 5 clearly-AI texts is at least 0.30 higher than the average of 5 clearly-human texts, on each of 3 runs. The AI texts are ones I generate and the human texts are ones I wrote, all 45 to 300 words.

**Why this target:** The two signals only help if they push clearly-AI and clearly-human text apart. `HUMAN_THRESHOLD` and `AI_THRESHOLD` in `config.py` are 0.30 apart, so the groups must be at least that far apart on average for the labels to mean anything.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->


---

## Capstone criteria

Five criteria for the failure-handling layer added in the capstone. Each one holds on every one of three trials.

### 1.

**3 of 3 stages** (detector, style signal, audit write) return status 503 with JSON containing `error`, `message` and `next_step`, all three non-empty, when that stage fails.

**Why this target:** The writer needs `message` to understand what happened and `next_step` to know how to fix it, and `error` is a fixed code so a program can tell failures apart without reading the wording. It has to hold for all 3 stages because they cover every place the route can fail, and a stage left out would fail silently. Before the layer, all three did, as a bare HTML 500 with no message. The response is built in `app.py::_stage_failed`.

### 2.

**2 of 2 stages** (detector, style signal) leave one new `failed` entry in `logs/audit.jsonl` when they fail, with the right `stage` and a `timestamp` later than the moment the request was sent.

**Why this target:** The log is how I understand what happened in an attack or a crash. The `stage` lets me pinpoint where it broke and patch it, and the `timestamp` lets me tell what came before the failure from what came after, so a test can see the entry is new. A failure with no entry would show up only as an absence. This covers 2 of 2 stages because the detector and the style signal are the two stages written to `audit.jsonl`. The entry is written by `audit.py::log_failure`.

### 3.

**1 of 1 stage** (the audit write) lands its entry in `logs/audit_fallback.jsonl` when `logs/audit.jsonl` cannot be written, and the response has `error` = `record_failed` and says the text was scored but not recorded.

**Why this target:** If the main log is down and nothing else records it, the failure flies under the radar undetected. The fallback file means there is no single point of failure, so I can still pinpoint what happened while the log is down. The response says the text was scored but not recorded because I want to be honest with the writer and not mislead them: a normal result would give them a `content_id` that `/appeal` cannot find, since `/appeal` reads only the main log. The fallback is written by `audit.py::_append` and the message by `app.py::_stage_failed`.

### 4.

**3 of 3 stages** fail at the same `stage` when the logged `input` is replayed under the same forced failure.

**Why this target:** What I can reproduce I can test, fix, and rule on as a real failure. Replaying the logged `input` and getting the same `stage` confirms I am fixing the right problem, because the log entry pointed at it correctly. It has to hold for all 3 stages, or one stage's failures could not be reproduced from the log. The full text is kept on `failed` entries by `app.py::_stage_failed`.

### 5.

**5 of 5** original criteria still pass and the labels are unchanged after the capstone changes, compared against `results/run_2026-11-16_2148_after.md` (18 `ai` / 9 `human` / 42 `unsure`).

**Why this target:** This is to ensure the system works as it should and there is no regression. The Nov 16 "after" run is the last known tested and graded version of the working system, so it is a good comparison. It has to be 5 of 5 because the extension is supposed to make the application better, so even one original criterion failing means it made something worse. The criteria are run by `run_eval.py`, and the comparison file is `results/run_2026-11-16_2148_after.md`.

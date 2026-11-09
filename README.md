# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

Provenance Guard takes a piece of text and says how likely it is to be AI-written, in words a non-technical reader can understand. Every submission passes through the same seven steps:

1. **`POST /submit` receives the request.** It takes `text` and `creator_id`, checks that `text` is a non-empty string, and adds a `content_id` so the submission can be found again later (the appeal needs it).
2. **The model signal (`detector.py`)** takes the text and adds `model_score`: how predictable a local language model finds it, from 0 to 1, where higher means more likely AI.
3. **The style signal (`stylometry.py`)** takes the same text and adds `style_score`: how even its sentences, vocabulary and punctuation are, from 0 to 1, where higher means more likely AI.
4. **`scoring.py::combine_signals`** takes both scores and adds `combined_score`, a single 0–1 number in the same direction.
5. **`scoring.py::score_to_label`** takes the combined score and adds the `guess` (`human`, `unsure` or `ai`) and the sentence the reader actually sees.
6. **`audit.py::log_decision`** takes everything so far and writes it to the audit log as one line, with status `decided`.
7. **The response** goes back to the writer with the `content_id`, guess, label and both signal scores. If they think the label is wrong, `POST /appeal` takes the `content_id` and their reasoning, adds an appeal entry to the log beside the original decision, and moves the status to `under_review`.

**`POST /submit`**
- **Request:** `{"text": string, "creator_id": string}`. `creator_id` defaults to `"unknown"` if missing.
- **Success (200):** `{"content_id", "guess" ("human" | "unsure" | "ai"), "confidence", "label", "model_score", "style_score"}`. Scores run from 0 to 1, higher meaning more likely AI. `confidence` is the combined score.
- **Errors:** every bad input returns 400 with `{"error": ..., "message": "..."}` and leaves one rejection entry in the log, not a decision. `error` is `bad_request` when `text` is missing, not a string, or empty; `text_too_short` under 45 words; `text_too_long` over 300 words.

**`POST /appeal`**
- **Request:** `{"content_id": string, "reasoning": string}`.
- **Success (200):** `{"content_id", "status": "under_review", "message": "..."}`.
- **Errors:** 404 if the `content_id` is not in the log; 400 if `reasoning` is missing.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the text is to a language model running locally (`detector.py::model_signal`). Low perplexity means the model could have guessed the next words. That is squashed onto 0–1 so that a high score means more likely AI.

**Why that might differ between human and AI writing:** AI text is built by picking likely next words, so a language model finds it easy to predict. Human writing surprises the model more often.

**What it can't see:** Authorship. It sees only predictability, and what it rewards is common words in short, ordinary sentences. Plenty of real people write that way, such as non-native English speakers, students and anyone writing plainly, so they score as AI. It fails the other way too: AI text that has been reworded or made deliberately odd looks unpredictable and scores as human.

### Signal two — the style signal

**What it measures:** The shape of the text, without reading it (`stylometry.py::style_signal`). It combines three measures: how much sentence length varies, how much of the vocabulary repeats (type-token ratio), and how much punctuation is used and how varied it is.

**Why that might differ between human and AI writing:** Generated prose tends toward even, mid-length sentences and a narrower band of vocabulary. Human writing is lumpier, with a three-word sentence next to a forty-word one. AI text also tends to use punctuation, such as em dashes, tidily and consistently, where human writers use less of it and miss some.

**What it can't see:** What the text says. It has no idea of meaning, so anything that changes the shape without changing the substance moves it: adding typos, breaking up sentences, or pasting in a quotation. Each measure has its own weak spot too:
- **Sentence length:** a human writing to a template or style guide produces even sentences on purpose, and a text with only a few sentences has almost no spread to measure.
- **Vocabulary:** the ratio falls as text gets longer, so a 50-word text looks varied and a 200-word one looks repetitive whatever the author. Length alone moves the score.
- **Punctuation:** it measures how carefully someone punctuates, not who they are. A careful human writer looks like AI, and a casual human writer, or AI told to write casually, looks the other way.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** Average the two signals, then subtract a share of how far apart they are. The more the signals disagree, the further the score is pulled down toward human. I chose this because a wrong accusation costs a writer more than a missed AI text costs the site, so I would rather let AI through than flag a person's own work. It is smooth on purpose: there is no gap size at which the score suddenly jumps.

**The numbers:** `combined = 0.5 × model_score + 0.5 × style_score − 0.25 × |model_score − style_score|`, kept between 0 and 1. The weights and the 0.25 penalty are in `config.py` (`WEIGHT_MODEL_SIGNAL`, `WEIGHT_STYLE_SIGNAL`, `DISAGREEMENT_PENALTY`). Inside the style signal, the three measures are weighted 0.7 sentence-length spread, 0.3 punctuation, and 0 vocabulary variety. I gave vocabulary no weight because on my three test texts it pointed the wrong way: the AI text had the most varied vocabulary.

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

My plain, ordinary writing about waiting on God (291 words, short sentences and common words) split the signals. The model signal read it as predictable, so `model_score` was 0.71, leaning AI. The style signal saw uneven sentence lengths, so `style_score` was 0.34, leaning human. A plain average gives 0.52. My rule subtracts 0.25 × 0.37 ≈ 0.09 and gives **0.43**, which is further from the 0.65 line for AI than the plain average. The cost is on the other side: AI text that fools only one of the two signals, such as AI with its sentences chopped into uneven pieces, is also pulled down.



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{"text": "So are you going to continue to give me this closed off energy anytime we talk?\nThere is no room to have a conversation about this and moving forward from this. No more hope for the friendship that barely started? You accepted my apology but it feels like there is still some resentment. I'm trying because I did value to friendship that was forming and didn't want to shut the door on that the first misunderstanding that came up. But all in all it's all good. It feels like your pointing it as being just my fault without taking accountability for anything. You left me on read for four days after I commented on a show you told me to watch? You kept asking if I was going ti show up that Tuesday and didn't talk to me at all after the dinner was done at pressrolm and didn't even ask if I had gotten home safely which is in your character to ask because you had been previously doing it. So if I held all that against you and gave the same energy your giving. How would you feel?  It’s like you already had expectations for fri ships that I was never aware of given I had just started to know you so I already didn’t even stand a chance to meet up to it given I didn’t even know what your boundaries were. Anyways I come in peace", "creator_id": "tofunmi"}
EOF
```

```json
{
  "confidence": 0.5,
  "content_id": "c_4de8630d7771",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.3742,
  "style_score": null
}
```

A second submission, with an AI-written text (`model_score` 0.8595), and its full request are in [sample_requests.md](sample_requests.md).

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 3,
  "entries": [
    {
      "combined_score": null,
      "content_id": "c_4ba86a70a5b1",
      "creator_id": "tofunmi",
      "guess": "unsure",
      "label": "not built yet",
      "model_score": 0.8595,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-09T13:57:31+00:00"
    },
    {
      "combined_score": null,
      "content_id": "c_f9a889665b31",
      "creator_id": "tofunmi",
      "guess": "unsure",
      "label": "not built yet",
      "model_score": 0.6678,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-09T13:57:31+00:00"
    },
    {
      "combined_score": null,
      "content_id": "c_4de8630d7771",
      "creator_id": "tofunmi",
      "guess": "unsure",
      "label": "not built yet",
      "model_score": 0.3742,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-09T14:02:10+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

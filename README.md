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
- **Errors:** every bad input returns 400 with `{"error": ..., "message": "..."}` and leaves one rejection entry in the log, not a decision. `error` is `bad_request` when the body isn't a JSON object, or `text` is missing, not a string, or empty; `text_too_short` under 45 words; `text_too_long` over 300 words.

**`POST /appeal`**
- **Request:** `{"content_id": string, "reasoning": string}`.
- **Success (200):** `{"content_id", "status": "under_review", "message": "..."}`.
- **Errors:** 404 if the `content_id` is not in the log; 400 if the body isn't a JSON object, or `content_id` or `reasoning` is missing. Every refused appeal leaves one rejection entry in the log (`appeal_not_found` or `appeal_bad_request`).

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
| high-confidence human | 0.00 – 0.35 | We think this was probably written by a person. |
| unsure | 0.35 – 0.70 | We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review. |
| high-confidence AI | 0.70 – 1.00 | We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why. |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

My plain and formal human test texts both landed here, so a real writer will see this label often. It says "we can't tell" instead of "this might be AI," which admits that the system doesn't know without suggesting the writer did something wrong, and the second sentence says outright that it is not a finding that anything is wrong. It points to a review, which the appeal moves into `under_review`, but it does not promise that anything will be checked again, because nothing re-scores the text automatically.



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
  "confidence": 0.1434,
  "content_id": "c_ead31d52f855",
  "guess": "human",
  "label": "We think this was probably written by a person.",
  "model_score": 0.3742,
  "style_score": 0.0664
}
```

A second submission, with an AI-written text (`model_score` 0.8595), and its full request are in [sample_requests.md](sample_requests.md).

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c_fe31d725b954", "reasoning": "I wrote this myself, in my own words, about something I have lived through."}'
```

```json
{
  "content_id": "c_fe31d725b954",
  "message": "We've received your appeal, and this is now under review.",
  "status": "under_review"
}
```

`c_fe31d725b954` is my plain writing about waiting on God, submitted just before and labeled "unsure." The log afterwards shows the original decision with the appeal added beside it, and the decision is unchanged:

```bash
$ curl "http://127.0.0.1:5000/log?limit=2"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.4203,
      "content_id": "c_fe31d725b954",
      "creator_id": "tofunmi",
      "guess": "unsure",
      "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
      "model_score": 0.6578,
      "status": "decided",
      "style_score": 0.3411,
      "timestamp": "2026-11-09T23:42:32+00:00"
    },
    {
      "content_id": "c_fe31d725b954",
      "creator_id": "tofunmi",
      "event": "appeal",
      "reasoning": "I wrote this myself, in my own words, about something I have lived through.",
      "status": "under_review",
      "timestamp": "2026-11-09T23:42:32+00:00"
    }
  ]
}
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
      "combined_score": 0.4203,
      "content_id": "c_fe31d725b954",
      "creator_id": "tofunmi",
      "guess": "unsure",
      "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
      "model_score": 0.6578,
      "status": "decided",
      "style_score": 0.3411,
      "timestamp": "2026-11-09T23:42:32+00:00"
    },
    {
      "content_id": "c_fe31d725b954",
      "creator_id": "tofunmi",
      "event": "appeal",
      "reasoning": "I wrote this myself, in my own words, about something I have lived through.",
      "status": "under_review",
      "timestamp": "2026-11-09T23:42:32+00:00"
    },
    {
      "combined_score": 0.1434,
      "content_id": "c_ead31d52f855",
      "creator_id": "tofunmi",
      "guess": "human",
      "label": "We think this was probably written by a person.",
      "model_score": 0.3742,
      "status": "decided",
      "style_score": 0.0664,
      "timestamp": "2026-11-10T03:19:32+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* A way to measure how varied a text's vocabulary is (unique words over total words) without text length distorting it, since longer texts repeat more words. I asked about using a length-corrected formula, dividing by the square root of the length.
- *What came back:* Claude built it and then tested it by cutting my three texts to 50, 100, 200 and full length. The test showed the formula did not fix the problem, it flipped it: the score now rose with length instead of falling. It also showed the measure pointing the wrong way on my texts, because my AI-written sample had a more varied vocabulary than my two human texts. Claude suggested a fixed first 45 words, and then a moving window that averages the ratio over every 45-word stretch.
- *What I changed:* I rejected the square-root formula and used the moving window in `stylometry.py::type_token_ratio`, which keeps length from mattering and still uses the whole text. Because the direction was still backwards on my texts, I gave this measure a weight of 0 in `style_signal` and trust sentence-length spread (weight 0.7) and punctuation (0.3) instead.

**Moment 2**

- *What I asked for:* A rule in `combine_signals` that matches my decision to let AI through before flagging a real writer. Claude proposed pulling the score toward the lower signal when the two disagreed by more than 0.25, and I asked whether that was the best rule we could come up with and what the balanced alternatives were.
- *What came back:* Claude admitted its own rule had a cliff, since a 0.01 change in input at the 0.25 gap moved the result by 0.07, and that it had quoted me a wrong number for one text (0.18 instead of 0.14). It then compared six other rules on my three texts, including reweighting, a geometric mean, taking the lower score, and calling split signals "unsure," and recommended a smooth penalty.
- *What I changed:* I chose the smooth penalty, `combined = average − 0.25 × |model − style|`, in `scoring.py::combine_signals` with the 0.25 in `config.py`. I kept the 50/50 weights and wrote the rule and the numbers into the combining rule section above.

**Moment 3**

- *What I asked for:* Whether to test the appeal criterion by hand or extend `run_eval.py`, since a hand test would not be recorded or reproducible.
- *What came back:* Claude recommended extending it and wrote an appeal mode that submits a text, appeals the returned `content_id`, and reads `GET /log` to record the decision and appeal counts, plus a before-and-after log count for every trial. It tested the change against a throwaway copy of the service so my real log stayed clean. It also warned me that logging refused appeals, which I had asked for earlier, would make criterion 4's "unknown id adds 0 entries" come out missed.
- *What I changed:* I told it to extend `run_eval.py`, and I kept the logging and recorded the miss with its cause, instead of editing the criterion or removing the logging.

**Moment 4**

- *What I asked for:* A diagnosis, with a stage and a mechanism, for each of the seven attacks that broke.
- *What came back:* Claude's first reading blamed my disagreement penalty for the evasions that passed. When it recomputed a plain average of the two signals for each attack, it found the equal 50/50 weights did most of the damage and the penalty decided the label only for EV01 (0.464 to 0.314). It also ran my stylometry on the attack text to confirm EV02 and EV06 had sentence-length spreads of 0.85 and 1.19, past the line my scaling treats as fully human.
- *What I changed:* I wrote the diagnoses with the plain-average column and put the cause on the weights, not the penalty alone. I kept the typos explanation for EV01 as "my reading," because Claude had not isolated it.

**Moment 5**

- *What I asked for:* One change to make from my diagnoses, with the alternatives compared.
- *What came back:* Claude replayed my recorded scores through eight candidate changes without sending anything and recommended raising `AI_THRESHOLD` to 0.70. It warned me that my own marking rule hides the cost, because AI text that slides from "ai" to "unsure" still counts as held, and that I would be tuning to the set I was measuring against.
- *What I changed:* I chose 0.70, and in the write-up I reported the evasions I stopped catching (3 of 10 down to 0), not only the two false positives I fixed.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 4 per minute, 45 per day (`RATE_LIMIT_PER_MINUTE` and `RATE_LIMIT_PER_DAY` in `config.py`, applied to `/submit`)

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

A real writer submitting their own work edits and resubmits a handful of times, not four times in a minute, so 4 a minute is more than they need and a 429 would rarely reach them. 45 a day is room for a long editing session. For a script trying to map where my thresholds sit, 45 a day from one `creator_id` means about 45 probes, so a thousand variations would take over three weeks, and each one also costs a model run on my machine. The limit is deliberately not tighter because a writer who gets blocked while revising their own work is the person I least want to hurt.

It has a hole: the limit is counted per `creator_id`, and the caller chooses the `creator_id`. A script that sends a different one on every request is never counted twice, so these limits slow down one name, not one attacker. I accepted that for now because a real fix needs accounts or per-address limits, which this service doesn't have.

**What a caller counts as:** The `creator_id` in the request body when there is one, and the caller's IP address only when it is missing or not a string (`rate_limit_key` in `app.py`). Counts are kept in memory (`memory://`), so a restart forgets them. Rejected requests count too: in my first test runs, requests my own route refused with a 400 still used up the limit.

**The run of status codes when I pushed past it:**

```bash
$ PORT=5001 python run_attacks.py --flood 15
```

```
15 submissions as 'flood_tester' against http://127.0.0.1:5001

  [ 1/15] 200
  [ 2/15] 200
  [ 3/15] 200
  [ 4/15] 200
  [ 5/15] 429
  [ 6/15] 429
  [ 7/15] 429
  [ 8/15] 429
  [ 9/15] 429
  [10/15] 429
  [11/15] 429
  [12/15] 429
  [13/15] 429
  [14/15] 429
  [15/15] 429

200 200 200 200 429 429 429 429 429 429 429 429 429 429 429

11 of 15 were rate limited.
```

I ran it on port 5001 because macOS AirPlay Receiver holds port 5000. The first runs returned 400 instead of 200, because the starter's 27-word `FLOOD_TEXT` is under my 45-word minimum, so I lengthened it to 66 words in `run_attacks.py`. `GET /log` recorded the 4 decisions and 11 rejections with reason `rate_limited` and the limit `4 per 1 minute`. The run is saved in `results/flood_2026-11-15_2157.md`.

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

I marked an attack **broke** when it got what it went for: a human's text labeled AI (false positives), AI text labeled human (evasions and injections), or a crash or untraced request (malformed and flood). Anything else is **held**. A 400 refusal counts as held. Run: `python run_attacks.py --set attack_set` on 2026-11-15, 56 attacks. The table below is taken from `results/attack_run_2026-11-15_2248.md`, which the script wrote.

**Held 49, broke 7 of 56.** evasion: 6 held, 4 broke; false_positive: 6 held, 2 broke; prompt_injection: 5 held, 1 broke; malformed: 20 held, 0 broke; flood_same_creator: 12 held, 0 broke.

| ID | Family | What it goes for | Outcome | Mark |
|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200, human (0.314) | **BROKE** |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200, human (0.149) | **BROKE** |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200, unsure (0.596) | held |
| EV04 | evasion | signal one: unusual words raise perplexity | 200, ai (0.663) | held |
| EV05 | evasion | both signals: heavy human editing pass | 200, human (0.334) | **BROKE** |
| EV06 | evasion | signal two: one very long sentence and one very short | 200, human (0.143) | **BROKE** |
| EV07 | evasion | signal two: padding with punctuation | 200, ai (0.690) | held |
| EV08 | evasion | signal one: text below the token window | 400 | held |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200, ai (0.667) | held |
| EV10 | evasion | signal two: repeated stanza structure | 200, unsure (0.600) | held |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200, unsure (0.454) | held |
| FP02 | false_positive | human writing in a formal register | 200, ai (0.674) | **BROKE** |
| FP03 | false_positive | a non-native English speaker writing carefully | 200, unsure (0.614) | held |
| FP04 | false_positive | a student essay written to a rubric | 200, unsure (0.587) | held |
| FP05 | false_positive | technical documentation written by a person | 200, ai (0.658) | **BROKE** |
| FP06 | false_positive | a person imitating a formal template | 200, unsure (0.466) | held |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200, human (0.281) | held |
| FP08 | false_positive | very short genuine human submission | 400 | held |
| PI01 | prompt_injection | instruction to ignore the check | 200, human (0.236) | **BROKE** |
| PI02 | prompt_injection | instruction disguised as a system message | 400 | held |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200, unsure (0.612) | held |
| PI04 | prompt_injection | attempt to make the label text hostile | 200, unsure (0.568) | held |
| PI05 | prompt_injection | attempt to inject into the audit log | 400 | held |
| PI06 | prompt_injection | instruction plus real human text | 200, unsure (0.450) | held |
| MF01 | malformed | text is only whitespace | 400 | held |
| MF02 | malformed | text is a single character | 400 | held |
| MF03 | malformed | text is control characters | 400 | held |
| MF04 | malformed | text is only punctuation | 400 | held |
| MF05 | malformed | text is a very long single word | 400 | held |
| MF06 | malformed | text is emoji only | 400 | held |
| MF07 | malformed | text is right-to-left script | 400 | held |
| MF08 | malformed | text is 60,000 characters | 400 | held |
| RQ01 | malformed | no text field at all | 400 | held |
| RQ02 | malformed | no creator_id | 400 | held |
| RQ03 | malformed | text is a number | 400 | held |
| RQ04 | malformed | text is a list | 400 | held |
| RQ05 | malformed | text is null | 400 | held |
| RQ06 | malformed | creator_id is an object | 400 | held |
| RQ07 | malformed | body is a JSON array, not an object | 400 | held |
| RQ08 | malformed | body is unparseable JSON | 400 | held |
| RQ09 | malformed | body is empty | 429 | held |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | held |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | held |
| RQ12 | malformed | deeply nested JSON | 400 | held |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 400 | held |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 400 | held |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 400 | held |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 400 | held |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

Which attack each entry belongs to:

1. **FP02**, a formal human writer labeled AI, both signals agreeing.
2. **FP05**, technical documentation by a person labeled AI, 0.008 over the line.
3. **FP06**, the penalty rule working: 0.881 and 0.328 pulled down to unsure.
4. **EV01**, typos: the detector was fooled to 0.164, not the style signal.
5. **EV02**, broken-up sentences: style signal fooled to 0.0, labeled human.
6. **EV05**, heavy human editing: both signals low, labeled human.
7. **PI01**, an injected instruction plus AI text, labeled human.
8. **RQ06**, a rejection where `creator_id` was an object and the log stored it as one.
9. **FL01_05**, a rejection: the flood from one `creator_id` hits the limit.
10. a rejection from my Milestone 1 flood test (`run_attacks.py --flood 15`).

```json
{"timestamp": "2026-11-16T06:48:35+00:00", "content_id": "c_9326ffaebe52", "creator_id": "attacker_FP02", "guess": "ai", "model_score": 0.7387, "style_score": 0.653, "combined_score": 0.6744, "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.", "status": "decided"}
{"timestamp": "2026-11-16T06:48:35+00:00", "content_id": "c_1ae0b6e9e7c2", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.6103, "combined_score": 0.6579, "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.", "status": "decided"}
{"timestamp": "2026-11-16T06:48:35+00:00", "content_id": "c_f9b97e6050aa", "creator_id": "attacker_FP06", "guess": "unsure", "model_score": 0.8814, "style_score": 0.3276, "combined_score": 0.4661, "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.", "status": "decided"}
{"timestamp": "2026-11-16T06:48:34+00:00", "content_id": "c_73736c7819a5", "creator_id": "attacker_EV01", "guess": "human", "model_score": 0.1635, "style_score": 0.7643, "combined_score": 0.3137, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-16T06:48:34+00:00", "content_id": "c_4582bceaf039", "creator_id": "attacker_EV02", "guess": "human", "model_score": 0.5943, "style_score": 0.0, "combined_score": 0.1486, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-16T06:48:35+00:00", "content_id": "c_d8b24a73d2a2", "creator_id": "attacker_EV05", "guess": "human", "model_score": 0.3212, "style_score": 0.3705, "combined_score": 0.3335, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-16T06:48:36+00:00", "content_id": "c_ca82d7049c2f", "creator_id": "attacker_PI01", "guess": "human", "model_score": 0.4625, "style_score": 0.1602, "combined_score": 0.2358, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-16T06:48:36+00:00", "creator_id": {"id": "x"}, "event": "rejected", "status": "rejected", "reason": "text_too_short", "word_count": 3}
{"timestamp": "2026-11-16T06:48:36+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "4 per 1 minute"}
{"timestamp": "2026-11-16T05:48:02+00:00", "creator_id": "flood_tester", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "4 per 1 minute"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

**FP02**, a real person's formal writing, labeled high-confidence AI. The detector scored it 0.7387 and the style signal 0.653, so both signals agreed it looked like a machine and my combining rule had no disagreement to subtract from. It came out at 0.6744, just over the 0.65 line, and the writer would read "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why." Their only recourse is `/appeal`, which records their reasoning and marks the item `under_review` but does not score the text again. I would have to tell them that the system called their own work machine-written because it was formal, and that nothing I built can look at it a second time.


---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing flagged as AI | ≤ 1 of 10 | 1/10 | 1/10 | 1/10 | MET (at the limit) |
| 2. Bad input returns 400 and one rejection entry | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. All three labels reachable | 3 of 3 | 3/3 | 3/3 | 3/3 | MET |
| 4. Appeal returns 200 and `under_review`; unknown id returns 404 and adds 0 entries | 5 of 5, and 0 entries | 5/5, unknown id added 1 | 5/5, unknown id added 1 | 5/5, unknown id added 1 | MISSED |
| 5. AI average at least 0.30 above human average | gap ≥ 0.30 | 0.288 | 0.288 | 0.288 | MISSED |

Run with `PORT=5001 python run_eval.py --label before`, output in `results/run_2026-11-15_2359_before.md`. I extended `run_eval.py` so it can test criterion 4 (it submits, appeals the returned `content_id`, and reads the log) and so it records how many log entries each trial added; the `appeal path` scenario is in `scenarios.py`, and all the texts are in `eval_texts.py`. "Own writing" in criterion 1 means texts I know a person wrote: 10 human-written pieces I supplied, mostly from one article series, so they are not ten independent writers.

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

Produced by `run_eval.py::main` (file `results/run_2026-11-15_2359_before.md`), which sent each request to `app.py::submit` or `app.py::appeal`; the scores come from `scoring.py::combine_signals`. This is trial 1 of 3, pasted exactly; trials 2 and 3 were identical.

**Criterion 1, ten human texts, trial 1**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5207,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.355,
    "model_score": 0.4524,
    "style_score": 0.3226,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "We need writers who are free to express the concerns of their own hear"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6445,
    "model_score": 0.6939,
    "style_score": 0.628,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5701,
    "model_score": 0.668,
    "style_score": 0.5375,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5676,
    "model_score": 0.6955,
    "style_score": 0.5249,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.1944,
    "model_score": 0.6651,
    "style_score": 0.0375,
    "label": "We think this was probably written by a person.",
    "sent": "So, will AI make the average person more intelligent? No. Definitely n"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.506,
    "model_score": 0.542,
    "style_score": 0.494,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "AI makes you feel like you have understanding on every topic, but the "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2691,
    "model_score": 0.5876,
    "style_score": 0.1629,
    "label": "We think this was probably written by a person.",
    "sent": "Having AI write for us ALL THE TIME is also an issue.\n\nIs a time comin"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6925,
    "model_score": 0.7795,
    "style_score": 0.6635,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "So I recently watched a movie called Honest Thief.\n\nThe main character"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4895,
    "model_score": 0.798,
    "style_score": 0.3866,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "The FBI don\u2019t take him seriously at first, because, after all, who wou"
  }
]
```

What the log did during that trial:

```json
{
  "log_entries_added": 10,
  "new_rejections": 0,
  "new_decisions": 10,
  "new_appeals": 0,
  "line": "unsure, unsure, unsure, unsure, unsure, human, unsure, human, ai, unsure   [10 log entries added]"
}
```

**Criterion 2, five bad inputs, trial 1**

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_bad_missing\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"text\": 12345, \"creator_id\": \"eval_bad_number\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "word word word word word word word word word word word word word word "
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "word word word word word word word word word word word word word word "
  }
]
```

What the log did during that trial:

```json
{
  "log_entries_added": 5,
  "new_rejections": 5,
  "new_decisions": 0,
  "new_appeals": 0,
  "statuses": [
    400,
    400,
    400,
    400,
    400
  ],
  "line": "statuses [400, 400, 400, 400, 400]; 5 rejection entries for 5 requests"
}
```

**Criterion 3, label coverage, trial 1**

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.909,
    "model_score": 0.9253,
    "style_score": 0.9036,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Climate change is one of the most pressing challenges facing the world"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5207,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.1944,
    "model_score": 0.6651,
    "style_score": 0.0375,
    "label": "We think this was probably written by a person.",
    "sent": "So, will AI make the average person more intelligent? No. Definitely n"
  }
]
```

What the log did during that trial:

```json
{
  "log_entries_added": 3,
  "new_rejections": 0,
  "new_decisions": 3,
  "new_appeals": 0,
  "line": "ai, unsure, human   [3 log entries added]"
}
```

**Criterion 4, appeals, trial 1**

```json
[
  {
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100",
    "submit_status": 200,
    "content_id": "c_6cd265427d32",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "We need writers who are free to express the concerns of their own hear",
    "submit_status": 200,
    "content_id": "c_83ae629263b0",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I",
    "submit_status": 200,
    "content_id": "c_484f41ee5534",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d",
    "submit_status": 200,
    "content_id": "c_eddfccebd9bb",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th",
    "submit_status": 200,
    "content_id": "c_159645838fc5",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "appeal for an id that does not exist",
    "status": 404,
    "error_code": "not_found",
    "log_entries_added": 1
  }
]
```

What the log did during that trial:

```json
{
  "log_entries_added": 11,
  "new_rejections": 1,
  "new_decisions": 5,
  "new_appeals": 5,
  "appeals_ok": 5,
  "appeals_sent": 5,
  "unknown_id_status": 404,
  "unknown_id_log_entries_added": 1,
  "line": "5/5 appeals returned 200 and under_review with the original decision still logged; unknown id -> 404, 1 log entries added"
}
```

**Criterion 5, five AI texts, trial 1**

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9025,
    "model_score": 0.9231,
    "style_score": 0.8956,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Regular exercise is one of the most effective ways to improve overall "
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7055,
    "model_score": 0.8611,
    "style_score": 0.6536,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Time management is an essential skill for professionals who want to ac"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8211,
    "model_score": 0.8092,
    "style_score": 0.8568,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Introducing the HydroSmart bottle, the perfect companion for staying h"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.909,
    "model_score": 0.9253,
    "style_score": 0.9036,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Climate change is one of the most pressing challenges facing the world"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7593,
    "model_score": 0.6884,
    "style_score": 0.9721,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Lisbon is a vibrant city that offers a perfect blend of history, cultu"
  }
]
```

What the log did during that trial:

```json
{
  "log_entries_added": 5,
  "new_rejections": 0,
  "new_decisions": 5,
  "new_appeals": 0,
  "line": "ai, ai, ai, ai, ai   [5 log entries added]"
}
```

**Criterion 5, five human texts, trial 1**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5207,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.355,
    "model_score": 0.4524,
    "style_score": 0.3226,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "We need writers who are free to express the concerns of their own hear"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6445,
    "model_score": 0.6939,
    "style_score": 0.628,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5701,
    "model_score": 0.668,
    "style_score": 0.5375,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5676,
    "model_score": 0.6955,
    "style_score": 0.5249,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th"
  }
]
```

What the log did during that trial:

```json
{
  "log_entries_added": 5,
  "new_rejections": 0,
  "new_decisions": 5,
  "new_appeals": 0,
  "line": "unsure, unsure, unsure, unsure, unsure   [5 log entries added]"
}
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

**Criterion 4, unknown-id half: missed on all three runs.** *Stage:* the route (`app.py::appeal`). *Mechanism:* I wrote the criterion in unit 7 as "an unknown `content_id` returns 404 and adds 0 entries," before I had decided to log refused requests. In unit 8, Milestone 1, I added `audit.log_rejection` to `/appeal` so that a run of bad ids leaves a trace instead of looking like a quiet afternoon. Every unknown-id appeal now adds one `appeal_not_found` entry, which contradicts "adds 0 entries" each time. The 404 and the five valid appeals are unaffected. I kept the logging and left the target as written, because a trace of refused requests matters more to me than an empty log, and a target I missed stays where it is.

**Criterion 5: missed by 0.012, identically on all three runs (gap 0.288 against 0.30).** *Stage:* signal one, with the combining rule unable to correct it. *Mechanism:* the five human texts (H01 to H05) are plain opinion writing in short sentences. Signal one reads common words in short sentences as predictable, and four of the five scored 0.67 to 0.70 on `model_score`. Signal two also leaned toward AI on three of them (0.52 to 0.63), so the signals agreed. My combining rule only subtracts when the two signals disagree, and here it took off about 0.04 per text, so the human average stayed at 0.532 against 0.819 for the AI texts. This is the same weakness the false-positive attacks found (FP02 and FP05): plain or formal human writing looks machine-like to both signals at once.

**Criterion 1: met, but only just.** One human text, H09 (a movie review), was labeled AI on every run, with `model_score` 0.7795, `style_score` 0.6635 and a combined 0.6925, which is 0.04 over the 0.65 line. The target allows one, so it passes, but a second text crossing the line would fail it.


**The seven attacks that broke.** For each: the stage, then the mechanism. The "plain average" is what the two signals would have given without my disagreement penalty, so it shows whether the signals or my rule did the damage.

- **FP02, a human writer's formal prose, labeled AI (0.674).** *Stage:* signal one and signal two together. *Mechanism:* the detector scored it 0.739 and the style signal 0.653, so both read formal writing as machine-like. The plain average is 0.696, still AI, so my combining rule is not the cause: it only subtracts when the signals disagree, and these agreed.
- **FP05, a person's technical documentation, labeled AI (0.658).** *Stage:* signal one and signal two together. *Mechanism:* the same as FP02, with 0.800 from the detector and 0.610 from the style signal, and a plain average of 0.705. It is only 0.008 over the line, so it is a fragile break.
- **EV01, typos added to AI text, labeled human (0.314).** *Stage:* signal one, then the combining rule. *Mechanism:* the attack was aimed at signal two, but the number that collapsed was the detector's, down to 0.164, while the style signal stayed at 0.764 and still read it as AI. My reading is that misspelled words are unlikely under the language model, which raises perplexity, so signal one took typos for human unpredictability. I did not isolate that. This is the one case where my rule decided the label: the plain average was 0.464 (unsure), and subtracting the penalty for a 0.60 gap pulled it to 0.314.
- **EV02, AI text with its sentences broken up, labeled human (0.149).** *Stage:* signal two. *Mechanism:* chopping sentences into uneven pieces pushes sentence-length spread past the point my scaling treats as clearly human, so the style signal went to 0.000, while the detector still said 0.594. Spread is 70% of the style signal, so one cheap edit zeroed it. The plain average was 0.297, already human.
- **EV06, one very long and one very short sentence, labeled human (0.143).** *Stage:* signal two. *Mechanism:* the same as EV02: style 0.000, detector 0.573, plain average 0.287.
- **EV05, a heavy human editing pass over AI text, labeled human (0.334).** *Stage:* signal one and signal two together. *Mechanism:* both signals fell, to 0.321 and 0.370, so the edit changed both the word choice and the sentence shape. A plain average gives 0.346, also human. No part of my rule could have caught it, because there is nothing for the signals to disagree about.
- **PI01, an injected "ignore previous instructions" line plus AI text, labeled human (0.236).** *Stage:* signal one and signal two. *Mechanism:* the instruction itself did nothing, because the service never reads for meaning. The three short sentences it added changed the measurements: style fell to 0.160 and the detector to 0.463. The plain average was 0.312, already human.

**The pattern.** Seven breaks come down to two problems, not seven.

1. **My two signals share a blind spot on plain and formal human writing.** FP02, FP05, the criterion 5 gap and the H09 near miss in criterion 1 are all the same failure. Signal one rewards common words in short sentences and signal two rewards even sentences, and plain or formal prose has both, so the signals agree, and my disagreement rule has nothing to act on.
2. **A single fooled signal is enough to pass AI text.** In EV01, EV02, EV06 and PI01, one signal was pushed low and the equal 50/50 weights dragged the average under 0.35 or close to it. My penalty decided the label only for EV01. This is the price of my choice to let AI through before flagging a writer, and the cheapest edit that triggers it is breaking up sentences, because spread carries 70% of the style signal.

The criterion 5 miss and the criterion 4 miss have different causes. Criterion 5 belongs to the first pattern, and criterion 4 is a conflict between a unit 7 target and a unit 8 decision, not a signal failure.

---

## The Improvement

**What I changed:** one value, `AI_THRESHOLD` in `config.py`, from 0.65 to 0.70. Everything else is the same: both signals, the 50/50 weights, the disagreement penalty and the label texts. I also changed the two score ranges in the Label Variants table to match (unsure is now 0.35 to 0.70, high-confidence AI is 0.70 to 1.00).

**Which diagnosis pointed at it:** the first pattern in my diagnoses. FP02 and FP05, two real writers' formal and technical prose, were labeled AI because both of my signals read plain and formal writing as machine-like, so they agreed and my disagreement penalty had nothing to act on. No reweighting fixes two signals that are wrong in the same direction. What did separate them from the AI texts was the line itself: FP02 scored 0.674, FP05 0.658 and my criterion 1 near miss H09 0.693, all just over 0.65. That is the worst outcome I named, and moving the threshold is the one change that reaches it. I picked 0.70 after replaying my recorded scores through eight candidate changes without sending anything, and the replay predicted the five rows that moved.

### Attack Run — After

Run: `python run_attacks.py --set attack_set --label after` on 2026-11-16, after restarting the service with the new threshold. The table is taken from `results/attack_run_2026-11-16_2147_after.md`. Same 56 attacks and the same marking rule as before. "was ai" means the label changed from the before run.

**Held 51, broke 5 of 56.** evasion: 6 held, 4 broke; false_positive: 8 held, 0 broke; prompt_injection: 5 held, 1 broke; malformed: 20 held, 0 broke; flood_same_creator: 12 held, 0 broke.

| ID | Family | What it goes for | Outcome | Mark |
|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200, human (0.314) | **BROKE** |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200, human (0.149) | **BROKE** |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200, unsure (0.596) | held |
| EV04 | evasion | signal one: unusual words raise perplexity | 200, unsure (0.663), was ai | held |
| EV05 | evasion | both signals: heavy human editing pass | 200, human (0.334) | **BROKE** |
| EV06 | evasion | signal two: one very long sentence and one very short | 200, human (0.143) | **BROKE** |
| EV07 | evasion | signal two: padding with punctuation | 200, unsure (0.690), was ai | held |
| EV08 | evasion | signal one: text below the token window | 400 | held |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200, unsure (0.667), was ai | held |
| EV10 | evasion | signal two: repeated stanza structure | 200, unsure (0.600) | held |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200, unsure (0.454) | held |
| FP02 | false_positive | human writing in a formal register | 200, unsure (0.674), was ai | held (was **BROKE**) |
| FP03 | false_positive | a non-native English speaker writing carefully | 200, unsure (0.614) | held |
| FP04 | false_positive | a student essay written to a rubric | 200, unsure (0.587) | held |
| FP05 | false_positive | technical documentation written by a person | 200, unsure (0.658), was ai | held (was **BROKE**) |
| FP06 | false_positive | a person imitating a formal template | 200, unsure (0.466) | held |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200, human (0.281) | held |
| FP08 | false_positive | very short genuine human submission | 400 | held |
| PI01 | prompt_injection | instruction to ignore the check | 200, human (0.236) | **BROKE** |
| PI02 | prompt_injection | instruction disguised as a system message | 400 | held |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200, unsure (0.612) | held |
| PI04 | prompt_injection | attempt to make the label text hostile | 200, unsure (0.568) | held |
| PI05 | prompt_injection | attempt to inject into the audit log | 400 | held |
| PI06 | prompt_injection | instruction plus real human text | 200, unsure (0.450) | held |
| MF01 | malformed | text is only whitespace | 400 | held |
| MF02 | malformed | text is a single character | 400 | held |
| MF03 | malformed | text is control characters | 400 | held |
| MF04 | malformed | text is only punctuation | 400 | held |
| MF05 | malformed | text is a very long single word | 400 | held |
| MF06 | malformed | text is emoji only | 400 | held |
| MF07 | malformed | text is right-to-left script | 400 | held |
| MF08 | malformed | text is 60,000 characters | 400 | held |
| RQ01 | malformed | no text field at all | 400 | held |
| RQ02 | malformed | no creator_id | 400 | held |
| RQ03 | malformed | text is a number | 400 | held |
| RQ04 | malformed | text is a list | 400 | held |
| RQ05 | malformed | text is null | 400 | held |
| RQ06 | malformed | creator_id is an object | 400 | held |
| RQ07 | malformed | body is a JSON array, not an object | 400 | held |
| RQ08 | malformed | body is unparseable JSON | 400 | held |
| RQ09 | malformed | body is empty | 429 | held |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | held |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | held |
| RQ12 | malformed | deeply nested JSON | 400 | held |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 400 | held |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 400 | held |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 400 | held |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 400 | held |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | held |

The scores did not change, only the labels: 51 of the 56 rows are identical to the before run and exactly five moved, FP02, FP05, EV04, EV07 and EV09.

**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

**Before and after, side by side**

| | Before (threshold 0.65) | After (threshold 0.70) |
|---|---|---|
| Attacks that broke | 7 of 56 | **5 of 56** |
| False positives that broke (a human labeled AI) | 2 (FP02, FP05) | **0** |
| Evasions that broke (AI labeled human) | 4 | 4 |
| Prompt injections that broke | 1 | 1 |
| Evasions still caught as high-confidence AI | 3 of 10 | **0 of 10** |

| Criterion (3 trials each) | Target | Before | After | Verdict after |
|---|---|---|---|---|
| 1. My human texts flagged as AI | ≤ 1 of 10 | 1/10, 1/10, 1/10 | **0/10, 0/10, 0/10** | MET |
| 2. Bad input returns 400 and one rejection entry | 5 of 5 | 5/5 ×3 | 5/5 ×3 | MET |
| 3. All three labels reachable | 3 of 3 | 3/3 ×3 | 3/3 ×3 | MET |
| 4. Appeal returns 200 and `under_review`; unknown id adds 0 entries | 5 of 5, and 0 | 5/5, unknown id +1, ×3 | 5/5, unknown id +1, ×3 | MISSED |
| 5. AI average at least 0.30 above human average | gap ≥ 0.30 | 0.288 ×3 | 0.288 ×3 | MISSED |

The criteria run is `results/run_2026-11-16_2148_after.md`, in the same format as before, and all three trials were identical again.

**It helped with what it was aimed at.** Both false positives, FP02 and FP05, now read as "unsure," so no real writer in the attack set is told their work is machine-written. Criterion 1 went from one human text flagged (H09, the movie review) to none, on every trial. The five rows that moved are the five my replay predicted.

**It did not help with the rest.** The four evasions that got through still get through, because they score under 0.35 and the threshold I moved is the other one. Criterion 5 is unchanged at 0.288, since it compares averages and the threshold does not change a single score. Criterion 4's miss is a different problem entirely.

**What it cost.** Moving the line up lets AI text through. EV04, EV07 and EV09 were my three evasions that were still caught as high-confidence AI, at 0.663, 0.690 and 0.667, and all three now read as "unsure." My marking rule counts "unsure" as held, so they still show as held in the table, which hides a real loss: before, I caught three of ten evasions, and now I catch none. The five AI texts in my criteria set are all still labeled AI, but A02 sits at 0.706, only 0.006 over the new line, so a slightly better-disguised AI text would slip under it too. This is the trade I chose: a writer who is told "we can't tell" instead of "AI" pays less than an AI text that gets through, and the people who pay for it are the readers and the site that trusted the label.

**How much I trust it.** The deterministic detector gave identical scores before and after, so the only thing that changed between the two runs is the threshold, which makes this a clean comparison. But I picked 0.70 after looking at these same attacks and texts, and it is the lowest round number above the three that mattered, so it is tuned to this set. FP02 is only 0.026 under the new line. On unseen human writing I would expect some formal prose to still cross it. I also did not edit `criteria.md`: criterion 5's reason says the thresholds are 0.30 apart, and they are now 0.35 apart, but the target is still 0.30 and I left the original line as written.

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

**An appeal changes nothing about the decision.** `POST /appeal` records the writer's reasoning, adds an appeal entry to the log beside the original decision, and marks the item `under_review`. It does not re-score the text: the signals are never called again, and the appeal doesn't even carry the text. Nothing reads the `under_review` status afterwards, so a person has to read `GET /log`, find the appeals, and decide. Re-running the same signals would give the same score, so a real re-check needs different information, such as a human reviewer or the writer's drafts. I stopped here because the brief asks only for the status change and the log entry, and a writer wrongly labeled AI still has a way to put their side on record.

**EV02, EV06 and PI01: cheap edits to sentence shape still pass AI text as human.** These are one problem, in signal two. Breaking a text into uneven pieces, or adding a few short sentences, zeroes or lowers the style signal, and the equal 50/50 weights then pull the average under 0.35. What I'd do is make sentence-length spread harder to game, for example by measuring it only over sentences above a minimum length, so chopping or one-word sentences stop counting. The obvious quick fix, requiring both signals to be low before a text is called human, I replayed on my recorded scores and it does not work: of the 17 real human texts I have scores for, only 3 are labeled human today, and under that rule none would be, because the detector scores real human writing high (those three have detector scores of 0.59, 0.67 and 0.88 and get there on the style signal). It would also still let 1 of the 4 evasions through. I stopped because the brief asks for one change measured properly, I spent it on the false accusations, and the spread fix would need its own before and after.

**EV01: typos still read as human.** This is signal one. I'd score the detector on a copy of the text with obvious misspellings corrected, so typos stop looking like unpredictability. I have not confirmed that is the mechanism, so the first step would be to score the same text with and without its typos. I stopped because that is an untested guess and one change was the limit.

**EV05: a heavy human editing pass still passes.** Both signals fell, because the text really was rewritten. I do not think two statistics about word choice and sentence shape can fix this. It needs different evidence, such as the writer's drafts or edit history, and past some point a heavily edited AI text is hard to tell from human writing. I stopped because there is no small change to these two signals that addresses it.

**Criterion 5 is still missed (gap 0.288 against 0.30).** What I'd do is add a signal that separates plain human prose from AI prose, because both of mine agree on both. In my replay, weighting the style signal at 0.65 would reach 0.312, but that passes by 0.012, it was found by tuning to this set, and it leans on the signal that EV02 and EV06 show is cheapest to fool, so it would not be a real fix. I stopped because my one change went to false accusations, which I think is the worse failure, and I left this miss as it is.

**Criterion 4 is still missed (an unknown id adds one log entry, not zero).** I would not change the code. I wrote the target in unit 7, before I decided to log refused requests, and I would rather have a trace of a refused appeal than an empty log. The two decisions conflict, and I stopped here on purpose.

**Also still true, and not from the attack set.** The rate limit counts per `creator_id` and the caller picks it, so a script that changes it on every request is never limited; I would also count by address. Four early log entries from before the second signal have empty `style_score` and `combined_score`, which I left as honest history. The log does not store the text or the weights and thresholds in force, and I moved `AI_THRESHOLD` from 0.65 to 0.70 during this unit, so an older entry labeled AI with a score between 0.65 and 0.70 was correct under the old line and would read as unsure now.

**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

I would keep the AI line high and let AI text through before I accuse a writer, because a wrong "AI" label lands on a person's own work and their only recourse is an appeal that nothing re-scores. The people who pay for that are the readers and the site, who trust a label that now misses more AI text (my threshold change alone cost me all three evasions I used to catch), and I accept that because a missed AI text costs them a little while a false accusation costs a writer a lot.

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

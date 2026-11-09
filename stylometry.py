"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics
import unicodedata

import config


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies. ← TODO

    Returns:
        A float: the standard deviation of sentence lengths divided by their
        mean. Higher means MORE human (lumpier sentences); 0.0 means every
        sentence is the same length, or there are fewer than two sentences to
        compare. `style_signal` flips it so that higher means more AI.

    A hint on what you're reaching for: the standard deviation of sentence
    lengths, probably divided by the mean so a long text and a short one are
    comparable. `statistics.stdev` is imported for you.

    Watch the edge case: a one-sentence submission has no spread at all, and
    `stdev` raises on fewer than two values. Decide what that should return
    before the attack set decides for you.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]

    # One sentence has no spread to measure; stdev would raise.
    if len(lengths) < 2:
        return 0.0

    return round(statistics.stdev(lengths) / statistics.mean(lengths), 4)


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words. ← TODO

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary (more
        human). It is the average unique/total ratio over every
        `config.MIN_WORDS` (45) word stretch of the text, sliding one word at a
        time (a moving-average type-token ratio).

    Worth knowing before you rely on it: a plain ratio falls as text gets
    longer, because common words repeat. Every window here is the same size, so
    a 60-word text and a 290-word text are measured on the same footing, and
    unlike cutting off after 45 words it still uses the whole text. A text
    shorter than one window is measured as a single window.
    """
    tokens = words(text)
    if not tokens:
        return 0.0

    size = min(config.MIN_WORDS, len(tokens))
    ratios = [
        len(set(tokens[i:i + size])) / size
        for i in range(len(tokens) - size + 1)
    ]
    return round(sum(ratios) / len(ratios), 4)


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to length. ← TODO

    Returns:
        A float: punctuation marks per sentence. Every kind counts — commas,
        full stops, semicolons, dashes, quotes, apostrophes — anything Unicode
        files under punctuation. Higher means more punctuation; the hypothesis
        is that AI text is tidier and uses more of it, so higher points toward
        AI. `style_signal` rescales it.

    Per sentence, not per word, so a text of short sentences and one of long
    sentences are compared on how heavily each sentence is marked up. Note
    every sentence ends in at least one mark, so the floor is about 1.0.
    """
    sents = sentences(text)
    if not sents:
        return 0.0
    marks = sum(1 for ch in text if unicodedata.category(ch).startswith("P"))
    return round(marks / len(sents), 4)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.** ← TODO

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Which direction each measure points. Low spread means more AI-ish, so
         it needs flipping. Work out which of your three need that.
      2. How to get each onto a comparable scale. A raw type-token ratio sits
         between 0 and 1; a raw punctuation count doesn't. Adding them
         unscaled means whichever has the bigger numbers wins by default.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.
    """
    spread = _scale(sentence_length_spread(text), config.SPREAD_HUMAN, config.SPREAD_AI)
    punctuation = _scale(punctuation_density(text), config.PUNCTUATION_HUMAN, config.PUNCTUATION_AI)
    vocabulary = _scale(type_token_ratio(text), config.VOCABULARY_HUMAN, config.VOCABULARY_AI)

    score = (
        config.STYLE_WEIGHT_SPREAD * spread
        + config.STYLE_WEIGHT_PUNCTUATION * punctuation
        + config.STYLE_WEIGHT_VOCABULARY * vocabulary
    )
    return round(score, 4)


def _scale(value: float, human_end: float, ai_end: float) -> float:
    """
    Stretch a raw measure onto 0–1, where 0 is the value that reads as clearly
    human and 1 the value that reads as clearly AI. Works whichever way round
    the two ends are, so a measure that runs backwards (low spread = AI) just
    has its ends swapped. Anything beyond an end is clipped to it.
    """
    return min(max(0.0, (value - human_end) / (ai_end - human_end)), 1.0)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")

# Run log — capstone_improved

- Produced by: `run_eval.py::main`
- Service: `app.py::submit` · scoring: `scoring.py::combine_signals`
- 3 trials per criterion · 2026-11-23 01:01

Fill in Target from `criteria.md`, and Run and Verdict from the output
underneath. Whether a trial passed depends on the criterion you wrote.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. false positives |  |   |   |   |  |
| 2. bad input |  |   |   |   |  |
| 3. label coverage |  |   |   |   |  |
| 4. appeal path |  |   |   |   |  |
| 5. ai spread |  |   |   |   |  |
| 5. human spread |  |   |   |   |  |

---

## What actually came back

Real output. Paste the relevant parts into your README — the rubric
asks for the actual JSON, not a description of it.

### false positives

**Trial 1**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4984,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3421,
    "model_score": 0.4524,
    "style_score": 0.3226,
    "label": "We think this was probably written by a person.",
    "sent": "We need writers who are free to express the concerns of their own hear"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6379,
    "model_score": 0.6939,
    "style_score": 0.628,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5571,
    "model_score": 0.668,
    "style_score": 0.5375,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5505,
    "model_score": 0.6955,
    "style_score": 0.5249,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.1316,
    "model_score": 0.6651,
    "style_score": 0.0375,
    "label": "We think this was probably written by a person.",
    "sent": "So, will AI make the average person more intelligent? No. Definitely n"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5012,
    "model_score": 0.542,
    "style_score": 0.494,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "AI makes you feel like you have understanding on every topic, but the "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2266,
    "model_score": 0.5876,
    "style_score": 0.1629,
    "label": "We think this was probably written by a person.",
    "sent": "Having AI write for us ALL THE TIME is also an issue.\n\nIs a time comin"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6809,
    "model_score": 0.7795,
    "style_score": 0.6635,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "So I recently watched a movie called Honest Thief.\n\nThe main character"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4483,
    "model_score": 0.798,
    "style_score": 0.3866,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "The FBI don\u2019t take him seriously at first, because, after all, who wou"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 10,
  "new_rejections": 0,
  "new_decisions": 10,
  "new_appeals": 0,
  "line": "unsure, human, unsure, unsure, unsure, human, unsure, human, unsure, unsure   [10 log entries added]"
}
```

**Trial 2**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4984,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3421,
    "model_score": 0.4524,
    "style_score": 0.3226,
    "label": "We think this was probably written by a person.",
    "sent": "We need writers who are free to express the concerns of their own hear"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6379,
    "model_score": 0.6939,
    "style_score": 0.628,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5571,
    "model_score": 0.668,
    "style_score": 0.5375,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5505,
    "model_score": 0.6955,
    "style_score": 0.5249,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.1316,
    "model_score": 0.6651,
    "style_score": 0.0375,
    "label": "We think this was probably written by a person.",
    "sent": "So, will AI make the average person more intelligent? No. Definitely n"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5012,
    "model_score": 0.542,
    "style_score": 0.494,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "AI makes you feel like you have understanding on every topic, but the "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2266,
    "model_score": 0.5876,
    "style_score": 0.1629,
    "label": "We think this was probably written by a person.",
    "sent": "Having AI write for us ALL THE TIME is also an issue.\n\nIs a time comin"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6809,
    "model_score": 0.7795,
    "style_score": 0.6635,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "So I recently watched a movie called Honest Thief.\n\nThe main character"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4483,
    "model_score": 0.798,
    "style_score": 0.3866,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "The FBI don\u2019t take him seriously at first, because, after all, who wou"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 10,
  "new_rejections": 0,
  "new_decisions": 10,
  "new_appeals": 0,
  "line": "unsure, human, unsure, unsure, unsure, human, unsure, human, unsure, unsure   [10 log entries added]"
}
```

**Trial 3**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4984,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3421,
    "model_score": 0.4524,
    "style_score": 0.3226,
    "label": "We think this was probably written by a person.",
    "sent": "We need writers who are free to express the concerns of their own hear"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6379,
    "model_score": 0.6939,
    "style_score": 0.628,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5571,
    "model_score": 0.668,
    "style_score": 0.5375,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5505,
    "model_score": 0.6955,
    "style_score": 0.5249,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.1316,
    "model_score": 0.6651,
    "style_score": 0.0375,
    "label": "We think this was probably written by a person.",
    "sent": "So, will AI make the average person more intelligent? No. Definitely n"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5012,
    "model_score": 0.542,
    "style_score": 0.494,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "AI makes you feel like you have understanding on every topic, but the "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2266,
    "model_score": 0.5876,
    "style_score": 0.1629,
    "label": "We think this was probably written by a person.",
    "sent": "Having AI write for us ALL THE TIME is also an issue.\n\nIs a time comin"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6809,
    "model_score": 0.7795,
    "style_score": 0.6635,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "So I recently watched a movie called Honest Thief.\n\nThe main character"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4483,
    "model_score": 0.798,
    "style_score": 0.3866,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "The FBI don\u2019t take him seriously at first, because, after all, who wou"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 10,
  "new_rejections": 0,
  "new_decisions": 10,
  "new_appeals": 0,
  "line": "unsure, human, unsure, unsure, unsure, human, unsure, human, unsure, unsure   [10 log entries added]"
}
```

### bad input

**Trial 1**

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

What the log did during this trial:

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

**Trial 2**

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

What the log did during this trial:

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

**Trial 3**

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

What the log did during this trial:

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

### label coverage

**Trial 1**

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9069,
    "model_score": 0.9253,
    "style_score": 0.9036,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Climate change is one of the most pressing challenges facing the world"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4984,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.1316,
    "model_score": 0.6651,
    "style_score": 0.0375,
    "label": "We think this was probably written by a person.",
    "sent": "So, will AI make the average person more intelligent? No. Definitely n"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 3,
  "new_rejections": 0,
  "new_decisions": 3,
  "new_appeals": 0,
  "line": "ai, unsure, human   [3 log entries added]"
}
```

**Trial 2**

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9069,
    "model_score": 0.9253,
    "style_score": 0.9036,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Climate change is one of the most pressing challenges facing the world"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4984,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.1316,
    "model_score": 0.6651,
    "style_score": 0.0375,
    "label": "We think this was probably written by a person.",
    "sent": "So, will AI make the average person more intelligent? No. Definitely n"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 3,
  "new_rejections": 0,
  "new_decisions": 3,
  "new_appeals": 0,
  "line": "ai, unsure, human   [3 log entries added]"
}
```

**Trial 3**

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9069,
    "model_score": 0.9253,
    "style_score": 0.9036,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Climate change is one of the most pressing challenges facing the world"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4984,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.1316,
    "model_score": 0.6651,
    "style_score": 0.0375,
    "label": "We think this was probably written by a person.",
    "sent": "So, will AI make the average person more intelligent? No. Definitely n"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 3,
  "new_rejections": 0,
  "new_decisions": 3,
  "new_appeals": 0,
  "line": "ai, unsure, human   [3 log entries added]"
}
```

### appeal path

**Trial 1**

```json
[
  {
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100",
    "submit_status": 200,
    "content_id": "c_56769699f355",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "We need writers who are free to express the concerns of their own hear",
    "submit_status": 200,
    "content_id": "c_7dc4243b7b0e",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I",
    "submit_status": 200,
    "content_id": "c_72c7bd67b695",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d",
    "submit_status": 200,
    "content_id": "c_1f509b5eb4b5",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th",
    "submit_status": 200,
    "content_id": "c_3d05f23d18f8",
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

What the log did during this trial:

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

**Trial 2**

```json
[
  {
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100",
    "submit_status": 200,
    "content_id": "c_b907842b5f1d",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "We need writers who are free to express the concerns of their own hear",
    "submit_status": 200,
    "content_id": "c_9fd03806390e",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I",
    "submit_status": 200,
    "content_id": "c_0b7667bace23",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d",
    "submit_status": 200,
    "content_id": "c_bef958082548",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th",
    "submit_status": 200,
    "content_id": "c_17d2b0701d81",
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

What the log did during this trial:

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

**Trial 3**

```json
[
  {
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100",
    "submit_status": 200,
    "content_id": "c_b3095ba7485c",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "We need writers who are free to express the concerns of their own hear",
    "submit_status": 200,
    "content_id": "c_be67f050d74d",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I",
    "submit_status": 200,
    "content_id": "c_454e84186c1e",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d",
    "submit_status": 200,
    "content_id": "c_ff45b9d17382",
    "status": 200,
    "appeal_status": "under_review",
    "log_decisions": 1,
    "log_appeals": 1,
    "log_appeal_status": "under_review"
  },
  {
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th",
    "submit_status": 200,
    "content_id": "c_6b583c56bfe7",
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

What the log did during this trial:

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

### ai spread

**Trial 1**

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8997,
    "model_score": 0.9231,
    "style_score": 0.8956,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Regular exercise is one of the most effective ways to improve overall "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6847,
    "model_score": 0.8611,
    "style_score": 0.6536,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Time management is an essential skill for professionals who want to ac"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8259,
    "model_score": 0.8092,
    "style_score": 0.8568,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Introducing the HydroSmart bottle, the perfect companion for staying h"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9069,
    "model_score": 0.9253,
    "style_score": 0.9036,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Climate change is one of the most pressing challenges facing the world"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7877,
    "model_score": 0.6884,
    "style_score": 0.9721,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Lisbon is a vibrant city that offers a perfect blend of history, cultu"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 5,
  "new_rejections": 0,
  "new_decisions": 5,
  "new_appeals": 0,
  "line": "ai, unsure, ai, ai, ai   [5 log entries added]"
}
```

**Trial 2**

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8997,
    "model_score": 0.9231,
    "style_score": 0.8956,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Regular exercise is one of the most effective ways to improve overall "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6847,
    "model_score": 0.8611,
    "style_score": 0.6536,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Time management is an essential skill for professionals who want to ac"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8259,
    "model_score": 0.8092,
    "style_score": 0.8568,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Introducing the HydroSmart bottle, the perfect companion for staying h"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9069,
    "model_score": 0.9253,
    "style_score": 0.9036,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Climate change is one of the most pressing challenges facing the world"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7877,
    "model_score": 0.6884,
    "style_score": 0.9721,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Lisbon is a vibrant city that offers a perfect blend of history, cultu"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 5,
  "new_rejections": 0,
  "new_decisions": 5,
  "new_appeals": 0,
  "line": "ai, unsure, ai, ai, ai   [5 log entries added]"
}
```

**Trial 3**

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8997,
    "model_score": 0.9231,
    "style_score": 0.8956,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Regular exercise is one of the most effective ways to improve overall "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6847,
    "model_score": 0.8611,
    "style_score": 0.6536,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Time management is an essential skill for professionals who want to ac"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8259,
    "model_score": 0.8092,
    "style_score": 0.8568,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Introducing the HydroSmart bottle, the perfect companion for staying h"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9069,
    "model_score": 0.9253,
    "style_score": 0.9036,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Climate change is one of the most pressing challenges facing the world"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7877,
    "model_score": 0.6884,
    "style_score": 0.9721,
    "label": "We think this was probably written with the help of AI. We can be wrong, so if you wrote it yourself, you can appeal and tell us why.",
    "sent": "Lisbon is a vibrant city that offers a perfect blend of history, cultu"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 5,
  "new_rejections": 0,
  "new_decisions": 5,
  "new_appeals": 0,
  "line": "ai, unsure, ai, ai, ai   [5 log entries added]"
}
```

### human spread

**Trial 1**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4984,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3421,
    "model_score": 0.4524,
    "style_score": 0.3226,
    "label": "We think this was probably written by a person.",
    "sent": "We need writers who are free to express the concerns of their own hear"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6379,
    "model_score": 0.6939,
    "style_score": 0.628,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5571,
    "model_score": 0.668,
    "style_score": 0.5375,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5505,
    "model_score": 0.6955,
    "style_score": 0.5249,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 5,
  "new_rejections": 0,
  "new_decisions": 5,
  "new_appeals": 0,
  "line": "unsure, human, unsure, unsure, unsure   [5 log entries added]"
}
```

**Trial 2**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4984,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3421,
    "model_score": 0.4524,
    "style_score": 0.3226,
    "label": "We think this was probably written by a person.",
    "sent": "We need writers who are free to express the concerns of their own hear"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6379,
    "model_score": 0.6939,
    "style_score": 0.628,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5571,
    "model_score": 0.668,
    "style_score": 0.5375,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5505,
    "model_score": 0.6955,
    "style_score": 0.5249,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 5,
  "new_rejections": 0,
  "new_decisions": 5,
  "new_appeals": 0,
  "line": "unsure, human, unsure, unsure, unsure   [5 log entries added]"
}
```

**Trial 3**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4984,
    "model_score": 0.6879,
    "style_score": 0.465,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "\u2019ve decided to add this statement at the top of all my writings.\n\n\u201c100"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3421,
    "model_score": 0.4524,
    "style_score": 0.3226,
    "label": "We think this was probably written by a person.",
    "sent": "We need writers who are free to express the concerns of their own hear"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6379,
    "model_score": 0.6939,
    "style_score": 0.628,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "When I read, I don\u2019t care how long it took the writer to produce it. I"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5571,
    "model_score": 0.668,
    "style_score": 0.5375,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "Though this is a few years old. I think it\u2019s safe to say that people d"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5505,
    "model_score": 0.6955,
    "style_score": 0.5249,
    "label": "We can't tell whether this was written by a person or by AI. That isn't a finding that anything is wrong. If you wrote it yourself, you can ask for a review.",
    "sent": "I\u2019ve had this brewing for a while, but haven\u2019t been able to pull my th"
  }
]
```

What the log did during this trial:

```json
{
  "log_entries_added": 5,
  "new_rejections": 0,
  "new_decisions": 5,
  "new_appeals": 0,
  "line": "unsure, human, unsure, unsure, unsure   [5 log entries added]"
}
```

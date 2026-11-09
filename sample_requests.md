# Sample requests

The full texts behind the Sample Run in the README, so the README can stay short. Each one was sent to the running service at `POST /submit` (45 to 300 words), and the response under it is the real response, with both signal scores. Every `content_id` below is in `logs/audit.jsonl` and shows up in `GET /log`.

How each request was sent (the JSON body is built from the text file so line breaks and apostrophes survive):

```bash
python -c 'import json,sys; print(json.dumps({"text": open(sys.argv[1]).read().strip(), "creator_id": "tofunmi"}))' text.txt \
  | curl -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d @-
```

| # | Input | Words | Detector | Style | Combined | `content_id` |
|---|---|---|---|---|---|---|
| 1 | Clearly AI | 289 | 0.8595 | 0.8116 | 0.8236 | `c_8470f2287473` |
| 2 | Clearly human (casual) | 240 | 0.3742 | 0.0664 | 0.1434 | `c_876b56703f88` |
| 3 | Plain human | 289 | 0.6578 | 0.3411 | 0.4203 | `c_e0d743bb21e7` |
| 4 | Formal human | 299 | 0.6552 | 0.3119 | 0.3977 | `c_9198eebbd319` |
| 5 | Lightly-edited AI | 154 | 0.8113 | 0.6665 | 0.7027 | `c_4cf3a794abe6` |

---

## 1. Clearly AI (289 words, an essay on remote work, written by Claude)

```text
Remote work has changed the way many people think about their careers and their daily lives. In recent years, more companies have adopted flexible policies that allow employees to work from home for part or all of the week. This shift has brought both benefits and challenges for workers and employers alike.

One of the most significant benefits of remote work is flexibility. Employees can often set their own schedules, which helps them balance their professional responsibilities with their personal commitments. Many people also save considerable time and money by avoiding a daily commute. This can lead to improved well-being, higher job satisfaction, and a better overall quality of life.

Remote work also offers advantages for employers. Companies can access a broader talent pool, since they are no longer limited to hiring people who live near a physical office. In addition, organizations may reduce costs related to office space, utilities, and equipment. Studies have shown that many remote employees maintain or even increase their productivity when given the right tools and support.

However, remote work is not without its difficulties. Some employees feel isolated and miss the social connections that come from working alongside colleagues. Communication can also become more challenging, as messages may be misunderstood without the context of tone and body language. Furthermore, the boundary between work and home can become blurred, making it harder for some people to disconnect at the end of the day.

To address these challenges, organizations should invest in clear communication practices and regular team check-ins. They should also encourage employees to set healthy boundaries and take time away from their screens. By taking these steps, companies can create a remote work environment that is productive, supportive, and sustainable for everyone involved.
```

Response:

```json
{
  "confidence": 0.8236,
  "content_id": "c_8470f2287473",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.8595,
  "style_score": 0.8116
}
```

---

## 2. Clearly human (casual) (240 words, a casual message, written by me)

```text
So are you going to continue to give me this closed off energy anytime we talk?
There is no room to have a conversation about this and moving forward from this. No more hope for the friendship that barely started? You accepted my apology but it feels like there is still some resentment. I'm trying because I did value to friendship that was forming and didn't want to shut the door on that the first misunderstanding that came up. But all in all it's all good. It feels like your pointing it as being just my fault without taking accountability for anything. You left me on read for four days after I commented on a show you told me to watch? You kept asking if I was going ti show up that Tuesday and didn't talk to me at all after the dinner was done at pressrolm and didn't even ask if I had gotten home safely which is in your character to ask because you had been previously doing it. So if I held all that against you and gave the same energy your giving. How would you feel?  It’s like you already had expectations for fri ships that I was never aware of given I had just started to know you so I already didn’t even stand a chance to meet up to it given I didn’t even know what your boundaries were. Anyways I come in peace
```

Response:

```json
{
  "confidence": 0.1434,
  "content_id": "c_876b56703f88",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.3742,
  "style_score": 0.0664
}
```

---

## 3. Plain human (289 words, plain writing about waiting on God, written by me, trimmed to fit)

```text
How do you handle the waiting season?

I asked myself this question late last year, and the Lord answered me:

Become a friend of the Holy Ghost and get to know Him deeply. Why? Because you will need this relationship for the rest of your life — even in marriage and in raising your children. Your relationship with God has to be strong because marriage is serious business, and raising children is not child’s play. You must be spiritually fortified.

You do not want to marry and stop journeying with God. You want a marriage that pushes you even closer to Him.

If marriage is still consuming your heart to the point where it controls your emotions, patience may still be doing its work. One sign that patience has matured you is when God becomes more important to you than marriage itself. Then marriage is no longer an idol in your heart.

That is the goal of the waiting season: growth.

The way to handle singleness well is to grow spiritually so you are not controlled by pressure, compromise, comparison, or panic because “everyone else is married.” You are in God’s timing. You cannot compare your timeline to someone else’s.

This season is a blessing.

Why? Because it gives you time to serve God without distraction, to grow closer to Him, and to let Him heal and refine the things in you that still need healing. Marriage exposes and amplifies what is already in the heart. Let God do the deep work in you now.

Do not let pressure, loneliness, or age push you into a relationship you have no business being in. Forever is a long time to regret a rushed decision, sis. It is not worth it.
```

Response:

```json
{
  "confidence": 0.4203,
  "content_id": "c_e0d743bb21e7",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.6578,
  "style_score": 0.3411
}
```

---

## 4. Formal human (299 words, a first-person essay passage, trimmed from 303 to 299 words so it fits the 300-word limit (removed "all over again" and "just"))

```text
My dorm room was the size of a matchbox, and had an AC that went thunk-thunk-thunk when it kicked on and only emitted a tiny wisp of cold air that made the room muggy and your hands sticky like flypaper. I was 19. Not a kid anymore but far from being a man. Men knew who they were. Me, not so much. I was watching via a small phone screen in my small dorm room as an entire city was broken and beaten and burned—buildings turned to charred nubs and wooden rubble, all over the shooting of an unarmed Black man, Michael Brown. It was triggering. I was back under that carport, imagining the muzzle flare that never happened and the closed casket that never was.

I had wanted to write about the Black experience in the South that night. Instead, the Word doc on my laptop remained blank and the crosshairs flickered off and on. I put my phone away so I could write, but my fingers hovered above my keyboard.

Writing for me had always been a release, and though I’d lost my love for it for a time, I’d recently rekindled it. But every time I tried to write about my experiences as a Black man, the same thing happened: I doubted myself, and wondered if I was Black enough to write about the Black experience. It never took me long to come up with an answer to this question, and that night, I did what I always did: I clung to my feeling of insecurity like an old raggedy ass blanket I was scared to let go of, all ’cause it was familiar, ’cause it made me feel safe. I closed my laptop, scooted my chair back, exhaled, and went back to watching Ferguson burn.
```

Response:

```json
{
  "confidence": 0.3977,
  "content_id": "c_9198eebbd319",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.6552,
  "style_score": 0.3119
}
```

---

## 5. Lightly-edited AI (154 words, product feedback on a game, AI-written and lightly edited)

```text
The game feels much more interactive now, and I love the vibrant, playful color choices! I played Pop the Kid and really liked how it feels like a board game. I also love the incorporation of sound and the option to toggle it off. The settings button is a great addition, with all the important information, including the rules, in one place. The rules are also much easier to understand now, thanks to the simpler language and explanations.

Overall, the game looks really good!

One suggestion that comes to mind is adding a universal leaderboard where players can see how they rank against others. It could also be fun to introduce some sort of reward system for winning, such as earning gems or coins that players can use to unlock new levels or other rewards. I think this could make the game even more engaging and give players an additional incentive to keep playing.
```

Response:

```json
{
  "confidence": 0.7027,
  "content_id": "c_4cf3a794abe6",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.8113,
  "style_score": 0.6665
}
```

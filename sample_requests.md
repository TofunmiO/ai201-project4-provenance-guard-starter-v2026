# Sample requests

The full texts behind the Sample Run in the README, so the README can stay short. Both were sent to `POST /submit` on the running service, and the responses below are the real ones.

How each request was sent (the JSON body is built from the text file so line breaks and apostrophes survive):

```bash
python -c 'import json,sys; print(json.dumps({"text": open(sys.argv[1]).read().strip(), "creator_id": "tofunmi"}))' text.txt \
  | curl -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d @-
```

---

## 1. Casual human message (240 words, written by me)

```text
So are you going to continue to give me this closed off energy anytime we talk?
There is no room to have a conversation about this and moving forward from this. No more hope for the friendship that barely started? You accepted my apology but it feels like there is still some resentment. I'm trying because I did value to friendship that was forming and didn't want to shut the door on that the first misunderstanding that came up. But all in all it's all good. It feels like your pointing it as being just my fault without taking accountability for anything. You left me on read for four days after I commented on a show you told me to watch? You kept asking if I was going ti show up that Tuesday and didn't talk to me at all after the dinner was done at pressrolm and didn't even ask if I had gotten home safely which is in your character to ask because you had been previously doing it. So if I held all that against you and gave the same energy your giving. How would you feel?  It’s like you already had expectations for fri ships that I was never aware of given I had just started to know you so I already didn’t even stand a chance to meet up to it given I didn’t even know what your boundaries were. Anyways I come in peace
```

Response:

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

---

## 2. AI-generated sample (289 words, written by Claude)

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
  "confidence": 0.5,
  "content_id": "c_4ba86a70a5b1",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.8595,
  "style_score": null
}
```

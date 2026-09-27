# Golf Coaching Business: product video

A 76-second, 1080p motion-graphics video for social media and the website. It's aimed at golf coaches and shows what the Golf Coaching Business CRM and AI tools do.

**Final file:** `golf-coaching-business-video.mp4` (1920×1080, 30fps, H.264 + AAC)

## Storyboard

| Time | Scene | Message |
|---|---|---|
| 0:00 | Hook | "You became a golf coach to help golfers play better. Not to chase admin." |
| 0:05 | The problem | "Sound familiar?": missed calls, unanswered DMs, unpaid packages, no-shows, spreadsheets |
| 0:10 | Brand reveal | Golf Coaching Business: the all-in-one business system & AI assistant built for golf coaches |
| 0:16 | **Hero feature** | **"Keep your business running smoothly whilst you're helping golfers"**: the AI books a new golfer mid-lesson (reply → booking → deposit → reminder) |
| 0:27 | AI assistant | Answers calls, replies to messages, books lessons, follows up, grows reviews, writes content |
| 0:34 | One inbox | WhatsApp, Instagram, Facebook, email, text in one place + mobile app |
| 0:39 | Online booking | Book & pay 24/7, automatic reminders, fewer no-shows |
| 0:45 | Pipeline | Turn one-off lessons into coaching programmes |
| 0:51 | Marketing | Websites, email/text campaigns, social planner, courses & community, done-for-you templates |
| 0:57 | Consolidation | Stop juggling apps → one system, one login, one monthly price |
| 1:03 | Benefits | Less admin. More coaching. Better work/life balance. 20+ years · PGA pros · ~1 hour a month |
| 1:09 | CTA | golfcoachingbusiness.com · Book a chat with our team today |

## Editing

- **Colours:** change the CSS variables at the top of `index.html` (`--gold`, `--fairway`, `--bg`, etc.).
- **Logo:** the flag-and-ball mark is a placeholder inline SVG. Swap in the real logo in the four `.mark` blocks.
- **Copy:** all text is plain HTML in `index.html`. Scene timings are the `data-start` / `data-end` attributes, and element timings are `data-in` (seconds from scene start).
- **Preview:** open `index.html` in Chrome. It plays in real time and loops.

## Re-rendering

Requirements: Node + Playwright (Chromium), ffmpeg with libx264, Python 3 + numpy.

```bash
python3 music.py soundtrack.wav             # original synthesised soundtrack (royalty-free)
node render.js silent.mp4                    # frame-accurate render, ~10 min
ffmpeg -i silent.mp4 -i soundtrack.wav -c:v copy -c:a aac -b:a 192k -shortest golf-coaching-business-video.mp4
node render.js --stills 5,20,40              # quick PNG stills for checking layout
```

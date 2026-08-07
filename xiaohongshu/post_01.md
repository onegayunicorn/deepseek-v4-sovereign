# Xiaohongshu Post 01 — Diary Style

## CES Strategy (brief)

Xiaohongshu's CES algorithm scores content on high-value interactions: **Follow (8 pts)**, **Save/Share (4 pts)**, **Comment (4 pts)**, **Like (1 pt)**. A post enters the initial 100–500 impression pool and must clear the Level-2 gate — **CTR ≥ 8% and engagement ≥ 5% within the first 2 hours** — to reach the Explore pool (10k+ impressions). Tactics applied here:

- **Title:** ≤20 characters, core keyword ("服务器"/self-host) inside the first 13 characters to capture search weight.
- **Body:** 300–600 characters, short sentences (10–15 words), 2–3 sentence paragraphs, emojis to break text and add personality.
- **Story:** Diary style — first-person, specific times and numbers, emotional peak, suspenseful closing question to trigger comments.
- **Golden 2 hours:** Post Tues/Thurs/Sat 19:00–20:00.
- **Tags:** 5–8 hashtags mixing broad, niche, and mandatory #AIContent / #AI生成内容 (platform AI-disclosure compliance).
- **CTA:** Suspense question that invites replies — comments are the heaviest signal after follows.

```json
{
  "title": "我把AI装进了自己的服务器",
  "content": "上周，我把用了两年的云端AI账号注销了。🎯\n不是一时冲动。\n是有一天我翻了它后台的导出文件，发现我所有的对话、文档、甚至深夜emo时打的字，都躺在别人的服务器上。\n那一刻我决定了：要么不用，要么自己养。\n于是我拉回了一整套DeepSeek架构的模型，跑在自己那台小服务器上。🤖\n没有云端，没有'你的数据将被用于训练'那行小字，没有每月自动扣款。\n速度反而更快。本地推理，局域网内基本秒回。\n最震撼的是昨晚。凌晨三点睡不着，我问它：'我该不该换工作？'\n它没哄我，给了三段很冷静、很扎心的分析，最后说：'你自己心里已经有答案了。'\n那一刻我确定了：这才是我要的AI。它只属于我。\n自己养AI这件事，真的回不去了。\n你们敢把自己的全部数据交给云端吗？评论区聊聊👇",
  "tags": ["#自托管AI", "#本地部署", "#AI隐私", "#独享AI", "#DeepSeek", "#SOVEREIGN", "#AI生成内容", "#AIContent"],
  "cover_prompt": "Xiaohongshu cover, 3:4 vertical, dark tech aesthetic (#0A0A10 background), a glowing cyan neural ring floating above a small home server rack in a cozy bedroom at night, mint green core dot, cyan circuit lines threading through the scene, cinematic rim lighting, high contrast, space at top for Chinese title overlay, no readable text in image",
  "best_time": "Tues/Thurs/Sat 19:00-20:00",
  "cta": "你们敢把自己的全部数据交给云端吗？评论区聊聊👇"
}
```

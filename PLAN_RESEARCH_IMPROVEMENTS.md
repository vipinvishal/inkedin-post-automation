# Plan: Improve research and post content (reduce “same” feeling)

## Why posts feel the same

1. **Same topic every run** – `TOPIC_FOCUS` is fixed (e.g. “AI, Agent AI, Gen AI…”), so the model and Google Search return similar clusters (OpenAI, Microsoft, Anthropic, agents).
2. **No recency window** – Prompt says “last few weeks/months,” so results stay broad and overlapping.
3. **No rotation** – Every run asks for the same type of content (headlines, company moves, tools, trends) with no sub-focus.
4. **No memory of last post** – We don’t tell the model “avoid what we already covered,” so it can repeat the same angles.

---

## Improvements (what we’ll do)

### 1. Stricter recency (research)

- In the research prompt, ask for **“news and announcements from the last 7 days”** (and pass the date range explicitly).
- Reduces overlap and pushes the model toward newer, more varied stories.

### 2. Rotating “research angle” (research)

- Each run gets a **sub-focus** that rotates by day of week (or run count), e.g.:
  - **Mon:** “New product launches, benchmarks, and model releases”
  - **Wed:** “Agent frameworks, multi-agent systems, and developer tools”
  - **Fri:** “Enterprise adoption, governance, and how companies are using AI”
- Same `TOPIC_FOCUS`, but each post has a **different angle**, so content varies.

### 3. Avoid last run’s theme (research)

- After each run, save a short **“theme”** (e.g. main headline or topic) to `data/last_research_theme.txt`.
- Next run: pass that into the research prompt as **“Do not focus on: [last theme]. Prefer different companies, products, or angles.”**
- Reduces back-to-back posts on the same story.

### 4. Lead with what’s new (content)

- In the content prompt: **“Lead with the most novel, surprising, or under-reported finding. Avoid generic intros like ‘The AI space is evolving.’”**
- So even if research overlaps a bit, the **post** takes a distinct angle.

### 5. Optional: multiple topic presets (config)

- Allow **rotating `TOPIC_FOCUS`** (e.g. from a list in config or .env) so some weeks focus on “AI coding tools,” others on “enterprise AI,” etc. Can be added later without changing the pipeline.

---

## Implementation summary

| Change              | Where           | What |
|---------------------|-----------------|------|
| Recency             | `config/prompts.py`, `src/research.py` | Add “last 7 days” and date range to research prompt. |
| Rotating angle      | `config/prompts.py`, `src/research.py` | Add `research_angle` argument; rotate by weekday in `run_pipeline`. |
| Avoid last theme    | `src/research.py`, `scripts/run_pipeline.py`, `data/` | Save theme after research; pass “avoid: last theme” into next research prompt. |
| Content: novel lead | `config/prompts.py` | Add line in content prompt: lead with novel/surprising finding, no generic intros. |

After this, each run should get **fresher** (7-day window), **narrower** (rotating angle), **less repetitive** (avoid last theme), and **sharper** (content leads with the novel angle).

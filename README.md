# LinkedIn Post Automation

Automated research → draft generation → email for approval → post to LinkedIn (every 2nd day, 11:00 AM IST). See [PLAN.md](PLAN.md) for full architecture and phases.

## Quick start (Phase 1)

1. **Clone and enter project**
   ```bash
   cd "LinkedIN post automation"
   ```

2. **Create virtualenv and install**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure**
   ```bash
   cp .env.example .env
   # Edit .env: set GEMINI_API_KEY and optionally TOPIC_FOCUS
   ```

4. **Run research + content (generate one post)**
   ```bash
   python scripts/run_pipeline.py
   ```
   This runs research (Gemini) → content generation (Gemini, using `samples/sample_posts.txt` and `config/STYLE_GUIDE.md`) and prints the draft post. Set `ENABLE_IMAGE_GENERATION=1` in `.env` to generate an image (saved under `output/`) for the post. **Note:** Image generation often requires a paid Gemini quota; the free tier may have 0 requests for image models. If you see a 429 quota error, leave this disabled (or upgrade your plan).

## Project layout

- `config/` – STYLE_GUIDE.md, prompts, env-based config
- `src/` – research, content, (later: email, LinkedIn, storage)
- `scripts/` – run_pipeline.py, run_approval_check.py, linkedin_oauth.py
- `samples/` – sample LinkedIn posts for tone/structure
- `deploy/` – VPS setup (Phase 4)

## Workflow

**Test locally first** → then push to **GitHub** → then deploy to **Hostinger VPS**. Keep secrets (`.env`) only on your machine and on the VPS; never commit them.

## Phases

| Phase | Status | Deliverable |
|-------|--------|-------------|
| 1 | ✅ | Research + content script; run → printed draft |
| 2 | ✅ | Email draft to Gmail; Approve/Re-write flow |
| 3 | ✅ | LinkedIn post on Approve (see [LINKEDIN_SETUP.md](LINKEDIN_SETUP.md)) |
| 4 | – | Scheduler + Hostinger VPS |
| 5 | – | Optional: scraping, logging, image |

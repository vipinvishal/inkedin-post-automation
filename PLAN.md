# LinkedIn Post Automation Agent – Detailed Plan

## Overview

An automated system that:
- **Researches** AI/Gen AI/Agent AI news (releases, comparisons, advancements)
- **Generates** engaging LinkedIn post drafts using Google Gemini
- **Sends** drafts to your Gmail for approval (Approve / Re-write)
- **Posts** to LinkedIn on your behalf every 2nd day at 11:00 AM IST when approved
- **Runs** 24/7 on Hostinger VPS

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HOSTINGER VPS (Cron / Systemd)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   SCHEDULER  │───▶│   RESEARCH   │───▶│   CONTENT    │───▶│   EMAIL    │ │
│  │ (every 2nd   │    │ (Gemini +    │    │   GEN        │    │   SEND     │ │
│  │  day 11AM)   │    │  web/scrape) │    │ (Gemini)     │    │ (Gmail)    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └─────┬──────┘ │
│                                                                     │        │
│                                                                     ▼        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   LINKEDIN   │◀───│  APPROVAL    │◀───│  INCOMING    │◀───│   EMAIL    │ │
│  │   POST API   │    │   PARSER     │    │   EMAIL      │    │   INBOX    │ │
│  │ (post/rewrite)   │ (Approve/     │    │ (IMAP)       │    │            │ │
│  └──────────────┘    │  Re-write)   │    └──────────────┘    └────────────┘ │
│                      └──────────────┘                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Components Breakdown

### 1.1 Scheduler
- **Role**: Trigger the pipeline every 2nd day at 11:00 AM IST.
- **Options**:
  - **Cron**: `0 11 */2 * *` (runs at 11:00 on odd days; for “every 2nd day” we’ll use a small script that checks “day of month % 2” or “days since start” to get exact 2-day cadence).
  - **Systemd timer** (alternative): more flexible, easier to log.
- **Action**: Run the main Python “run pipeline” script (research → generate → email).

### 1.2 Research Module
- **Input**: Topic focus (AI, Agent AI, Gen AI – releases, comparisons, advancements).
- **Output**: Structured “research notes” (headlines, summaries, links, comparisons).
- **Methods**:
  1. **Gemini**: Use Gemini with “search grounding” or “Google Search” if available in your API tier to pull recent info.
  2. **Web scraping**: Optional – scrape trusted sources (e.g. official blogs, TechCrunch, VentureBeat, AI lab blogs) via `requests` + `BeautifulSoup` or `playwright` for JS-heavy sites. Respect `robots.txt` and rate limits.
- **Caching**: Cache research by date/topic to avoid duplicate calls and stay within API limits.

### 1.3 Content Generation (Gemini)
- **Input**: Research notes + your “style” (from sample posts in `samples/sample_posts.txt` and `config/STYLE_GUIDE.md`).
- **Output**: One LinkedIn post (text only first; optional: suggest image later).
- **Prompt design**:
  - Load and include 2–4 sample posts from `samples/sample_posts.txt` so Gemini mimics tone, length, structure, line breaks, emojis (👇 ➡ ✔ 🔹), and hashtags.
  - Apply rules from `config/STYLE_GUIDE.md`: hook in first line (challenge assumption or reframe debate), short paragraphs, one clear takeaway/CTA, 5–8 relevant hashtags at the end.
  - Instruct: hook in first line, clear value (news/insight/comparison), CTA or memorable closing line, relevant hashtags (e.g. #AI #GenAI #MachineLearning #LLM #RAG #AIArchitecture).
- **Engagement hooks** (to maximize likes/comments/views):
  - Start with a bold claim, reframe, or “Stop X. Start Y.” style opener.
  - Use short paragraphs and line breaks for readability.
  - One clear CTA or takeaway at the end.
  - 5–8 hashtags at end; avoid over-tagging.

### 1.4 Email Sender (Gmail)
- **When**: After content is generated.
- **To**: Your Gmail.
- **Content**:
  - Subject: e.g. `[LinkedIn Draft] Approval needed – [date]`
  - Body: Full post text (clearly formatted).
  - **Two buttons/links**:
    - **Approve**: Link or reply keyword, e.g. `APPROVE-<draft_id>` (or a link that hits your server with a token).
    - **Re-write**: Link or reply keyword, e.g. `REWRITE-<draft_id>`.
- **Implementation**: Gmail API (preferred) or SMTP with app password. Store draft_id (and post text) in a small DB or file so the approval parser can resolve it.

### 1.5 Incoming Email (Approval Parser)
- **How**: Either **Gmail API** (read inbox/label) or **IMAP** (e.g. `imaplib`).
- **Trigger**: Polling (cron every 5–15 min) or, on VPS, a separate small daemon that checks for new emails with a specific label (e.g. `linkedin-drafts`).
- **Parse**:
  - If subject/body contains “Approve” / `APPROVE-<id>` (or click on Approve link): mark draft as approved → call **LinkedIn post**.
  - If “Re-write” / `REWRITE-<id>`: fetch draft by id, call **Content Generation** again (with “re-write” instruction), then **Email Sender** again with new draft and new draft_id.
- **Idempotency**: Once a draft_id is approved or re-written, ignore further replies for that id.

### 1.6 LinkedIn Posting
- **Options**:
  1. **LinkedIn API**: Official “Share” (UGC) API – requires OAuth 2.0 and a LinkedIn Developer App. Best for long-term, compliant automation.
  2. **Unofficial/browser automation**: e.g. Playwright/Puppeteer to log in and post. Higher risk (ToS, breakage), use only if you accept that.
- **Recommendation**: Use **LinkedIn API** with a refresh token stored securely on the VPS. Flow: one-time OAuth in browser → store refresh_token in env or secrets manager → server uses it to get access_token and post.

---

## 2. Tech Stack (Recommended)

| Layer           | Choice              | Notes                                      |
|----------------|---------------------|--------------------------------------------|
| Language       | Python 3.10+        | Good for APIs, cron, Gemini SDK            |
| LLM            | Google Gemini API   | As requested                               |
| Research       | Gemini + requests/BeautifulSoup or Playwright | Optional scrape for sources   |
| Email out      | Gmail API           | Or SMTP with app password                  |
| Email in       | Gmail API or IMAP   | Poll for Approve/Re-write                  |
| LinkedIn       | LinkedIn API (UGC)  | OAuth 2.0, share content                   |
| Scheduler      | Cron or systemd     | On Hostinger VPS                           |
| Storage        | SQLite or JSON files| Draft id, state, last run date             |
| Secrets        | .env (not in git)   | API keys, tokens, email credentials        |

---

## 3. Hostinger VPS Deployment

- **OS**: Ubuntu 22.04 LTS (typical for Hostinger VPS).
- **Setup**:
  1. Install Python 3.10+, pip, venv.
  2. Clone or copy your project; create venv and install dependencies.
  3. Configure `.env` with: `GEMINI_API_KEY`, Gmail OAuth credentials (or app password), LinkedIn app credentials, your email.
  4. **Cron**:
     - Pipeline: e.g. `0 11 */2 * *` plus a wrapper script that ensures “every 2nd day” logic if you need exact alternation.
     - Approval checker: e.g. `*/10 * * * *` (every 10 min) to process Approve/Re-write.
  5. Logs: redirect cron output to log files; optional rotation with `logrotate`.

---

## 4. Engagement & Hook Strategy (For Prompts)

So that posts hook people and increase engagement (likes, comments, views):

- **First line**: Strong hook – number, contrarian take, or question (e.g. “Most people still think AI is just chatbots. Here’s what changed in 2025.”).
- **Structure**: 1–2 short sentences per “paragraph”; 3–5 lines max per block.
- **Value**: One clear takeaway (release, comparison, or advancement).
- **CTA**: End with a question or “What would you add?” to encourage comments.
- **Hashtags**: 3–5 relevant (#AI #GenAI #Agents #MachineLearning #TechNews); avoid spammy quantity.
- **Length**: LinkedIn favors ~150–300 words for engagement; avoid walls of text.
- **Tone**: Match your samples (professional but approachable; use your samples in the Gemini prompt).

---

## 5. Security & Best Practices

- Never commit `.env` or tokens; use `.gitignore`.
- Store LinkedIn refresh_token and Gmail credentials securely; restrict file permissions (e.g. `chmod 600`).
- Prefer Gmail OAuth over storing password; use a dedicated Gmail account or label for this flow if possible.
- Rate-limit Gemini and LinkedIn calls to avoid bans.
- Respect LinkedIn’s Automation Policy: use official API and one account; no fake engagement.

---

## 6. How We’ll Proceed (Phases)

### Phase 1 – Foundation (Week 1)
1. **Project setup**: Repo structure, `requirements.txt`, `.env.example`, README.
2. **Config**: Load `GEMINI_API_KEY` and topic focus from env.
3. **Research module**: Gemini-only research (with optional “search” if available); output structured notes (JSON/dict).
4. **Content generation**: Gemini prompt that takes research + placeholder “sample posts”; output one post text. No email yet.

**Deliverable**: Script that, when run, prints a generated post from current “research”.

### Phase 2 – Email Flow (Week 2)
5. **Email sender**: Send draft to your Gmail with post body and two clear actions (Approve / Re-write). Use Gmail API or SMTP; include a unique `draft_id` in the email (link or reply keyword).
6. **Draft storage**: Save draft (id, text, created_at) in SQLite or JSON.
7. **Incoming email**: Poll Gmail (API or IMAP); parse Approve/Re-write; map to `draft_id`.
8. **Re-write path**: On Re-write, call content generation again (with “re-write” and previous post), save new draft, send new email.

**Deliverable**: End-to-end: generate → email → you reply “Re-write” → new draft emailed; “Approve” only logged (no LinkedIn yet).

### Phase 3 – LinkedIn Posting (Week 3)
9. **LinkedIn OAuth**: Script or doc for one-time OAuth; save refresh_token in `.env`.
10. **Post to LinkedIn**: On Approve, call LinkedIn Share API with the approved post text.
11. **Idempotency**: Mark draft as “posted” so the same approval email isn’t processed twice.

**Deliverable**: Approve email → post goes live on LinkedIn.

### Phase 4 – Scheduling & VPS (Week 4)
12. **Scheduler**: Cron (or systemd) for “every 2nd day at 11:00 AM IST” and separate cron for approval checker.
13. **Deployment doc**: Hostinger VPS setup (Ubuntu, Python, venv, cron, `.env`).
14. **Sample posts**: You provide 2–3 sample posts; we add them to the repo (or config) and wire into the Gemini prompt.

**Deliverable**: Full automation on VPS; no manual run required.

### Phase 5 – Polish (Optional)
15. **Web scraping**: Add optional scraper for 1–2 trusted AI news sources if Gemini search is limited.
16. **Logging & alerts**: Simple log file + optional email on failure.
17. **Image**: Optional – generate or pick an image for the post (Gemini image or stock); attach in LinkedIn post.

---

## 9. Adding a Picture to Posts (Feasibility)

**Yes, both are possible and feasible.**

| Question | Answer |
|----------|--------|
| **Can we add a picture?** | Yes. The pipeline can attach one image per post. |
| **Can we generate the picture?** | Yes. Using the **Gemini API** (e.g. `response_modalities: ['Text', 'Image']`) or **Imagen** we can generate an image from a short prompt (e.g. derived from the post topic or first line). The image is saved to a file (e.g. `output/draft_YYYYMMDD.png`) and passed to the email step and to LinkedIn. |
| **Can we post it on LinkedIn?** | Yes. The **LinkedIn API** supports posts with images: (1) Register an upload, (2) Upload the image binary to the returned URL, (3) Create the post with `shareMediaCategory: IMAGE` and the image URN. When we implement Phase 3 (LinkedIn posting), we will use this flow so the same generated image is posted with the text. |

**Flow with image:** Research → Content → **Optional: generate image from topic/post** → Email draft (body + image attachment or link) → On Approve → Post to LinkedIn (text + uploaded image).

---

## 7. What I Need From You Next

1. **Sample posts**: ✅ Done. Four sample posts are in `samples/sample_posts.txt`; style rules are in `config/STYLE_GUIDE.md`.
2. **Confirm**:
   - Gmail: address to receive drafts and to use for sending (OAuth or app password).
   - LinkedIn: are you okay creating a LinkedIn Developer App for API access?
3. **Hostinger**: Do you already have the VPS (Ubuntu)? If yes, we can tailor the deployment steps.

Once you confirm Gmail, LinkedIn app, and Hostinger, we can start **Phase 1** (project setup + research + content generation script) in code.

---

## 8. File Structure (Proposed)

```
linkedin-post-automation/
├── .env.example
├── .gitignore
├── README.md
├── PLAN.md                    # This file
├── requirements.txt
├── config/
│   └── prompts.py             # Gemini prompts
├── src/
│   ├── __init__.py
│   ├── research.py            # Research (Gemini + optional scrape)
│   ├── content.py             # Content generation (Gemini)
│   ├── image_gen.py           # Optional image for post (Gemini image model)
│   ├── email_sender.py        # Send draft to Gmail
│   ├── email_receiver.py      # Poll and parse Approve/Re-write
│   ├── linkedin.py            # LinkedIn API post
│   ├── storage.py             # Draft storage (SQLite/JSON)
│   └── pipeline.py            # Main: research → content → email
├── scripts/
│   ├── run_pipeline.py        # Entry for cron (generate + send email)
│   ├── run_approval_check.py  # Entry for cron (check inbox)
│   └── linkedin_oauth.py      # One-time OAuth helper
├── samples/                   # Your sample posts (for prompt)
│   └── sample_posts.txt
└── deploy/
    └── hostinger_setup.md     # VPS setup instructions
```

This plan gives you a clear path from “idea” to “fully automated, approval-based LinkedIn posts every 2nd day at 11:00 AM IST” with room to add scraping and images later.

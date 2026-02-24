# AI news RSS feeds (for research / agents)

High-signal feeds you can plug into Feedly, n8n, Zapier, or a future research step in this pipeline.

## Core AI news

| Source | Focus | RSS URL |
|--------|--------|--------|
| **WIRED AI** | Research + industry, ML, startups, chips | https://www.wired.com/feed/tag/ai/latest/rss |
| **ScienceDaily AI** | Academic + research | https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml |
| **The Guardian AI** | Policy + global AI | https://www.theguardian.com/technology/artificialintelligenceai/rss |
| **AIwire** | Enterprise AI, infrastructure, HPC | Check aiwire.com for their RSS feeds |
| **AI Weekly** | Curated best stories weekly; high signal | Check their site for RSS / newsletter |

## Possible use in this project

- **Option A:** Add an optional research step that fetches recent items from these feeds and passes headlines/links to the Gemini research prompt (e.g. "Also consider these recent headlines: …").
- **Option B:** Use in n8n/Zapier to trigger runs or enrich the topic focus.
- **Option C:** Manual: skim feeds when tuning `TOPIC_FOCUS` or angles in the pipeline.

No code changes required for now; this file is a reference.

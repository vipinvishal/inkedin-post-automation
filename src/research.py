"""Research module: Gemini with Google Search grounding → structured notes (dict/JSON)."""
import json
import re
from datetime import date, timedelta
from typing import Any

from google import genai
from google.genai import types

from config.prompts import RESEARCH_SYSTEM, RESEARCH_USER_TEMPLATE
from config.settings import get_gemini_api_key, get_topic_focus

# Rotating sub-focus by run (weekday % 3) so each post has a different angle
RESEARCH_ANGLES = [
    "New product launches, model releases, and benchmarks",
    "Agent frameworks, multi-agent systems, and developer tools",
    "Enterprise adoption, governance, and how companies are using AI",
]


def _extract_json(text: str) -> dict[str, Any]:
    """Try to parse JSON from model output; strip markdown code blocks if present."""
    raw = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        raw = m.group(1).strip()
    return json.loads(raw)


def run_research(
    topic_focus: str | None = None,
    reference_date: date | None = None,
    research_angle: str | None = None,
    avoid_theme: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """
    Run Gemini research with Google Search grounding (searches the web).
    Returns a dict with: headlines, summaries, links, comparisons_or_insights, date_context,
    company_moves, new_tools_and_agents, key_trends, how_to_use.
    - research_angle: optional sub-focus for this run (e.g. "Agent frameworks and developer tools").
    - avoid_theme: optional short text (e.g. last run's headline) so this run prefers different angles.
    Pass api_key to use a specific key (e.g. for fallback when another key hits 429).
    """
    topic_focus = topic_focus or get_topic_focus()
    reference_date = reference_date or date.today()
    ref_str = reference_date.isoformat()
    since_date = (reference_date - timedelta(days=7)).isoformat()
    recency_instruction = f"Focus on news and announcements from the last 7 days (since {since_date})."
    angle_instruction = f"This run's angle: {research_angle}." if research_angle else ""
    avoid_instruction = (
        f"Do not focus on: {avoid_theme}. Prefer different companies, products, or angles."
        if avoid_theme else ""
    )
    key = api_key or get_gemini_api_key()
    client = genai.Client(api_key=key)
    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(tools=[grounding_tool])

    user_prompt = RESEARCH_USER_TEMPLATE.format(
        topic_focus=topic_focus,
        reference_date=ref_str,
        recency_instruction=recency_instruction,
        angle_instruction=angle_instruction,
        avoid_instruction=avoid_instruction,
    )
    full_prompt = f"{RESEARCH_SYSTEM}\n\n---\n\n{user_prompt}"

    # Use a free-tier model; Google Search grounding may have quota limits
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
        config=config,
    )

    text = getattr(response, "text", None) or ""
    if not text:
        raise RuntimeError("Gemini returned empty response for research.")

    try:
        notes = _extract_json(text)
    except json.JSONDecodeError:
        # Retry: ask model to fix JSON (no search)
        fix_prompt = (
            "The following text is invalid JSON. Output only a corrected, valid JSON object "
            "with the same structure and content. Fix any unescaped quotes, trailing commas, or newlines inside strings.\n\n"
            + text[:15000]
        )
        fix_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=fix_prompt,
        )
        fix_text = getattr(fix_response, "text", None) or ""
        if not fix_text:
            raise RuntimeError("Research response was not valid JSON and fix attempt returned empty.")
        try:
            notes = _extract_json(fix_text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Research response was not valid JSON: {e}") from e

    expected = {
        "headlines",
        "summaries",
        "links",
        "contrarian_angle",
        "second_order_impact",
        "date_context",
        "company_moves",
        "new_tools_and_agents",
        "key_trends",
        "how_to_use",
        "viral_hook_angles",
    }
    string_keys = {"date_context", "contrarian_angle"}
    for k in expected:
        if k not in notes:
            notes[k] = "" if k in string_keys else []
    return notes

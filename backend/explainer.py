"""
explainer.py — WHY Layer / Explanation Generation for WHY.AI

Uses OpenAI GPT to generate human-readable explanations for each
recommendation. The LLM is ONLY used for explanation — the ranking
is already determined by the deterministic scoring engine.

Falls back to template-based explanations if the API key is missing
or the call fails, so the demo always works.
"""

import os
import json
from typing import List, Dict, Any

# Try to import openai; graceful fallback if not installed
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def _build_system_prompt() -> str:
    """System prompt that instructs GPT to act as an explainer, not a ranker."""
    return """You are the WHY.AI explanation engine. You receive a list of recommendations
that have ALREADY been ranked by a deterministic constraint scoring engine.

Your job is ONLY to explain the recommendations in plain language. 
You must NOT change the ranking order.

For each item, provide:
1. why_recommended: A 1-2 sentence explanation of why this item scored well given the user's constraints.
2. tradeoffs: A brief note on what the user gives up by choosing this (e.g., higher price, more time).
3. why_others_lower: A brief note on why items below this one scored lower.

Be concise, specific, and reference actual constraint values (budget, time, comfort/exploration preference).
Respond ONLY with valid JSON — an array of objects with fields: id, why_recommended, tradeoffs, why_others_lower."""


def _build_user_prompt(
    query: str,
    constraints: Dict[str, Any],
    items: List[Dict[str, Any]],
) -> str:
    """Build the user prompt with context about query, constraints, and scored items."""
    items_summary = []
    for item in items:
        items_summary.append({
            "id": item["id"],
            "name": item["name"],
            "price": item["price"],
            "time_minutes": item["time_minutes"],
            "score": item["score"],
            "comfort_score": item["comfort_score"],
            "exploration_score": item["exploration_score"],
            "is_discovery": item.get("is_discovery", False),
            "score_breakdown": item.get("score_breakdown", {}),
        })

    return f"""User query: "{query}"

Constraints:
- Budget: ₹{constraints.get('budget', 'N/A')}
- Time: {constraints.get('time', 'N/A')} minutes
- Comfort vs Exploration slider: {constraints.get('comfort_vs_exploration', 0.5)} (0=comfort, 1=exploration)
- Preset: {constraints.get('preset', 'none')}

Ranked items (already scored by deterministic engine):
{json.dumps(items_summary, indent=2)}

Generate explanations for each item. For discovery items, emphasize that they are shown to broaden horizons while still meeting constraints."""


def generate_explanations_llm(
    query: str,
    constraints: Dict[str, Any],
    items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Call OpenAI API to generate explanations for the scored items.
    Returns list of dicts with: id, why_recommended, tradeoffs, why_others_lower.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return []

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": _build_user_prompt(query, constraints, items)},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1]  # remove first line
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        explanations = json.loads(content)
        return explanations
    except Exception as e:
        print(f"[WHY.AI] OpenAI explanation failed: {e}")
        return []


def generate_explanations_template(
    constraints: Dict[str, Any],
    items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    FALLBACK: Generate template-based explanations when OpenAI is unavailable.
    These are less nuanced but still useful and constraint-aware.
    """
    budget = constraints.get("budget", 0)
    time_limit = constraints.get("time", 0)
    explanations = []

    for i, item in enumerate(items):
        budget_pct = round((1 - item["price"] / budget) * 100) if budget > 0 else 0
        time_pct = round((1 - item["time_minutes"] / time_limit) * 100) if time_limit > 0 else 0

        if item.get("is_discovery"):
            why = f"🔍 Discovery pick! '{item['name']}' meets your constraints but offers something different — it scores high on exploration ({item['exploration_score']})."
            tradeoffs = f"Exploration-focused pick: may not be your usual preference, but it stays within ₹{budget} and {time_limit} min."
        else:
            why = f"Scored {item['score']:.2f} — saves {budget_pct}% of your budget and uses only {item['time_minutes']}/{time_limit} min."
            tradeoffs = f"Costs ₹{item['price']} ({budget_pct}% saved) and takes {item['time_minutes']} min ({time_pct}% time saved)."

        why_others = ""
        if i == 0:
            why_others = "Top pick — best balance of your constraints."
        elif i < 3:
            why_others = "Strong option, slightly less optimal on one dimension."
        else:
            why_others = "Still meets your constraints but scored lower on weighted combination."

        explanations.append({
            "id": item["id"],
            "why_recommended": why,
            "tradeoffs": tradeoffs,
            "why_others_lower": why_others,
        })

    return explanations


def generate_explanations(
    query: str,
    constraints: Dict[str, Any],
    items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    MAIN ENTRY POINT
    ────────────────
    Try LLM explanations first; fall back to templates.
    Merges explanation data back into the item dicts.
    """
    # Try LLM first
    explanations = generate_explanations_llm(query, constraints, items)

    # Fall back to template
    if not explanations:
        explanations = generate_explanations_template(constraints, items)

    # Merge explanations into items by id
    expl_map = {e["id"]: e for e in explanations}
    for item in items:
        expl = expl_map.get(item["id"], {})
        item["why_recommended"] = expl.get("why_recommended", "Meets your constraints.")
        item["tradeoffs"] = expl.get("tradeoffs", "No significant tradeoffs identified.")
        item["why_others_lower"] = expl.get("why_others_lower", "")

    return items

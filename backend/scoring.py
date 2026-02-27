"""
scoring.py — Deterministic Constraint Scoring Engine for WHY.AI

This module implements a transparent, constraint-aware scoring system.
The LLM is NEVER used for ranking. All scoring is deterministic and auditable.

Concepts:
  - Hard constraints: Binary pass/fail. Items violating these are excluded.
  - Soft constraints: Numeric 0→1 satisfaction scores, weighted and combined.
  - Presets: Named weight profiles (student, saver, explorer) that shift priorities.
"""

from typing import List, Dict, Any, Optional

# ──────────────────────────────────────────────
# PRESET WEIGHT PROFILES
# Each preset adjusts how much weight is given to budget savings,
# time efficiency, and comfort-vs-exploration alignment.
# ──────────────────────────────────────────────
PRESET_WEIGHTS = {
    "student": {
        "budget_weight": 0.50,   # Students care most about saving money
        "time_weight": 0.30,     # Also time-constrained (classes)
        "alignment_weight": 0.20,
    },
    "saver": {
        "budget_weight": 0.60,   # Maximum budget sensitivity
        "time_weight": 0.15,
        "alignment_weight": 0.25,
    },
    "explorer": {
        "budget_weight": 0.15,   # Willing to spend more
        "time_weight": 0.15,     # Willing to spend more time
        "alignment_weight": 0.70, # Strongly favours exploration side
    },
    "default": {
        "budget_weight": 0.35,
        "time_weight": 0.30,
        "alignment_weight": 0.35,
    },
}


def apply_hard_constraints(
    items: List[Dict[str, Any]],
    budget: float,
    time: float,
) -> List[Dict[str, Any]]:
    """
    HARD CONSTRAINT FILTER
    ──────────────────────
    Remove any item that EXCEEDS the user's maximum budget or time.
    These are non-negotiable — if the user says ₹200 max, a ₹250 item
    is excluded no matter how good it is.

    Returns:
        List of items that pass all hard constraints.
    """
    passed = []
    for item in items:
        # Hard constraint 1: Price must not exceed budget
        if item["price"] > budget:
            continue
        # Hard constraint 2: Time must not exceed available time
        if item["time_minutes"] > time:
            continue
        passed.append(item)
    return passed


def compute_soft_scores(
    items: List[Dict[str, Any]],
    budget: float,
    time: float,
    comfort_vs_exploration: float,
    preset: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    SOFT CONSTRAINT SCORING
    ───────────────────────
    For each surviving item, compute a 0→1 composite score based on:

    1. Budget efficiency  — How much of the budget does this save?
       Formula: 1 - (price / budget)
       A ₹50 item on a ₹200 budget scores 0.75.

    2. Time efficiency    — How much time headroom does this leave?
       Formula: 1 - (time_minutes / time_limit)
       A 10-min meal with 30 min available scores 0.67.

    3. Alignment score    — How well does this match the user's
       comfort-vs-exploration preference?
       The slider goes 0 (pure comfort) → 1 (pure exploration).
       Formula: blend between comfort_score and exploration_score.

    These three are combined using PRESET WEIGHTS (or defaults).

    Args:
        items: Items that already passed hard constraints.
        budget: User's budget limit (₹).
        time: User's time limit (minutes).
        comfort_vs_exploration: 0 = full comfort, 1 = full exploration.
        preset: Optional preset name to load weight profile.

    Returns:
        Items enriched with `score` and `score_breakdown` fields, sorted descending.
    """
    weights = PRESET_WEIGHTS.get(preset, PRESET_WEIGHTS["default"])

    scored = []
    for item in items:
        # --- Individual dimension scores ---
        budget_score = 1.0 - (item["price"] / budget) if budget > 0 else 1.0
        time_score = 1.0 - (item["time_minutes"] / time) if time > 0 else 1.0

        # Alignment: interpolate between comfort and exploration
        # comfort_vs_exploration = 0 → use comfort_score
        # comfort_vs_exploration = 1 → use exploration_score
        alignment_score = (
            (1 - comfort_vs_exploration) * item["comfort_score"]
            + comfort_vs_exploration * item["exploration_score"]
        )

        # --- Weighted composite ---
        composite = (
            weights["budget_weight"] * budget_score
            + weights["time_weight"] * time_score
            + weights["alignment_weight"] * alignment_score
        )

        # Round for cleanliness
        composite = round(composite, 4)

        scored_item = {
            **item,
            "score": composite,
            "score_breakdown": {
                "budget_efficiency": round(budget_score, 4),
                "time_efficiency": round(time_score, 4),
                "alignment": round(alignment_score, 4),
                "weights_used": weights,
            },
        }
        scored.append(scored_item)

    # Sort descending by score
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def score_items(
    items: List[Dict[str, Any]],
    budget: float,
    time: float,
    comfort_vs_exploration: float,
    preset: Optional[str] = None,
) -> Dict[str, Any]:
    """
    MAIN ENTRY POINT
    ────────────────
    Run full scoring pipeline: hard filter → soft score → sort.

    Returns a dict with:
      - ranked: the scored & sorted items
      - filtered_out_count: how many items failed hard constraints
      - total_count: original item count
    """
    total = len(items)
    passed = apply_hard_constraints(items, budget, time)
    filtered_out = total - len(passed)
    ranked = compute_soft_scores(passed, budget, time, comfort_vs_exploration, preset)

    return {
        "ranked": ranked,
        "filtered_out_count": filtered_out,
        "total_count": total,
    }

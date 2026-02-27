"""
discovery.py — Anti-Filter-Bubble / Novelty Injection for WHY.AI

Injects 10–15% "discovery" recommendations from the pool of items that
passed hard constraints but didn't make the top-N ranked list.

These items broaden the user's horizon while still respecting their
hard constraints (budget, time). They are clearly flagged so the UI
can explain: "This is shown to broaden your discovery."
"""

import random
from typing import List, Dict, Any


def inject_discovery(
    ranked: List[Dict[str, Any]],
    all_passed: List[Dict[str, Any]],
    top_n: int = 5,
    discovery_ratio: float = 0.15,
) -> List[Dict[str, Any]]:
    """
    DISCOVERY INJECTION
    ───────────────────
    1. Take the top_n items from the ranked list.
    2. From the REMAINING items (those that passed hard constraints
       but didn't make top_n), randomly select ~discovery_ratio of top_n.
    3. Flag them with is_discovery = True.
    4. Insert them into the results at semi-random positions.

    Args:
        ranked:          Full scored & sorted list (post hard + soft).
        all_passed:      All items that passed hard constraints (same as ranked but unsorted).
        top_n:           How many top results to show.
        discovery_ratio: Fraction of top_n to inject as discovery (0.10 – 0.15).

    Returns:
        Final results list with discovery items injected and flagged.
    """
    # Take the top N items
    top_items = ranked[:top_n]
    top_ids = {item["id"] for item in top_items}

    # Mark top items as non-discovery
    for item in top_items:
        item["is_discovery"] = False

    # Candidate pool: items that passed hard constraints but aren't in top N
    discovery_pool = [item for item in ranked if item["id"] not in top_ids]

    if not discovery_pool:
        return top_items

    # How many discovery items to inject (10–15% of top_n, at least 1 if pool exists)
    num_discovery = max(1, round(top_n * discovery_ratio))
    num_discovery = min(num_discovery, len(discovery_pool))

    # Randomly pick from the pool
    discovery_picks = random.sample(discovery_pool, num_discovery)

    # Flag each discovery item
    for item in discovery_picks:
        item["is_discovery"] = True
        item["discovery_reason"] = "This is shown to broaden your discovery. It satisfies your constraints but explores a different direction."

    # Insert discovery items at varied positions (not all at the end)
    results = list(top_items)
    for i, pick in enumerate(discovery_picks):
        # Insert after position 2, 4, etc. to interleave naturally
        insert_pos = min(2 + i * 2, len(results))
        results.insert(insert_pos, pick)

    return results

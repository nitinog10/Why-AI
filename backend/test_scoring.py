"""
test_scoring.py — Unit tests for the WHY.AI scoring engine and discovery logic.

Run with: python -m pytest test_scoring.py -v
"""

import json
import os
from scoring import apply_hard_constraints, compute_soft_scores, score_items
from discovery import inject_discovery


# ──────────────────────────────────────────────
# SAMPLE DATA FOR TESTING
# ──────────────────────────────────────────────
SAMPLE_ITEMS = [
    {
        "id": "t1", "name": "Cheap Quick Meal", "category": "meal",
        "price": 50, "time_minutes": 10,
        "comfort_score": 0.8, "exploration_score": 0.2,
        "tags": ["budget"], "description": "A cheap, quick meal."
    },
    {
        "id": "t2", "name": "Expensive Slow Experience", "category": "experience",
        "price": 500, "time_minutes": 120,
        "comfort_score": 0.3, "exploration_score": 0.9,
        "tags": ["premium"], "description": "Costly and time-consuming."
    },
    {
        "id": "t3", "name": "Mid-Range Comfort", "category": "meal",
        "price": 200, "time_minutes": 30,
        "comfort_score": 0.9, "exploration_score": 0.3,
        "tags": ["comfort"], "description": "Mid-range comfortable option."
    },
    {
        "id": "t4", "name": "Budget Explorer", "category": "experience",
        "price": 80, "time_minutes": 45,
        "comfort_score": 0.4, "exploration_score": 0.85,
        "tags": ["explore"], "description": "Cheap but adventurous."
    },
    {
        "id": "t5", "name": "Premium Comfort", "category": "meal",
        "price": 350, "time_minutes": 40,
        "comfort_score": 0.95, "exploration_score": 0.1,
        "tags": ["luxury"], "description": "Premium comfort option."
    },
]


# ──────────────────────────────────────────────
# TEST: HARD CONSTRAINTS
# ──────────────────────────────────────────────
def test_hard_constraint_budget_filter():
    """Items over budget must be excluded."""
    result = apply_hard_constraints(SAMPLE_ITEMS, budget=100, time=120)
    ids = [item["id"] for item in result]
    assert "t1" in ids, "Cheap item should pass"
    assert "t4" in ids, "Budget explorer should pass"
    assert "t2" not in ids, "Expensive item should be filtered out"
    assert "t3" not in ids, "₹200 item should fail ₹100 budget"
    assert "t5" not in ids, "₹350 item should fail ₹100 budget"


def test_hard_constraint_time_filter():
    """Items exceeding time limit must be excluded."""
    result = apply_hard_constraints(SAMPLE_ITEMS, budget=10000, time=30)
    ids = [item["id"] for item in result]
    assert "t1" in ids, "10-min item should pass 30-min limit"
    assert "t3" in ids, "30-min item should pass 30-min limit"
    assert "t2" not in ids, "120-min item should fail 30-min limit"
    assert "t4" not in ids, "45-min item should fail 30-min limit"
    assert "t5" not in ids, "40-min item should fail 30-min limit"


def test_hard_constraint_both():
    """Budget AND time must both be satisfied."""
    result = apply_hard_constraints(SAMPLE_ITEMS, budget=100, time=15)
    ids = [item["id"] for item in result]
    assert ids == ["t1"], "Only cheap+quick item should survive both constraints"


# ──────────────────────────────────────────────
# TEST: SOFT SCORING
# ──────────────────────────────────────────────
def test_soft_scoring_deterministic():
    """Same inputs must produce same scores (deterministic)."""
    passed = apply_hard_constraints(SAMPLE_ITEMS, budget=500, time=120)
    result1 = compute_soft_scores(passed, 500, 120, 0.5)
    result2 = compute_soft_scores(passed, 500, 120, 0.5)
    scores1 = [item["score"] for item in result1]
    scores2 = [item["score"] for item in result2]
    assert scores1 == scores2, "Scoring must be deterministic"


def test_soft_scoring_sorted_descending():
    """Results must be sorted by score, highest first."""
    passed = apply_hard_constraints(SAMPLE_ITEMS, budget=500, time=120)
    result = compute_soft_scores(passed, 500, 120, 0.5)
    scores = [item["score"] for item in result]
    assert scores == sorted(scores, reverse=True), "Should be sorted descending"


def test_comfort_preference_favors_comfort():
    """With comfort_vs_exploration = 0 (pure comfort), high-comfort items score higher."""
    passed = apply_hard_constraints(SAMPLE_ITEMS, budget=500, time=120)
    result = compute_soft_scores(passed, 500, 120, comfort_vs_exploration=0.0)
    # t1 (comfort 0.8) and t3 (comfort 0.9) should rank higher than t2 (comfort 0.3)
    ids = [item["id"] for item in result]
    t1_idx = ids.index("t1")
    t2_idx = ids.index("t2")
    assert t1_idx < t2_idx, "Comfort items should rank higher with comfort=0"


def test_exploration_preference_favors_exploration():
    """With comfort_vs_exploration = 1 (pure exploration), high-exploration items score higher."""
    passed = apply_hard_constraints(SAMPLE_ITEMS, budget=500, time=120)
    result = compute_soft_scores(passed, 500, 120, comfort_vs_exploration=1.0)
    ids = [item["id"] for item in result]
    t4_idx = ids.index("t4")
    t5_idx = ids.index("t5")
    assert t4_idx < t5_idx, "Explorer items should rank higher with exploration=1"


# ──────────────────────────────────────────────
# TEST: PRESETS
# ──────────────────────────────────────────────
def test_student_preset_favors_budget():
    """Student preset should rank budget-friendly items higher."""
    passed = apply_hard_constraints(SAMPLE_ITEMS, budget=500, time=120)
    result = compute_soft_scores(passed, 500, 120, 0.5, preset="student")
    # t1 (₹50) should be in top 2 due to budget weight
    ids = [item["id"] for item in result]
    assert ids.index("t1") <= 1, "Cheapest item should rank top-2 with student preset"


# ──────────────────────────────────────────────
# TEST: DISCOVERY INJECTION
# ──────────────────────────────────────────────
def test_discovery_injection_adds_items():
    """Discovery should inject at least 1 flagged item."""
    passed = apply_hard_constraints(SAMPLE_ITEMS, budget=500, time=120)
    ranked = compute_soft_scores(passed, 500, 120, 0.5)
    results = inject_discovery(ranked, ranked, top_n=3, discovery_ratio=0.15)
    discovery_items = [r for r in results if r.get("is_discovery")]
    assert len(discovery_items) >= 1, "Should have at least 1 discovery item"


def test_discovery_items_flagged():
    """All discovery items must have is_discovery=True and a reason."""
    passed = apply_hard_constraints(SAMPLE_ITEMS, budget=500, time=120)
    ranked = compute_soft_scores(passed, 500, 120, 0.5)
    results = inject_discovery(ranked, ranked, top_n=3, discovery_ratio=0.15)
    for r in results:
        if r.get("is_discovery"):
            assert "discovery_reason" in r, "Discovery items must have a reason"


def test_discovery_does_not_duplicate():
    """Discovery items should not duplicate items already in top-N."""
    passed = apply_hard_constraints(SAMPLE_ITEMS, budget=500, time=120)
    ranked = compute_soft_scores(passed, 500, 120, 0.5)
    results = inject_discovery(ranked, ranked, top_n=3, discovery_ratio=0.15)
    ids = [r["id"] for r in results]
    assert len(ids) == len(set(ids)), "No duplicate IDs in results"


# ──────────────────────────────────────────────
# TEST: FULL PIPELINE
# ──────────────────────────────────────────────
def test_score_items_pipeline():
    """Full pipeline: score_items returns correct structure."""
    result = score_items(SAMPLE_ITEMS, budget=300, time=60, comfort_vs_exploration=0.5)
    assert "ranked" in result
    assert "filtered_out_count" in result
    assert "total_count" in result
    assert result["total_count"] == 5
    assert result["filtered_out_count"] >= 1  # ₹500 item should be filtered
    for item in result["ranked"]:
        assert "score" in item
        assert "score_breakdown" in item


def test_real_data_loads():
    """Ensure all 3 domain data files are valid JSON."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    for domain in ["campus", "retail", "travel"]:
        filepath = os.path.join(data_dir, f"{domain}.json")
        assert os.path.exists(filepath), f"{domain}.json should exist"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
        assert len(data) >= 10, f"{domain} should have at least 10 items"
        for item in data:
            assert "id" in item
            assert "price" in item
            assert "time_minutes" in item

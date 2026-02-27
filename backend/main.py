"""
main.py — FastAPI Backend for WHY.AI

Single endpoint: POST /recommend
Orchestrates: load data → score → inject discovery → explain → respond.
"""

import json
import os
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from scoring import score_items
from discovery import inject_discovery
from explainer import generate_explanations

# ──────────────────────────────────────────────
# APP SETUP
# ──────────────────────────────────────────────
app = FastAPI(
    title="WHY.AI — Constraint-Aware Consumer Intelligence",
    version="1.0.0",
    description="Explainable, constraint-aware recommendation engine.",
)

# CORS — allow the React frontend (dev server on port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_domain_data(domain: str) -> List[Dict[str, Any]]:
    """Load mock data for the given domain (campus, retail, travel)."""
    filepath = os.path.join(DATA_DIR, f"{domain}.json")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=400, detail=f"Unknown domain: {domain}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.loads(f.read())


# ──────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ──────────────────────────────────────────────
class Constraints(BaseModel):
    budget: float = Field(500, description="Maximum budget in ₹")
    time: float = Field(60, description="Maximum time in minutes")
    comfort_vs_exploration: float = Field(
        0.5, ge=0, le=1,
        description="0 = pure comfort, 1 = pure exploration"
    )

class RecommendRequest(BaseModel):
    query: str = Field("", description="Natural language user intent")
    constraints: Constraints = Field(default_factory=Constraints)
    domain: str = Field("campus", description="Domain: campus, retail, or travel")
    preset: Optional[str] = Field(None, description="Preset: student, saver, explorer, or null")

class ScoreBreakdown(BaseModel):
    budget_efficiency: float
    time_efficiency: float
    alignment: float

class RecommendationItem(BaseModel):
    id: str
    name: str
    category: str
    price: float
    time_minutes: float
    comfort_score: float
    exploration_score: float
    tags: List[str]
    description: str
    score: float
    score_breakdown: Dict[str, Any]
    is_discovery: bool
    discovery_reason: Optional[str] = None
    why_recommended: str
    tradeoffs: str
    why_others_lower: str

class RecommendResponse(BaseModel):
    recommendations: List[RecommendationItem]
    total_items: int
    filtered_out: int
    domain: str
    constraints_used: Constraints
    preset_used: Optional[str]


# ──────────────────────────────────────────────
# MAIN ENDPOINT
# ──────────────────────────────────────────────
@app.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    """
    RECOMMENDATION PIPELINE
    ───────────────────────
    1. Load domain data
    2. Apply hard constraints (filter)
    3. Apply soft scoring (rank)
    4. Inject discovery items (anti-filter-bubble)
    5. Generate explanations (LLM or template fallback)
    6. Return structured response
    """
    # Step 1: Load data
    items = load_domain_data(request.domain)

    # Step 2 + 3: Score (hard filter + soft rank)
    scoring_result = score_items(
        items=items,
        budget=request.constraints.budget,
        time=request.constraints.time,
        comfort_vs_exploration=request.constraints.comfort_vs_exploration,
        preset=request.preset,
    )

    ranked = scoring_result["ranked"]

    # Step 4: Inject discovery items
    results = inject_discovery(
        ranked=ranked,
        all_passed=ranked,
        top_n=5,
        discovery_ratio=0.15,
    )

    # Step 5: Generate explanations
    constraints_dict = {
        "budget": request.constraints.budget,
        "time": request.constraints.time,
        "comfort_vs_exploration": request.constraints.comfort_vs_exploration,
        "preset": request.preset,
    }
    results = generate_explanations(
        query=request.query,
        constraints=constraints_dict,
        items=results,
    )

    # Step 6: Build response
    return RecommendResponse(
        recommendations=results,
        total_items=scoring_result["total_count"],
        filtered_out=scoring_result["filtered_out_count"],
        domain=request.domain,
        constraints_used=request.constraints,
        preset_used=request.preset,
    )


@app.get("/")
async def root():
    return {
        "name": "WHY.AI API",
        "version": "1.0.0",
        "endpoints": {
            "POST /recommend": "Get constraint-aware, explainable recommendations",
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}

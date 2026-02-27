# WHY.AI — Constraint-Aware Consumer Intelligence Platform

An explainable, constraint-aware AI system that helps users make consumer decisions by respecting real-world constraints (budget, time, comfort/exploration) and clearly explains **WHY** each recommendation is made.

## ✨ Key Features

- **Deterministic Scoring Engine** — No black-box AI. Budget, time, and preference constraints are scored with transparent, auditable math.
- **Hard + Soft Constraints** — Hard constraints (budget/time limits) filter items out. Soft constraints (preference alignment) rank what remains.
- **Explainable WHY Layer** — Every card shows "Why recommended", "Tradeoffs", and "Why others ranked lower".
- **Anti-Filter-Bubble** — 10–15% discovery items are injected to broaden recommendations while respecting constraints.
- **Multi-Domain** — Same engine works across Campus (canteen/events), Retail (shopping), and Travel (layover activities).
- **Preset Modes** — Student, Saver, Explorer presets adjust scoring weights.
- **LLM for Explanation Only** — OpenAI GPT generates natural-language explanations but never decides rankings.

## 🏗️ Architecture

```
┌──────────────┐       POST /recommend       ┌──────────────────┐
│   React UI   │  ──────────────────────────▸ │   FastAPI Server │
│  (Vite)      │  ◂────────────────────────── │                  │
│  :5173       │     JSON response            │   :8000          │
└──────────────┘                              └──────────────────┘
                                                      │
                                              ┌───────┼────────┐
                                              │       │        │
                                         scoring.py  discovery.py  explainer.py
                                              │                     │
                                         deterministic        OpenAI GPT
                                         constraint           (explanation
                                         engine               only)
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **Node.js 18+**
- (Optional) **OpenAI API key** for AI-generated explanations

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

**Set your OpenAI API key** (optional — template explanations work without it):

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-your-key-here"

# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"
```

**Start the server:**

```bash
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Open the App

Navigate to **http://localhost:5173** in your browser.

## 🧪 Run Tests

```bash
cd backend
python -m pytest test_scoring.py -v
```

## 📁 Project Structure

```
WhyAI/
├── backend/
│   ├── main.py              # FastAPI app + /recommend endpoint
│   ├── scoring.py           # Deterministic constraint scoring engine
│   ├── discovery.py         # Anti-filter-bubble novelty injection
│   ├── explainer.py         # OpenAI WHY explanations + template fallback
│   ├── test_scoring.py      # Unit tests
│   ├── requirements.txt     # Python dependencies
│   └── data/
│       ├── campus.json      # Campus canteen & events (12 items)
│       ├── retail.json      # Retail shopping items (12 items)
│       └── travel.json      # Travel/layover places (12 items)
└── frontend/
    ├── src/
    │   ├── App.jsx           # Root component
    │   ├── api.js            # Backend API client
    │   ├── index.css         # Design system (dark theme)
    │   └── components/
    │       ├── ConstraintPanel.jsx      # Sliders, presets, query input
    │       ├── DomainSelector.jsx       # Domain tab bar
    │       └── RecommendationCard.jsx   # Card with WHY explanations
    ├── package.json
    └── vite.config.js
```

## 🧠 How Scoring Works

1. **Hard Filter** — Remove items exceeding budget or time limit.
2. **Soft Score** — For each surviving item:
   - Budget efficiency: `1 - (price / budget)`
   - Time efficiency: `1 - (time / time_limit)`
   - Alignment: blend of `comfort_score` & `exploration_score` based on slider
3. **Weighted Sum** — Combine using preset weights (or defaults).
4. **Discovery** — Inject 10-15% items that passed hard constraints but didn't make top-5.
5. **Explain** — Send to GPT for natural-language explanations (or use templates as fallback).

## ⚖️ Principles

- NO black-box recommendations
- NO engagement optimization
- ALWAYS respect user constraints
- AI acts as a responsible assistant
- Every recommendation is explainable
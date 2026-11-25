# SmartPack – HealthFit & AI Guidance (Member 3)

Backend for checking packaged-food suitability against a user's optional health profile.
Results come from **validated rules + real product data**. AI only *explains* results and
can only cite sources from `app/rules/sources.py`.

## Run
```bash
cd healthfit-ai
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add GEMINI_API_KEY (never commit .env)
uvicorn app.main:app --reload
```
Docs: http://127.0.0.1:8000/docs

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | /api/health/profile | Save optional profile |
| GET/DELETE | /api/health/profile/{user_id} | Read / delete profile (privacy) |
| POST | /api/health/assess | Product suitability |
| POST | /api/assistant/ask | Evidence-grounded answer (EN/TA) |

### Assess request (agree final format with Members 1 & 2)

**Option A: send the profile inline (nothing is stored)**
```json
{
  "language": "en",
  "profile": {
    "user_id": "test1",
    "conditions": ["diabetes", "gluten_restriction"],
    "allergies": ["peanut"],
    "language": "en"
  },
  "product": {
    "name": "Cream biscuit",
    "ingredients": ["Refined wheat flour", "Sugar", "Milk solids"],
    "allergens_declared": ["milk", "gluten"],
    "may_contain": [],
    "nutrition": {"sugar_g": 28, "carbohydrates_g": 70, "sodium_mg": 300}
  }
}
```

**Option B: use a saved profile.** First call `POST /api/health/profile`, then send `"user_id"` instead of `"profile"`.

All nutrition values are **per 100 g**; use `null` when unreadable.

### Results
`Better fit` · `Use caution` · `Avoid due to a confirmed incompatibility` · `Insufficient information`
- Declared allergen or listed ingredient match → **Avoid** (confirmed).
- "May contain" → **Use caution** (labelled uncertain).
- Missing data → **Insufficient information**.

## Before release (important)
1. Review thresholds in `app/rules/thresholds.py`. The carbohydrate cut-off is a **placeholder** (`needs_review`).
2. Open every URL in `app/rules/sources.py` and confirm it works.
3. Have Tamil text reviewed by a native speaker.
4. Never claim a product is medically safe; keep the disclaimer visible in the UI.
